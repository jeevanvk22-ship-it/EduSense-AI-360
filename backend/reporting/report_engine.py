"""
EduSense AI 360 - Report Engine
===============================

Assembles a complete, export-ready :class:`ReportData` bundle from a finished (or
in-progress) session (Functional Requirements Part 1B §12; Architecture Part 3 §17).
It gathers the session summary, the per-frame timeline, per-student summaries, and
the constructive teacher insights into one structure the Export Engine renders to
PDF / Excel / CSV.

Charts in exported documents are drawn natively by the Export Engine (ReportLab /
spreadsheet charts) from the timeline carried here, so reports need no extra
image-rendering dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from config.config_manager import ConfigManager
from backend.analytics.student_analytics import ClassroomAnalytics, StudentSummary
from backend.analytics.teacher_analytics import TeacherInsights
from backend.contracts.models import SessionSummary, FrameRecord
from core.logger import get_logger
from utilities.helpers import now_iso

log = get_logger("application")


@dataclass
class ReportData:
    """Everything needed to render a session report in any format."""
    session_summary: SessionSummary
    frames: list[FrameRecord]
    timeseries: dict[str, list]
    student_summaries: list[StudentSummary]
    teacher_observations: list[str]
    teacher_suggestions: list[str]
    teacher_overall: str
    generated_at: str = field(default_factory=now_iso)
    app_name: str = "EduSense AI 360"
    app_tagline: str = ""

    @property
    def has_data(self) -> bool:
        return self.session_summary.frames_recorded > 0


class ReportEngine:
    """Collects and aggregates session data into a ReportData bundle."""

    def __init__(self, config: ConfigManager) -> None:
        self._app_name = config.get("app.name", "EduSense AI 360")
        self._app_tagline = config.get("app.tagline", "")

    def build(
        self,
        classroom: ClassroomAnalytics,
        student_summaries: list[StudentSummary],
        teacher_insights: TeacherInsights,
    ) -> ReportData:
        """Assemble a ReportData bundle from the analytics sources."""
        return ReportData(
            session_summary=classroom.summary(),
            frames=list(classroom.frames),
            timeseries=classroom.timeseries(),
            student_summaries=list(student_summaries),
            teacher_observations=list(teacher_insights.observations),
            teacher_suggestions=list(teacher_insights.suggestions),
            teacher_overall=teacher_insights.overall,
            app_name=self._app_name,
            app_tagline=self._app_tagline,
        )

    def preview_text(self, data: ReportData) -> str:
        """A short human-readable preview of the report contents."""
        s = data.session_summary
        lines = [
            f"# {data.app_name} — Session Report",
            f"**{s.session_name}**  ·  generated {data.generated_at}",
            "",
            f"- Duration: {s.duration_seconds}s over {s.frames_recorded} frames",
            f"- Average engagement: {s.average_engagement}/100  ·  "
            f"peak {s.peak_engagement}  ·  lowest {s.lowest_engagement}",
            f"- Attention trend: {s.attention_trend.value}",
            f"- Average attendance: {s.average_attendance} students",
            f"- Students analysed: {len(data.student_summaries)}",
            "",
            f"**Overall:** {data.teacher_overall or '—'}",
        ]
        return "\n".join(lines)
