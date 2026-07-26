"""
EduSense AI 360 - Engagement Engine
===================================

The interpretive heart of the system (AI Decision Logic Part 6 §4). Fuses
attention, emotion, and presence into a 0-100 engagement score, maps it to a level
(Poor / Average / Good / Excellent) via configured bands, derives a risk level and
confidence, and tracks distraction and prolonged inattention per student.

All weights, bands, and thresholds are configuration-driven (no hard-coded values);
the score is temporally smoothed per student for a stable live reading. Missing
inputs substitute neutral defaults and lower confidence rather than failing.
"""

from __future__ import annotations

import time
from typing import Optional

from config.config_manager import ConfigManager
from backend.contracts.models import (
    EngagementResult, EngagementLevel, RiskLevel, EmotionResult, EyeSignals, EmotionLabel,
)
from core.exceptions import EngagementError
from core.error_handler import handle
from core.logger import get_logger
from utilities.helpers import clamp, safe_mean, MovingAverage

log = get_logger("ai")


class EngagementEngine:
    """Computes per-student engagement and classroom aggregates."""

    def __init__(self, config: ConfigManager) -> None:
        eng = config.section("engagement")
        weights = eng.get("weights", {})
        self._w_attention = float(weights.get("attention", 0.5))
        self._w_emotion = float(weights.get("emotion", 0.3))
        self._w_presence = float(weights.get("presence", 0.2))

        self._bands = sorted(
            [(int(b["min"]), str(b["label"])) for b in eng.get("bands", [])],
            key=lambda x: x[0], reverse=True,
        ) or [(81, "Excellent"), (61, "Good"), (31, "Average"), (0, "Poor")]

        self._distraction_threshold = float(eng.get("distraction_threshold", 31))
        self._prolonged_seconds = float(eng.get("prolonged_inattention_seconds", 10))
        self._smoothing = int(eng.get("smoothing_window", 15))

        risk = eng.get("risk_levels", {})
        self._risk_high_below = float(risk.get("high_below", 25))
        self._risk_moderate_below = float(risk.get("moderate_below", 50))

        self._smoothers: dict[int, MovingAverage] = {}
        self._distraction_since: dict[int, Optional[float]] = {}

    def reset(self) -> None:
        self._smoothers.clear()
        self._distraction_since.clear()

    # -- mapping helpers ----------------------------------------------------
    def _level_for(self, score: float) -> EngagementLevel:
        label = self._bands[-1][1]
        for lower, lbl in self._bands:
            if score >= lower:
                label = lbl
                break
        try:
            return EngagementLevel(label)
        except ValueError:
            return EngagementLevel.POOR

    def _risk_for(self, score: float, prolonged: bool) -> RiskLevel:
        if prolonged or score < self._risk_high_below:
            return RiskLevel.HIGH
        if score < self._risk_moderate_below:
            return RiskLevel.MODERATE
        return RiskLevel.LOW

    # -- scoring ------------------------------------------------------------
    def score_face(
        self,
        student_id: int,
        eye: Optional[EyeSignals],
        emotion: Optional[EmotionResult],
        present: bool = True,
        attention_override: Optional[float] = None,
        now: Optional[float] = None,
    ) -> EngagementResult:
        """Compute engagement for one student for the current frame."""
        now = time.time() if now is None else now
        try:
            attention = attention_override if attention_override is not None else (
                eye.attention if eye else 0.0)
            contribution = emotion.engagement_contribution if emotion else 0.0
            emotion_score = clamp((contribution + 1.0) / 2.0, 0.0, 1.0)
            presence = 1.0 if present else 0.0

            blended = (
                self._w_attention * attention
                + self._w_emotion * emotion_score
                + self._w_presence * presence
            )
            raw_score = clamp(blended * 100.0, 0.0, 100.0)

            smoother = self._smoothers.setdefault(student_id, MovingAverage(self._smoothing))
            score = round(smoother.update(raw_score), 1)

            distracted = score < self._distraction_threshold
            started = self._distraction_since.get(student_id)
            if distracted:
                if started is None:
                    started = now
                    self._distraction_since[student_id] = started
                distracted_seconds = now - started
            else:
                self._distraction_since[student_id] = None
                distracted_seconds = 0.0
            prolonged = distracted_seconds >= self._prolonged_seconds

            # Confidence from available input confidences, scaled by presence.
            confidences = [c for c in (
                eye.confidence if eye else None,
                emotion.confidence if emotion and emotion.available else None,
            ) if c is not None]
            confidence = round(clamp(safe_mean(confidences, 0.3) * presence, 0.0, 1.0), 3)

            return EngagementResult(
                score=score,
                level=self._level_for(score),
                attention=round(attention, 3),
                emotion_score=round(emotion_score, 3),
                presence=presence,
                confidence=confidence,
                risk_level=self._risk_for(score, prolonged),
                distracted=distracted,
                prolonged_inattention=prolonged,
                distracted_seconds=round(distracted_seconds, 1),
                dominant_emotion=emotion.dominant if emotion else EmotionLabel.NEUTRAL,
            )
        except Exception as exc:  # noqa: BLE001 - never break the per-frame loop
            handle(EngagementError(f"Engagement scoring failed: {exc}"),
                   context="engagement scoring", category="ai")
            return EngagementResult()

    @staticmethod
    def classroom_average(results: list[EngagementResult]) -> float:
        """Mean engagement across all visible students this frame."""
        if not results:
            return 0.0
        return round(sum(r.score for r in results) / len(results), 1)

    def cleanup(self, active_ids: set[int]) -> None:
        for sid in list(self._smoothers.keys()):
            if sid not in active_ids:
                self._smoothers.pop(sid, None)
                self._distraction_since.pop(sid, None)
