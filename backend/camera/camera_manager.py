"""
EduSense AI 360 - Camera Manager
================================

Owns the external USB webcam: enumeration, initialisation, a dedicated capture
thread that keeps the latest frame available, resolution/FPS negotiation, live FPS
measurement, status reporting, and bounded-retry reconnection on disconnect
(Functional Requirements Part 1B §1; Architecture Part 3 §5).

Concurrency model
-----------------
A background capture thread reads frames as fast as the device delivers them and
pushes the newest into a :class:`FrameBuffer` (latest-wins). The analysis side pulls
``read()`` at its own cadence, so a slow consumer never stalls capture and the UI
stays responsive.

OpenCV is imported lazily, so this module is importable without the CV stack; if
OpenCV is absent at runtime, the manager reports a clear error state instead of
crashing.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Optional

from config.config_manager import ConfigManager
from backend.camera.frame_buffer import FrameBuffer
from backend.contracts.models import CameraStatus
from core.exceptions import CameraError
from core.error_handler import handle
from core.logger import get_logger
from utilities.helpers import MovingAverage

log = get_logger("camera")

StatusCallback = Callable[[CameraStatus, str], None]


class CameraManager:
    """Manages the webcam capture lifecycle on a background thread."""

    def __init__(self, config: ConfigManager, on_status: Optional[StatusCallback] = None) -> None:
        self._config = config
        self._on_status = on_status

        cam = config.section("camera")
        self._device_index: int = int(cam.get("device_index", 0))
        self._width: int = int(cam.get("width", 1280))
        self._height: int = int(cam.get("height", 720))
        self._target_fps: int = int(cam.get("fps", 30))
        self._max_retries: int = int(cam.get("reconnect_max_retries", 5))
        self._backoff: float = float(cam.get("reconnect_backoff_seconds", 1.5))
        self._failed_read_limit: int = int(cam.get("failed_read_limit", 30))

        self._buffer = FrameBuffer()
        self._capture: Any = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._status: CameraStatus = CameraStatus.DISCONNECTED
        self._fps_meter = MovingAverage(30)
        self._actual_resolution: tuple[int, int] = (0, 0)
        self._lock = threading.Lock()

    # -- status -------------------------------------------------------------
    @property
    def status(self) -> CameraStatus:
        with self._lock:
            return self._status

    def _set_status(self, status: CameraStatus, detail: str = "") -> None:
        with self._lock:
            self._status = status
        log.info("Camera status: %s%s", status.value, f" ({detail})" if detail else "")
        if self._on_status is not None:
            try:
                self._on_status(status, detail)
            except Exception as exc:  # never let a UI callback break capture
                handle(exc, context="camera status callback", category="camera")

    @property
    def fps(self) -> float:
        return round(self._fps_meter.value, 1)

    @property
    def resolution(self) -> tuple[int, int]:
        return self._actual_resolution

    @property
    def device_index(self) -> int:
        return self._device_index

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # -- enumeration --------------------------------------------------------
    def list_devices(self, max_probe: int = 8) -> list[int]:
        """Return indices of available camera devices by probing.

        Returns an empty list if OpenCV is unavailable.
        """
        try:
            import cv2
        except ImportError:
            log.warning("OpenCV not available; cannot enumerate cameras.")
            return []

        available: list[int] = []
        for index in range(max_probe):
            cap = cv2.VideoCapture(index)
            try:
                if cap is not None and cap.isOpened():
                    available.append(index)
            finally:
                if cap is not None:
                    cap.release()
        log.info("Enumerated camera devices: %s", available or "none")
        return available

    # -- lifecycle ----------------------------------------------------------
    def start(self, device_index: Optional[int] = None) -> bool:
        """Open the camera and begin the capture thread. Returns success."""
        if self.is_running:
            log.debug("Camera already running; ignoring start().")
            return True
        if device_index is not None:
            self._device_index = int(device_index)

        self._set_status(CameraStatus.INITIALISING, f"device {self._device_index}")
        try:
            self._open_device()
        except CameraError as exc:
            self._set_status(CameraStatus.ERROR, exc.message)
            handle(exc, context="camera start", category="camera")
            return False

        self._stop_event.clear()
        self._fps_meter.reset()
        self._buffer.clear()
        self._thread = threading.Thread(target=self._capture_loop, name="camera-capture", daemon=True)
        self._thread.start()
        self._set_status(CameraStatus.STREAMING)
        return True

    def stop(self) -> None:
        """Stop capture and release the device cleanly."""
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self._thread = None
        self._release_device()
        self._buffer.clear()
        self._set_status(CameraStatus.DISCONNECTED)

    def switch_camera(self, device_index: int) -> bool:
        """Switch to a different device at runtime."""
        log.info("Switching camera to device %s", device_index)
        self.stop()
        return self.start(device_index)

    # -- frame access -------------------------------------------------------
    def read(self) -> Optional[Any]:
        """Return the latest captured frame, or None if none is available yet."""
        return self._buffer.get_latest_frame()

    @property
    def dropped_frames(self) -> int:
        return self._buffer.dropped

    # -- device helpers -----------------------------------------------------
    def _open_device(self) -> None:
        try:
            import cv2
        except ImportError as exc:
            raise CameraError(
                "OpenCV is not installed; cannot open the camera.",
                user_message="The camera library is missing. Please install dependencies.",
                recoverable=False,
            ) from exc

        capture = cv2.VideoCapture(self._device_index)
        if not capture or not capture.isOpened():
            if capture is not None:
                capture.release()
            raise CameraError(f"Could not open camera device {self._device_index}.")

        # Request configured properties; the device may negotiate the nearest values.
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        capture.set(cv2.CAP_PROP_FPS, self._target_fps)

        actual_w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or self._width
        actual_h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or self._height
        self._actual_resolution = (actual_w, actual_h)
        self._capture = capture
        log.info("Camera opened: device %s @ %dx%d", self._device_index, actual_w, actual_h)

    def _release_device(self) -> None:
        if self._capture is not None:
            try:
                self._capture.release()
            except Exception as exc:  # noqa: BLE001
                handle(exc, context="camera release", category="camera")
            self._capture = None

    # -- capture loop -------------------------------------------------------
    def _capture_loop(self) -> None:
        """Continuously read frames and publish the latest to the buffer."""
        consecutive_failures = 0
        last_time = time.time()

        while not self._stop_event.is_set():
            capture = self._capture
            if capture is None:
                break

            ok, frame = False, None
            try:
                ok, frame = capture.read()
            except Exception as exc:  # noqa: BLE001 - device read may raise
                handle(exc, context="frame read", category="camera")
                ok = False

            if not ok or frame is None:
                consecutive_failures += 1
                if consecutive_failures >= self._failed_read_limit:
                    log.warning("Camera read failed %d times; attempting recovery.", consecutive_failures)
                    if not self._attempt_reconnect():
                        self._set_status(CameraStatus.ERROR, "camera lost")
                        return
                    consecutive_failures = 0
                else:
                    time.sleep(0.01)
                continue

            consecutive_failures = 0
            self._buffer.put(frame)

            now = time.time()
            dt = now - last_time
            last_time = now
            if dt > 0:
                self._fps_meter.update(1.0 / dt)

    # -- reconnection -------------------------------------------------------
    def _attempt_reconnect(self) -> bool:
        """Bounded-retry reconnection with backoff. Returns True on success."""
        self._set_status(CameraStatus.RECONNECTING, f"device {self._device_index}")
        self._release_device()

        for attempt in range(1, self._max_retries + 1):
            if self._stop_event.is_set():
                return False
            wait = self._backoff * attempt
            log.info("Reconnect attempt %d/%d in %.1fs", attempt, self._max_retries, wait)
            time.sleep(wait)
            try:
                self._open_device()
                self._set_status(CameraStatus.STREAMING, "reconnected")
                return True
            except CameraError:
                continue
        log.error("Camera reconnection failed after %d attempts.", self._max_retries)
        return False
