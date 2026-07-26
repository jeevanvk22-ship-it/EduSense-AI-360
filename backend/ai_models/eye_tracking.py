"""
EduSense AI 360 - Eye Tracking
==============================

Derives per-student attention signals from facial landmarks (MediaPipe FaceMesh
with iris refinement): eye openness (EAR), blink, gaze direction, head pose, sleep
detection, and a blended attention value with confidence (Functional Requirements
Part 1B §3; AI Decision Logic Part 6 §2).

Temporal signals (blink, sleeping) require per-student memory, so the tracker keeps
state keyed by the **face id** supplied by detection. FaceMesh results are matched to
detection boxes by centroid proximity.

Design seams for testing
------------------------
* :meth:`_run_facemesh` isolates the model call.
* :meth:`_signals_from_mesh` computes instantaneous geometry (pure maths).
* :meth:`_apply_temporal` evolves per-id state (blink/sleep/smoothing).
These let the temporal logic and geometry be tested without MediaPipe.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, NamedTuple, Optional

from config.config_manager import ConfigManager
from backend.contracts.models import EyeSignals, GazeDirection, FaceBox
from core.exceptions import EyeTrackingError
from core.error_handler import handle
from core.logger import get_logger
from utilities.helpers import euclidean, clamp, MovingAverage

log = get_logger("ai")

# FaceMesh landmark indices ---------------------------------------------------
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_CORNERS = (33, 133)
LEFT_CORNERS = (362, 263)
RIGHT_IRIS = 468
LEFT_IRIS = 473
POSE_LANDMARKS = {
    "nose_tip": 1, "chin": 199, "left_eye_corner": 33,
    "right_eye_corner": 263, "left_mouth": 61, "right_mouth": 291,
}


class Landmark(NamedTuple):
    x: float   # normalised [0, 1]
    y: float


@dataclass
class MeshResult:
    """A single face's landmarks plus its pixel-space centre."""
    landmarks: list[Landmark]
    center: tuple[int, int]


class _Instant(NamedTuple):
    """Instantaneous (single-frame) geometry before temporal smoothing."""
    ear: float
    gaze_offset: float
    gaze_direction: GazeDirection
    yaw: float
    pitch: float
    eyes_open: bool
    gaze_on_target: bool
    head_facing: bool
    landmarks_ok: bool


@dataclass
class _EyeState:
    """Per-student temporal state."""
    closed_run: int = 0
    closed_since: Optional[float] = None
    ear_avg: MovingAverage = field(default_factory=lambda: MovingAverage(5))
    attention_avg: MovingAverage = field(default_factory=lambda: MovingAverage(5))


