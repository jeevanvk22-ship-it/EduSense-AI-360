"""
EduSense AI 360 - Model Registry
================================

Owns the single instances of the AI models, lazily loaded and reused across frames
and sessions, and reports their health to the Health Monitor (Architecture Part 3
§9). Centralising model lifecycle here means the pipeline asks the registry for a
detector rather than constructing models itself, and model identity/version is
recorded in one place for reproducibility.
"""

from __future__ import annotations

from typing import Optional

from config.config_manager import ConfigManager
from backend.ai_models.face_detection import FaceDetector
from backend.ai_models.eye_tracking import EyeTracker
from backend.ai_models.emotion_detection import EmotionDetector
from backend.services.health_monitor import HealthMonitor
from core.logger import get_logger

log = get_logger("ai")


class ModelRegistry:
    """Creates, holds, and health-checks the AI models."""

    def __init__(self, config: ConfigManager, health: Optional[HealthMonitor] = None) -> None:
        self._config = config
        self._health = health
        self._face_detector: Optional[FaceDetector] = None
        self._eye_tracker: Optional[EyeTracker] = None
        self._emotion_detector: Optional[EmotionDetector] = None

    # -- accessors (lazy singletons) ---------------------------------------
    @property
    def face_detector(self) -> FaceDetector:
        if self._face_detector is None:
            self._face_detector = FaceDetector(self._config)
        return self._face_detector

    @property
    def eye_tracker(self) -> EyeTracker:
        if self._eye_tracker is None:
            self._eye_tracker = EyeTracker(self._config)
        return self._eye_tracker

    @property
    def emotion_detector(self) -> EmotionDetector:
        if self._emotion_detector is None:
            self._emotion_detector = EmotionDetector(self._config)
        return self._emotion_detector

    # -- health -------------------------------------------------------------
    def check_health(self) -> dict[str, bool]:
        """Probe each model's availability and report to the Health Monitor."""
        status = {
            "face_detection": self.face_detector.available,
            "eye_tracking": self.eye_tracker.available,
            "emotion_detection": self.emotion_detector.available,
        }
        if self._health is not None:
            for component, ok in status.items():
                if ok:
                    self._health.healthy(component)
                else:
                    self._health.degraded(component, "model unavailable")
        return status

    def versions(self) -> dict[str, str]:
        """Report model backend identity for session metadata/logs."""
        return {
            "face_detection": "mediapipe.face_detection",
            "eye_tracking": "mediapipe.face_mesh",
            "emotion_detection": f"{self._config.get('emotion.backend', 'fer')}",
        }

    def reset(self) -> None:
        """Clear per-session tracking/temporal state in all models."""
        if self._face_detector is not None:
            self._face_detector.reset()
        if self._eye_tracker is not None:
            self._eye_tracker.reset()
        if self._emotion_detector is not None:
            self._emotion_detector.reset()

    def close(self) -> None:
        for model in (self._face_detector, self._eye_tracker):
            if model is not None:
                model.close()
