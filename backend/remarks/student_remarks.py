"""
EduSense AI 360 - Student Remarks Rules
=======================================

Rule set that maps a student's engagement state to one supportive, non-stigmatising
remark (AI Decision Logic Part 6 §7, §9). Rules are ordered by priority so the most
important message is chosen; the Remarks Engine performs the selection.

Each rule is a predicate over the engagement result (and optional session summary)
plus the remark text it yields. Sensitive observations are phrased cautiously as
possibilities warranting attention - never as diagnoses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from backend.contracts.models import EngagementResult, EngagementLevel, EmotionLabel, RiskLevel
from backend.analytics.student_analytics import StudentSummary
from backend.analytics.attention_engine import AttentionReading, AttentionLevel


@dataclass
class StudentRemark:
    """A selected student remark with the priority tier that produced it."""
    text: str
    priority: int          # lower = higher priority
    tier: str              # "alert" | "negative" | "neutral" | "positive"


def evaluate(
    engagement: EngagementResult,
    summary: Optional[StudentSummary] = None,
    attention: Optional[AttentionReading] = None,
) -> StudentRemark:
    """Return the single highest-priority remark for a student.

    Priority tiers (Part 6 §9.1):
        1 alert  -> safety/attention
        2 negative -> declining/low/confusion
        3 neutral
        4 positive
    """
    # --- Tier 1: safety / attention alerts --------------------------------
    if engagement.prolonged_inattention or (attention and attention.level == AttentionLevel.UNKNOWN
                                            and engagement.presence == 0.0):
        if engagement.prolonged_inattention:
            return StudentRemark(
                "Has been disengaged for a while - may benefit from a direct check-in.",
                1, "alert")
    if engagement.risk_level == RiskLevel.HIGH and engagement.distracted:
        return StudentRemark(
            "Sustained low engagement - worth a gentle check-in.", 1, "alert")

    # --- Tier 2: negative / declining -------------------------------------
    if summary is not None and summary.trend.value == "Declining":
        return StudentRemark("Engagement has been declining - may need re-engaging.", 2, "negative")
    if engagement.score < 31:
        if engagement.dominant_emotion in (EmotionLabel.SAD, EmotionLabel.FEAR):
            return StudentRemark(
                "Appears disengaged and possibly confused - worth checking understanding.",
                2, "negative")
        if engagement.presence == 0.0:
            return StudentRemark("Not clearly visible to the camera right now.", 2, "negative")
        return StudentRemark("Currently distracted - attention is away from the lesson.", 2, "negative")
    if engagement.dominant_emotion in (EmotionLabel.SAD, EmotionLabel.FEAR) and engagement.score < 55:
        return StudentRemark(
            "Following along but may be a little confused - worth a check.", 2, "negative")

    # --- Tier 4: positive reinforcement -----------------------------------
    if engagement.level == EngagementLevel.EXCELLENT:
        return StudentRemark("Strongly focused and actively following the lesson.", 4, "positive")
    if engagement.level == EngagementLevel.GOOD:
        if summary is not None and summary.trend.value == "Rising":
            return StudentRemark("Engaged, with attention improving over the session.", 4, "positive")
        return StudentRemark("Engaged and attentive overall.", 4, "positive")

    # --- Tier 3: neutral / steady -----------------------------------------
    return StudentRemark("Partially engaged; attention drifts intermittently.", 3, "neutral")