class EyeTracker:
    """Computes attention signals per tracked face."""

    def __init__(self, config: ConfigManager) -> None:
        et = config.section("eye_tracking")
        self._ear_threshold = float(et.get("ear_open_threshold", 0.18))
        self._gaze_tolerance = float(et.get("gaze_center_tolerance", 0.22))
        self._yaw_limit = float(et.get("head_yaw_limit", 30.0))
        self._pitch_limit = float(et.get("head_pitch_limit", 25.0))
        self._long_closure = float(et.get("long_closure_seconds", 3.0))
        self._blink_min = int(et.get("blink_min_frames", 1))
        self._blink_max = int(et.get("blink_max_frames", 6))
        self._smoothing = int(et.get("smoothing_window", 5))
        self._max_faces = int(config.get("camera.max_faces", 10))
        self._match_ratio = float(config.get("face_detection.reacquire_distance_ratio", 0.15))

        self._face_mesh: Any = None
        self._available: Optional[bool] = None
        self._state: dict[int, _EyeState] = {}

    # -- model lifecycle ----------------------------------------------------
    def _ensure_loaded(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import mediapipe as mp
            self._face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=self._max_faces,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self._available = True
            log.info("Eye tracker loaded (MediaPipe FaceMesh).")
        except Exception as exc:  # noqa: BLE001
            self._available = False
            handle(EyeTrackingError(f"Eye tracker unavailable: {exc}"),
                   context="eye tracker load", category="ai")
        return self._available

    @property
    def available(self) -> bool:
        return bool(self._ensure_loaded())

    def reset(self) -> None:
        self._state.clear()

    # -- geometry (pure maths) ---------------------------------------------
    @staticmethod
    def _ear(landmarks: list[Landmark], idx: list[int], w: int, h: int) -> float:
        pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in idx]
        vertical = euclidean(pts[1], pts[5]) + euclidean(pts[2], pts[4])
        horizontal = 2.0 * euclidean(pts[0], pts[3])
        return vertical / horizontal if horizontal else 0.0

    @staticmethod
    def _gaze(landmarks: list[Landmark], corners: tuple[int, int], iris: int,
              w: int, h: int) -> tuple[float, float]:
        """Return (offset_magnitude, signed_horizontal_offset) for one eye."""
        c1 = (landmarks[corners[0]].x * w, landmarks[corners[0]].y * h)
        c2 = (landmarks[corners[1]].x * w, landmarks[corners[1]].y * h)
        ir = (landmarks[iris].x * w, landmarks[iris].y * h)
        center = ((c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2)
        width = euclidean(c1, c2)
        if not width:
            return 1.0, 0.0
        magnitude = clamp(euclidean(ir, center) / width, 0.0, 1.0)
        horizontal = (ir[0] - center[0]) / width
        return magnitude, horizontal

    def _head_pose(self, landmarks: list[Landmark], w: int, h: int) -> tuple[float, float]:
        import numpy as np
        import cv2
        model_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, -63.6, -12.5], [-43.3, 32.7, -26.0],
            [43.3, 32.7, -26.0], [-28.9, -28.9, -24.1], [28.9, -28.9, -24.1],
        ], dtype=np.float64)
        image_2d = np.array([
            [landmarks[POSE_LANDMARKS[k]].x * w, landmarks[POSE_LANDMARKS[k]].y * h]
            for k in ("nose_tip", "chin", "left_eye_corner", "right_eye_corner",
                      "left_mouth", "right_mouth")
        ], dtype=np.float64)
        cam = np.array([[w, 0, w / 2], [0, w, h / 2], [0, 0, 1]], dtype=np.float64)
        ok, rvec, _ = cv2.solvePnP(model_3d, image_2d, cam, np.zeros((4, 1)),
                                   flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok:
            return 0.0, 0.0
        rmat, _ = cv2.Rodrigues(rvec)
        sy = (rmat[0, 0] ** 2 + rmat[1, 0] ** 2) ** 0.5
        pitch = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
        yaw = float(np.degrees(np.arctan2(rmat[1, 0], rmat[0, 0])))
        return yaw, pitch

    def _signals_from_mesh(self, mesh: MeshResult, w: int, h: int) -> _Instant:
        """Compute instantaneous geometry from a face mesh."""
        lm = mesh.landmarks
        try:
            ear = (self._ear(lm, RIGHT_EYE, w, h) + self._ear(lm, LEFT_EYE, w, h)) / 2
            gr_mag, gr_h = self._gaze(lm, RIGHT_CORNERS, RIGHT_IRIS, w, h)
            gl_mag, gl_h = self._gaze(lm, LEFT_CORNERS, LEFT_IRIS, w, h)
            gaze_offset = (gr_mag + gl_mag) / 2
            horizontal = (gr_h + gl_h) / 2
            yaw, pitch = self._head_pose(lm, w, h)
            landmarks_ok = True
        except (IndexError, ZeroDivisionError):
            return _Instant(0.0, 1.0, GazeDirection.CENTER, 0.0, 0.0, False, False, False, False)

        eyes_open = ear >= self._ear_threshold
        gaze_on = gaze_offset <= self._gaze_tolerance
        head_facing = abs(yaw) <= self._yaw_limit and abs(pitch) <= self._pitch_limit
        direction = self._classify_gaze(horizontal, gaze_offset, yaw, pitch)
        return _Instant(ear, gaze_offset, direction, yaw, pitch,
                        eyes_open, gaze_on, head_facing, landmarks_ok)

    def _classify_gaze(self, horizontal: float, offset: float, yaw: float, pitch: float) -> GazeDirection:
        if offset <= self._gaze_tolerance and abs(yaw) <= self._yaw_limit:
            return GazeDirection.CENTER
        if abs(horizontal) >= abs(pitch) / 90.0:
            return GazeDirection.RIGHT if horizontal > 0 else GazeDirection.LEFT
        return GazeDirection.DOWN if pitch < 0 else GazeDirection.UP

    # -- temporal evolution -------------------------------------------------
    def _apply_temporal(self, face_id: int, inst: _Instant, quality_confidence: float,
                        now: Optional[float] = None) -> EyeSignals:
        """Update per-id state and produce the final smoothed EyeSignals."""
        now = time.time() if now is None else now
        state = self._state.setdefault(face_id, _EyeState(
            ear_avg=MovingAverage(self._smoothing), attention_avg=MovingAverage(self._smoothing)))

        blink = False
        sleeping = False
        if inst.eyes_open:
            # Eyes reopened: was the closure brief enough to be a blink?
            if self._blink_min <= state.closed_run <= self._blink_max:
                blink = True
            state.closed_run = 0
            state.closed_since = None
        else:
            state.closed_run += 1
            if state.closed_since is None:
                state.closed_since = now
            elif (now - state.closed_since) >= self._long_closure:
                sleeping = True

        smoothed_ear = state.ear_avg.update(inst.ear)

        # Attention blend (Part 6 §2.2): eyes-open + graded gaze + head-facing.
        graded_gaze = 1.0 - clamp(inst.gaze_offset / max(self._gaze_tolerance * 2, 1e-6), 0.0, 1.0)
        raw_attention = (
            0.40 * (1.0 if inst.eyes_open and not sleeping else 0.0)
            + 0.35 * graded_gaze
            + 0.25 * (1.0 if inst.head_facing else 0.0)
        )
        attention = state.attention_avg.update(clamp(raw_attention, 0.0, 1.0))

        # Confidence: landmark quality, dampened by extreme pose and frame quality.
        pose_penalty = clamp(1.0 - (abs(inst.yaw) / 90.0 + abs(inst.pitch) / 90.0) / 2, 0.2, 1.0)
        confidence = clamp((1.0 if inst.landmarks_ok else 0.2) * pose_penalty * quality_confidence, 0.0, 1.0)

        return EyeSignals(
            eyes_open=inst.eyes_open and not sleeping,
            ear=round(smoothed_ear, 3),
            blink=blink,
            gaze_direction=inst.gaze_direction,
            gaze_on_target=inst.gaze_on_target,
            gaze_offset=round(inst.gaze_offset, 3),
            head_facing=inst.head_facing,
            yaw=round(inst.yaw, 1),
            pitch=round(inst.pitch, 1),
            sleeping=sleeping,
            attention=round(attention, 3),
            confidence=round(confidence, 3),
        )

    # -- model seam (mockable) ---------------------------------------------
    def _run_facemesh(self, frame_bgr: Any) -> list[MeshResult]:
        import cv2
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)
        meshes: list[MeshResult] = []
        if not results.multi_face_landmarks:
            return meshes
        for face in results.multi_face_landmarks:
            lms = [Landmark(p.x, p.y) for p in face.landmark]
            xs = [p.x for p in face.landmark]
            ys = [p.y for p in face.landmark]
            center = (int(sum(xs) / len(xs) * w), int(sum(ys) / len(ys) * h))
            meshes.append(MeshResult(landmarks=lms, center=center))
        return meshes

    # -- public api ---------------------------------------------------------
    def analyze(self, frame_bgr: Any, faces: list[FaceBox],
                quality_confidence: float = 1.0) -> dict[int, EyeSignals]:
        """Return ``{face_id: EyeSignals}`` for the supplied tracked faces."""
        if not self._ensure_loaded() or not faces:
            return {}
        try:
            meshes = self._run_facemesh(frame_bgr)
        except Exception as exc:  # noqa: BLE001
            handle(EyeTrackingError(f"FaceMesh failed: {exc}"),
                   context="eye tracking", category="ai")
            return {}

        h, w = frame_bgr.shape[:2]
        match_distance = (w ** 2 + h ** 2) ** 0.5 * self._match_ratio
        out: dict[int, EyeSignals] = {}
        used: set[int] = set()

        for face in faces:
            best_idx, best_dist = -1, match_distance
            for i, mesh in enumerate(meshes):
                if i in used:
                    continue
                dist = euclidean(face.center, mesh.center)
                if dist < best_dist:
                    best_dist, best_idx = dist, i
            if best_idx < 0:
                continue
            used.add(best_idx)
            inst = self._signals_from_mesh(meshes[best_idx], w, h)
            out[face.face_id] = self._apply_temporal(face.face_id, inst, quality_confidence)

        # Drop temporal state for faces no longer present.
        for fid in list(self._state.keys()):
            if fid not in {f.face_id for f in faces}:
                self._state.pop(fid, None)
        return out

    def close(self) -> None:
        if self._face_mesh is not None:
            try:
                self._face_mesh.close()
            except Exception:  # noqa: BLE001
                pass
            self._face_mesh = None
