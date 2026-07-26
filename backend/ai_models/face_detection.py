"""
EduSense AI 360 - Face Detection
================================

Detects student faces (MediaPipe) and assigns each a **stable per-session id** via
centroid tracking, so per-student reasoning stays continuous across frames
(Functional Requirements Part 1B §2; AI Decision Logic Part 6 §1.1).

* MediaPipe is imported lazily, so this module imports without the CV stack.
* The actual detector call is isolated in :meth:`_run_detection`, giving a clean
  seam for testing the tracking logic without the model.
* Output is a list of :class:`FaceBox` (with ``face_id``) — downstream modules never
  need to know MediaPipe was used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from config.config_manager import ConfigManager
from backend.contracts.models import FaceBox
from core.exceptions import FaceDetectionError
from core.error_handler import handle
from core.logger import get_logger
from utilities.helpers import euclidean

log = get_logger("ai")


@dataclass
class _RawDetection:
    """An untracked detection straight from the model (relative coords resolved)."""
    x: int
    y: int
    w: int
    h: int
    confidence: float


@dataclass
class _TrackedFace:
    """Internal tracking record for one identity."""
    face_id: int
    center: tuple[int, int]
    box: FaceBox
    lost_frames: int = 0


class FaceTracker:
    """Associates detections across frames to maintain stable identities."""

    def __init__(self, max_lost_frames: int, match_distance: float) -> None:
        self._max_lost = max_lost_frames
        self._match_distance = match_distance
        self._tracked: dict[int, _TrackedFace] = {}
        self._next_id = 0

    def reset(self) -> None:
        self._tracked.clear()
        self._next_id = 0

    def update(self, detections: list[FaceBox]) -> list[FaceBox]:
        """Assign stable ids to ``detections`` (greedy nearest-centroid match)."""
        unmatched_ids = set(self._tracked.keys())
        results: list[FaceBox] = []

        for det in detections:
            det_center = det.center
            best_id: Optional[int] = None
            best_dist = self._match_distance
            for tid in unmatched_ids:
                dist = euclidean(det_center, self._tracked[tid].center)
                if dist < best_dist:
                    best_dist = dist
                    best_id = tid

            if best_id is None:
                best_id = self._next_id
                self._next_id += 1
            else:
                unmatched_ids.discard(best_id)

            det.face_id = best_id
            self._tracked[best_id] = _TrackedFace(face_id=best_id, center=det_center, box=det)
            results.append(det)

        # Age out identities that were not matched this frame.
        for tid in list(unmatched_ids):
            record = self._tracked[tid]
            record.lost_frames += 1
            if record.lost_frames > self._max_lost:
                del self._tracked[tid]

        return results

    @property
    def active_ids(self) -> list[int]:
        return [tid for tid, rec in self._tracked.items() if rec.lost_frames == 0]


class FaceDetector:
    """Detects faces in BGR frames and tracks them to stable ids."""

    def __init__(self, config: ConfigManager) -> None:
        fd = config.section("face_detection")
        self._min_confidence = float(fd.get("min_confidence", 0.5))
        self._model_selection = int(fd.get("model_selection", 1))
        self._max_faces = int(config.get("camera.max_faces", 10))
        match_ratio = float(fd.get("reacquire_distance_ratio", 0.15))

        self._tracker = FaceTracker(
            max_lost_frames=int(fd.get("tracking_max_lost_frames", 15)),
            match_distance=10_000.0,  # replaced per-frame using frame diagonal * ratio
        )
        self._match_ratio = match_ratio
        self._detector: Any = None
        self._available: Optional[bool] = None

    # -- model lifecycle ----------------------------------------------------
    def _ensure_loaded(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import mediapipe as mp
            self._detector = mp.solutions.face_detection.FaceDetection(
                model_selection=self._model_selection,
                min_detection_confidence=self._min_confidence,
            )
            self._available = True
            log.info("Face detector loaded (MediaPipe, model %d).", self._model_selection)
        except Exception as exc:  # noqa: BLE001
            self._available = False
            handle(FaceDetectionError(f"Face detector unavailable: {exc}"),
                   context="face detector load", category="ai")
        return self._available

    @property
    def available(self) -> bool:
        return bool(self._ensure_loaded())

    def reset(self) -> None:
        """Clear tracking state (call when a session restarts)."""
        self._tracker.reset()

    # -- detection seam (mockable) -----------------------------------------
    def _run_detection(self, frame_bgr: Any) -> list[_RawDetection]:
        """Run the MediaPipe detector and return raw, resolved detections."""
        import cv2
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._detector.process(rgb)
        raw: list[_RawDetection] = []
        if not results.detections:
            return raw
        for det in results.detections:
            score = float(det.score[0]) if det.score else 0.0
            box = det.location_data.relative_bounding_box
            raw.append(_RawDetection(
                x=int(box.xmin * w), y=int(box.ymin * h),
                w=int(box.width * w), h=int(box.height * h),
                confidence=score,
            ))
        return raw

    # -- public api ---------------------------------------------------------
    def detect(self, frame_bgr: Any) -> list[FaceBox]:
        """Detect and track faces; return up to ``max_faces`` FaceBox with ids."""
        if not self._ensure_loaded():
            return []
        try:
            raw = self._run_detection(frame_bgr)
        except Exception as exc:  # noqa: BLE001 - per-frame fault must not break stream
            handle(FaceDetectionError(f"Detection failed: {exc}"),
                   context="face detection", category="ai")
            return []

        h, w = frame_bgr.shape[:2]
        self._tracker._match_distance = (w ** 2 + h ** 2) ** 0.5 * self._match_ratio

        boxes: list[FaceBox] = []
        for d in raw:
            if d.confidence < self._min_confidence:
                continue
            x1, y1 = max(0, d.x), max(0, d.y)
            x2, y2 = min(w, d.x + d.w), min(h, d.y + d.h)
            if x2 <= x1 or y2 <= y1:
                continue
            boxes.append(FaceBox(x=x1, y=y1, w=x2 - x1, h=y2 - y1, confidence=round(d.confidence, 3)))

        boxes.sort(key=lambda b: b.confidence, reverse=True)
        boxes = boxes[: self._max_faces]
        return self._tracker.update(boxes)

    def count(self, frame_bgr: Any) -> int:
        return len(self.detect(frame_bgr))

    def close(self) -> None:
        if self._detector is not None:
            try:
                self._detector.close()
            except Exception:  # noqa: BLE001
                pass
            self._detector = None
