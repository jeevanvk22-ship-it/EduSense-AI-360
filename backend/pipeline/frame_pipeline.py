"""
EduSense AI 360 - Frame (Perception) Pipeline
=============================================

The single orchestration point for the computer-vision stages (Architecture Part 3
§4; AI Decision Logic Part 6 §1). Per processed frame it:

  1. detects + tracks faces        (face_detection)   - on the down-scaled frame
  2. derives attention signals     (eye_tracking)     - on the full frame
  3. classifies emotion per face   (emotion_detection)
  4. annotates the frame for display

It produces a :class:`PerceptionResult` (faces with their FaceBox, EyeSignals, and
EmotionResult). Engagement scoring and remarks compose *on top of* this result in the
analytics phase, keeping perception and interpretation cleanly separated.

Frame-quality confidence (from frame processing) is propagated into the eye and
emotion confidences, so unreliable frames produce lower-confidence signals rather
than confident errors (Part 6 §14).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from config.config_manager import ConfigManager
from backend.ai_models.model_registry import ModelRegistry
from backend.camera.frame_processor import ProcessedFrame
from backend.contracts.models import FaceBox, EyeSignals, EmotionResult, EmotionLabel
from core.error_handler import handle
from core.logger import get_logger

log = get_logger("ai")


@dataclass
class PerceptionFace:
    """Per-face perception bundle for one frame."""
    face_id: int
    box: FaceBox
    eye: Optional[EyeSignals] = None
    emotion: Optional[EmotionResult] = None


@dataclass
class PerceptionResult:
    """Outcome of perceiving a single frame (pre-engagement)."""
    faces: list[PerceptionFace] = field(default_factory=list)
    faces_present: int = 0
    dominant_emotion: EmotionLabel = EmotionLabel.NEUTRAL
    quality_confidence: float = 1.0
    annotated_frame: Any = None


class FramePipeline:
    """Composes the AI models to perceive one frame."""

    def __init__(self, config: ConfigManager, registry: ModelRegistry) -> None:
        self._config = config
        self._registry = registry

    def reset(self) -> None:
        """Clear per-session model state (tracking, temporal, smoothing)."""
        self._registry.reset()

    # -- helpers ------------------------------------------------------------
    @staticmethod
    def _rescale_boxes(boxes: list[FaceBox], from_shape, to_shape) -> list[FaceBox]:
        """Scale boxes detected on the analysis frame back to full-resolution."""
        fh, fw = from_shape[:2]
        th, tw = to_shape[:2]
        if (fw, fh) == (tw, th) or fw == 0 or fh == 0:
            return boxes
        sx, sy = tw / fw, th / fh
        for b in boxes:
            b.x = int(b.x * sx)
            b.y = int(b.y * sy)
            b.w = int(b.w * sx)
            b.h = int(b.h * sy)
        return boxes

    # -- main ---------------------------------------------------------------
    def process(self, processed: ProcessedFrame) -> PerceptionResult:
        """Run detection, eye tracking, and emotion on a processed frame."""
        result = PerceptionResult(quality_confidence=processed.quality.quality_confidence)
        full = processed.bgr
        analysis = processed.analysis

        try:
            faces = self._registry.face_detector.detect(analysis)
            faces = self._rescale_boxes(faces, analysis.shape, full.shape)
        except Exception as exc:  # noqa: BLE001
            handle(exc, context="perception: detection", category="ai")
            faces = []

        # Eye tracking (operates on the full-resolution frame).
        eye_signals: dict[int, EyeSignals] = {}
        if faces:
            try:
                eye_signals = self._registry.eye_tracker.analyze(
                    full, faces, quality_confidence=result.quality_confidence)
            except Exception as exc:  # noqa: BLE001
                handle(exc, context="perception: eye tracking", category="ai")

        annotated = full.copy() if hasattr(full, "copy") else full
        emotion_tally: dict[EmotionLabel, int] = {}

        for face in faces:
            crop = face.crop(full)
            try:
                emotion = self._registry.emotion_detector.analyze(
                    crop, face_id=face.face_id, quality_confidence=result.quality_confidence)
            except Exception as exc:  # noqa: BLE001
                handle(exc, context="perception: emotion", category="ai")
                emotion = EmotionResult()

            eye = eye_signals.get(face.face_id)
            result.faces.append(PerceptionFace(
                face_id=face.face_id, box=face, eye=eye, emotion=emotion))
            emotion_tally[emotion.dominant] = emotion_tally.get(emotion.dominant, 0) + 1
            self._annotate(annotated, face, eye, emotion)

        result.faces_present = len(faces)
        result.dominant_emotion = (
            max(emotion_tally, key=emotion_tally.get) if emotion_tally else EmotionLabel.NEUTRAL)
        result.annotated_frame = annotated
        return result

    # -- annotation ---------------------------------------------------------
    @staticmethod
    def _annotate(frame: Any, box: FaceBox, eye: Optional[EyeSignals],
                  emotion: Optional[EmotionResult]) -> None:
        """Draw the face box + a compact label. No-op if OpenCV is unavailable."""
        try:
            import cv2
        except ImportError:
            return
        attention = eye.attention if eye else 0.0
        g = int(255 * attention)
        r = int(255 * (1 - attention))
        color = (0, g, r)  # BGR
        cv2.rectangle(frame, (box.x, box.y), (box.x + box.w, box.y + box.h), color, 2)
        emo = emotion.dominant.value if emotion else "?"
        label = f"#{box.face_id} att{attention:.0%} {emo}"
        cv2.putText(frame, label, (box.x, max(0, box.y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        if eye and eye.sleeping:
            cv2.putText(frame, "ZZZ", (box.x + box.w - 36, box.y + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
