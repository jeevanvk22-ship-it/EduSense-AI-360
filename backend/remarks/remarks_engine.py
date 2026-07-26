"""
EduSense AI 360 - Remarks Engine
================================

The arbitration layer that turns analytics into the system's natural-language
outputs (AI Decision Logic Part 6 §9): student remarks, teacher remarks, a session
summary, alerts, and positive feedback.

It enforces the priority discipline (alert > negative > neutral > positive), emits
exactly one *primary* remark per student per update (guaranteeing no contradictory
remarks), and is rule-transparent and explainable. A future version can swap the
underlying generators for an LLM behind these same method signatures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from config.config_manager import ConfigManager
from backend.contracts.models import EngagementResult, SessionSummary
from backend.analytics.attention_engine import AttentionReading
from backend.analytics.student_analytics import StudentSummary, ClassroomAnalytics
from backend.analytics.teacher_analytics import TeacherAnalytics, TeacherInsights
from backend.remarks import student_remarks as student_rules
from backend.remarks import teacher_remarks as teacher_rules
from core.logger import get_logger

log = get_logger("application")


@dataclass
class SessionRemarks:
    """The full set of end-of-session natural-language outputs."""
    session_summary: str = ""
    teacher_observations: list[str] = field(default_factory=list)
    teacher_suggestions: list[str] = field(default_factory=list)
    student_remarks: dict[int, str] = field(default_factory=dict)
    positives: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)


class RemarksEngine:
    """Generates prioritised, consistent remarks for students and teachers."""

    def __init__(self, config: ConfigManager, teacher_analytics: Optional[TeacherAnalytics] = None) -> None:
        self._teacher = teacher_analytics or TeacherAnalytics(config)

    # -- live, per-student --------------------------------------------------
    def student_remark(
        self,
        engagement: EngagementResult,
        summary: Optional[StudentSummary] = None,
        attention: Optional[AttentionReading] = None,
    ) -> str:
        """Return the single highest-priority remark for a student."""
        return student_rules.evaluate(engagement, summary, attention).text

    # -- session-level ------------------------------------------------------
    def session_remarks(
        self,
        classroom: ClassroomAnalytics,
        student_summaries: list[StudentSummary],
    ) -> SessionRemarks:
        """Assemble the complete set of session remarks."""
        insights: TeacherInsights = self._teacher.analyse(classroom)
        suggestions = teacher_rules.build(insights)

        out = SessionRemarks(
            session_summary=insights.overall,
            teacher_observations=insights.observations,
            teacher_suggestions=suggestions,
        )

        # Per-student remarks + alerts + positives, kept consistent by tier.
        for s in student_summaries:
            remark = self._summary_remark(s)
            out.student_remarks[s.student_id] = remark
            if "Needs attention" in s.behaviour_pattern:
                out.alerts.append(f"Student {s.student_id + 1}: {remark}")
            elif s.average_engagement >= 75:
                out.positives.append(f"Student {s.student_id + 1}: {remark}")

        if not out.student_remarks:
            out.session_summary = out.session_summary or "No students were tracked this session."
        return out

    def _summary_remark(self, summary: StudentSummary) -> str:
        """A remark derived from a whole-session student summary."""
        if "Needs attention" in summary.behaviour_pattern:
            return "Needs additional attention - extended disengagement was observed."
        if summary.average_engagement >= 75 and summary.low_engagement_periods == 0:
            return "Highly engaged with good classroom participation throughout."
        if summary.trend.value == "Rising":
            return "Positive improvement - engagement rose over the session."
        if summary.trend.value == "Declining":
            return "Engagement declined over the session; may benefit from re-engagement."
        if summary.average_engagement < 40:
            return "Low participation - attention was frequently away from the lesson."
        return "Steady, moderate participation across the session."
