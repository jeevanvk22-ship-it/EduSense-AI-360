"""
EduSense AI 360 - Teacher Analytics
===================================

Analyses **classroom response** and produces constructive, time-anchored
observations and suggestions. It NEVER evaluates, ranks, or blames the teacher
(Functional Requirements Part 1B §7; AI Decision Logic Part 6 §8).

Inputs are the classroom time-series and summary from :class:`ClassroomAnalytics`.
Outputs are supportive natural-language observations plus impersonal teaching
suggestions, generated only when sufficient session data exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from config.config_manager import ConfigManager
from backend.contracts.models import TrendDirection
from backend.analytics.student_analytics import ClassroomAnalytics
from core.logger import get_logger
from utilities.helpers import safe_mean, format_duration

log = get_logger("application")


@dataclass
class TeacherInsights:
    """Constructive classroom-level insights and suggestions."""
    observations: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    drop_points: list[str] = field(default_factory=list)
    overall: str = ""


class TeacherAnalytics:
    """Derives constructive, non-evaluative classroom insights."""

    def __init__(self, config: ConfigManager) -> None:
        self._min_frames = int(config.get("analytics.trend_min_frames", 6))
        self._drop_delta = float(config.get("teacher.drop_delta", 12.0))

    def analyse(self, classroom: ClassroomAnalytics) -> TeacherInsights:
        """Produce insights from the classroom time-series and summary."""
        insights = TeacherInsights()
        summary = classroom.summary()

        if summary.frames_recorded < self._min_frames:
            insights.overall = "More session data is needed before insights can be drawn."
            return insights

        avg = summary.average_engagement
        trend = summary.attention_trend

        # Overall level (impersonal, supportive).
        if avg >= 75:
            insights.observations.append(
                f"Students maintained strong attention throughout (avg {avg}/100).")
        elif avg >= 55:
            insights.observations.append(
                f"Students were engaged overall (avg {avg}/100), with quieter stretches.")
        elif avg >= 35:
            insights.observations.append(
                f"Classroom engagement was moderate (avg {avg}/100).")
        else:
            insights.observations.append(
                f"Classroom engagement was low this session (avg {avg}/100); this often "
                "reflects pacing or difficulty rather than the class itself.")

        # Trend observation.
        if trend == TrendDirection.DECLINING:
            insights.observations.append("Attention gradually decreased as the session went on.")
            insights.suggestions.append(
                "A short activity or break around the dip can re-energise the room.")
        elif trend == TrendDirection.RISING:
            insights.observations.append("Engagement built up over the session.")
            insights.suggestions.append(
                "Whatever you shifted to later worked well and is worth front-loading.")
        elif trend == TrendDirection.STABLE:
            insights.observations.append("Attention stayed steady throughout the session.")

        # Time-anchored drop points.
        insights.drop_points = self._drop_points(classroom)
        for dp in insights.drop_points:
            insights.observations.append(dp)

        # General constructive suggestions tied to level.
        if avg < 60:
            insights.suggestions.extend([
                "Introduce a question or quick poll to invite participation.",
                "Use concrete examples or visuals to anchor difficult points.",
            ])
        if summary.average_attendance > 0:
            insights.observations.append(
                f"On average {summary.average_attendance} students were visible and participating.")

        insights.overall = self._overall(avg, trend)
        return insights

    # -- helpers ------------------------------------------------------------
    def _drop_points(self, classroom: ClassroomAnalytics) -> list[str]:
        """Find notable engagement dips and anchor them in time."""
        frames = classroom.frames
        if len(frames) < self._min_frames * 2:
            return []
        points: list[str] = []
        window = max(3, len(frames) // 10)
        for i in range(window, len(frames) - window):
            before = safe_mean([f.classroom_engagement for f in frames[i - window:i]])
            after = safe_mean([f.classroom_engagement for f in frames[i:i + window]])
            if before - after >= self._drop_delta:
                points.append(
                    f"Attention dipped around {format_duration(frames[i].t)} into the session.")
                # Skip ahead to avoid reporting the same dip repeatedly.
                break
        return points

    def _overall(self, avg: float, trend: TrendDirection) -> str:
        if avg >= 70 and trend != TrendDirection.DECLINING:
            return "A strong, well-engaged session overall."
        if trend == TrendDirection.RISING:
            return "Engagement improved through the session - a positive trajectory."
        if avg < 40:
            return "A challenging session for engagement; small interactive changes can help."
        return "A solid session with clear opportunities to lift the quieter moments."
