"""
EduSense AI 360 - Attention Engine
==================================

Consolidates attention semantics so the Engagement Engine stays clean
(Architecture Part 3 §11; AI Decision Logic Part 6 §2). Per student it:

* classifies the attention value into a state (High / Medium / Low / Unknown),
* tracks **focus continuity** (consecutive on-task frames) and distraction streaks,
* accumulates **attentive vs distracted time** (wall-clock) for Student Analytics.

It deliberately does *not* own the engagement-score-based prolonged-inattention timer
(that lives in the Engagement Engine, since it is defined on the engagement score),
which avoids any circular dependency between the two engines.

State thresholds are read from configuration with sensible fallbacks, so no existing
configuration file needs changing for this engine to work.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from config.config_manager import ConfigManager
from backend.contracts.models import EyeSignals
from core.logger import get_logger
from utilities.helpers import clamp

log = get_logger("ai")


class AttentionLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNKNOWN = "Unknown"


@dataclass
class AttentionReading:
    """Per-student attention outcome for one frame."""
    attention: float = 0.0           # [0, 1]
    level: AttentionLevel = AttentionLevel.UNKNOWN
    focus_streak: int = 0            # consecutive on-task frames
    attentive_seconds: float = 0.0   # cumulative this session
    distracted_seconds: float = 0.0  # cumulative this session
    confidence: float = 0.0


@dataclass
class _AttnState:
    focus_streak: int = 0
    attentive_seconds: float = 0.0
    distracted_seconds: float = 0.0
    last_update: Optional[float] = None


class AttentionEngine:
    """Classifies attention and tracks continuity and time per student."""

    def __init__(self, config: ConfigManager) -> None:
        # Attention-state thresholds (config-driven, fallback defaults).
        self._high = float(config.get("attention.high_threshold", 0.66))
        self._medium = float(config.get("attention.medium_threshold", 0.33))
        self._confidence_floor = float(config.get("attention.confidence_floor", 0.25))
        self._state: dict[int, _AttnState] = {}

    def reset(self) -> None:
        self._state.clear()

    # -- classification -----------------------------------------------------
    def classify(self, attention: float, present: bool, confidence: float) -> AttentionLevel:
        """Map an attention value to a state, honouring presence and confidence."""
        if not present or confidence < self._confidence_floor:
            return AttentionLevel.UNKNOWN
        if attention >= self._high:
            return AttentionLevel.HIGH
        if attention >= self._medium:
            return AttentionLevel.MEDIUM
        return AttentionLevel.LOW

    # -- update -------------------------------------------------------------
    def update(
        self,
        student_id: int,
        eye: Optional[EyeSignals],
        present: bool,
        now: Optional[float] = None,
    ) -> AttentionReading:
        """Evolve per-student attention state and return the reading."""
        now = time.time() if now is None else now
        state = self._state.setdefault(student_id, _AttnState())

        attention = eye.attention if eye else 0.0
        confidence = eye.confidence if eye else 0.0
        level = self.classify(attention, present, confidence)

        # Time accumulation by wall-clock delta since this student's last update.
        if state.last_update is not None:
            dt = max(0.0, now - state.last_update)
            if level in (AttentionLevel.HIGH, AttentionLevel.MEDIUM):
                state.attentive_seconds += dt
            elif level == AttentionLevel.LOW:
                state.distracted_seconds += dt
            # UNKNOWN time is attributed to neither bucket.
        state.last_update = now

        # Focus continuity.
        if level in (AttentionLevel.HIGH, AttentionLevel.MEDIUM):
            state.focus_streak += 1
        else:
            state.focus_streak = 0

        return AttentionReading(
            attention=round(attention, 3),
            level=level,
            focus_streak=state.focus_streak,
            attentive_seconds=round(state.attentive_seconds, 1),
            distracted_seconds=round(state.distracted_seconds, 1),
            confidence=round(confidence, 3),
        )

    def cleanup(self, active_ids: set[int]) -> None:
        """Drop state for students no longer present."""
        for sid in list(self._state.keys()):
            if sid not in active_ids:
                self._state.pop(sid, None)
