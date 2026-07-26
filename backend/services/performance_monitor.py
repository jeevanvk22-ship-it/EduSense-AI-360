"""
EduSense AI 360 - Performance Monitor
=====================================

Measures runtime performance against the configured budgets (Architecture Part 3
§21): effective analysis FPS, mean frame-processing time, and — when ``psutil`` is
available — process CPU and memory. Exposes a snapshot the dashboard's System Health
card and the Health Monitor consume.

``psutil`` is optional: if it is not installed, FPS and frame-time are still
reported and resource metrics are marked unavailable, so the monitor never fails.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

from config.config_manager import ConfigManager
from core.logger import get_logger
from utilities.helpers import MovingAverage

log = get_logger("performance")

try:  # optional dependency
    import psutil  # type: ignore
    _PSUTIL = True
except Exception:  # noqa: BLE001
    psutil = None  # type: ignore
    _PSUTIL = False


@dataclass
class PerformanceSnapshot:
    """A point-in-time view of system performance vs budget."""
    fps: float = 0.0
    frame_ms: float = 0.0
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    dropped_frames: int = 0
    fps_ok: bool = True
    frame_ms_ok: bool = True
    cpu_ok: bool = True
    memory_ok: bool = True
    resources_available: bool = _PSUTIL

    @property
    def within_budget(self) -> bool:
        return self.fps_ok and self.frame_ms_ok and self.cpu_ok and self.memory_ok


class PerformanceMonitor:
    """Tracks FPS, frame time, and resource usage against configured targets."""

    def __init__(self, config: ConfigManager) -> None:
        perf = config.section("performance")
        window = int(perf.get("sample_window", 30))
        self._target_fps = float(perf.get("target_fps", 15.0))
        self._max_frame_ms = float(perf.get("max_frame_ms", 80.0))
        self._max_cpu = float(perf.get("max_cpu_percent", 60.0))
        self._max_memory_mb = float(perf.get("max_memory_mb", 1500.0))

        self._fps_meter = MovingAverage(window)
        self._frame_ms_meter = MovingAverage(window)
        self._last_frame_time: Optional[float] = None
        self._dropped_frames = 0
        self._lock = threading.Lock()
        self._process = psutil.Process() if _PSUTIL else None
        if not _PSUTIL:
            log.info("psutil not installed; CPU/memory metrics disabled.")

    # -- recording ----------------------------------------------------------
    def record_frame(self, processing_ms: Optional[float] = None) -> None:
        """Record one processed frame: update FPS and (optionally) frame time."""
        now = time.time()
        with self._lock:
            if self._last_frame_time is not None:
                dt = now - self._last_frame_time
                if dt > 0:
                    self._fps_meter.update(1.0 / dt)
            self._last_frame_time = now
            if processing_ms is not None:
                self._frame_ms_meter.update(processing_ms)

    def record_dropped(self, count: int) -> None:
        with self._lock:
            self._dropped_frames = count

    def reset(self) -> None:
        with self._lock:
            self._fps_meter.reset()
            self._frame_ms_meter.reset()
            self._last_frame_time = None
            self._dropped_frames = 0

    # -- sampling -----------------------------------------------------------
    def _sample_resources(self) -> tuple[Optional[float], Optional[float]]:
        if not _PSUTIL or self._process is None:
            return None, None
        try:
            cpu = self._process.cpu_percent(interval=None)
            mem_mb = self._process.memory_info().rss / (1024 * 1024)
            return round(cpu, 1), round(mem_mb, 1)
        except Exception:  # noqa: BLE001
            return None, None

    def snapshot(self) -> PerformanceSnapshot:
        """Return current performance metrics and budget compliance."""
        with self._lock:
            fps = round(self._fps_meter.value, 1)
            frame_ms = round(self._frame_ms_meter.value, 1)
            dropped = self._dropped_frames

        cpu, memory = self._sample_resources()

        snap = PerformanceSnapshot(
            fps=fps,
            frame_ms=frame_ms,
            cpu_percent=cpu,
            memory_mb=memory,
            dropped_frames=dropped,
            fps_ok=(fps >= self._target_fps) or fps == 0.0,
            frame_ms_ok=(frame_ms <= self._max_frame_ms) or frame_ms == 0.0,
            cpu_ok=(cpu is None) or (cpu <= self._max_cpu),
            memory_ok=(memory is None) or (memory <= self._max_memory_mb),
        )
        return snap
