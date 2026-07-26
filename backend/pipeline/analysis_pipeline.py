"""
EduSense AI 360 - Analysis Pipeline
===================================

Composes perception with interpretation to produce the full per-frame
:class:`FrameResult` (Architecture Part 3 §4). It sits one level above the
perception :class:`FramePipeline`:

    ProcessedFrame
        -> FramePipeline (detect / eyes / emotion / annotate)   [perception]
        -> AttentionEngine + EngagementEngine                   [scoring]
        -> RemarksEngine                                        [live remark]
        -> StudentAnalytics + ClassroomAnalytics                [accumulation]
        => FrameResult

Keeping this composition in its own module preserves the perception pipeline as a
self-contained unit while giving the application a single call - ``analyze()`` - that
yields everything the dashboard and reports need. Session-level summaries, teacher
insights, and end-of-session remarks are exposed for the reporting layer.
"""

from __future__ import annotations

import time
from typing import Optional

from config.config_manager import ConfigManager
from backend.pipeline.frame_pipeline import FramePipeline, PerceptionResult
from backend.camera.frame_processor import ProcessedFrame
from backend.ai_models.model_registry import ModelRegistry
from backend.analytics.attention_engine import AttentionEngine
from backend.analytics.engagement_engine import EngagementEngine
from backend.analytics.student_analytics import StudentAnalytics, ClassroomAnalytics, StudentSummary
from backend.analytics.teacher_analytics import TeacherAnalytics, TeacherInsights
from backend.remarks.remarks_engine import RemarksEngine, SessionRemarks
from backend.contracts.models import (
    FrameResult, StudentResult, EngagementResult, EmotionLabel, SessionSummary,
)
from core.logger import get_logger

log = get_logger("application")


class AnalysisPipeline:
    """Full per-frame analysis: perception + engagement + remarks + analytics."""

    def __init__(
        self,
        config: ConfigManager,
        registry: ModelRegistry,
        session_id: str = "",
        session_name: str = "",
    ) -> None:
        self._config = config
        self._perception = FramePipeline(config, registry)
        self._demo_source = None
        self._attention = AttentionEngine(config)
        self._engagement = EngagementEngine(config)
        self._student_analytics = StudentAnalytics(config)
        self._classroom = ClassroomAnalytics(config, session_id, session_name)
        self._teacher = TeacherAnalytics(config)
        self._remarks = RemarksEngine(config, self._teacher)

    # -- lifecycle ----------------------------------------------------------
    def reset(self, session_id: str = "", session_name: str = "") -> None:
        """Clear all per-session state (call when a session restarts)."""
        self._perception.reset()
        self._demo_source = None
        self._attention.reset()
        self._engagement.reset()
        self._student_analytics.reset()
        self._classroom.reset(session_id, session_name)

    # -- per-frame ----------------------------------------------------------
    def analyze(self, processed: ProcessedFrame, now: Optional[float] = None) -> FrameResult:
        """Analyse one processed frame end-to-end, returning a FrameResult."""
        now = time.time() if now is None else now
        source = self._demo_source or self._perception
        perception: PerceptionResult = source.process(processed)

        result = FrameResult(annotated_frame=perception.annotated_frame)
        engagement_results: list[EngagementResult] = []
        active_ids: set[int] = set()

        for face in perception.faces:
            sid = face.face_id
            active_ids.add(sid)

            attention_reading = self._attention.update(sid, face.eye, present=True, now=now)
            engagement = self._engagement.score_face(
                student_id=sid, eye=face.eye, emotion=face.emotion, present=True,
                attention_override=attention_reading.attention, now=now,
            )
            engagement_results.append(engagement)

            self._student_analytics.record(sid, engagement, attention_reading)
            summary = self._student_analytics.summary(sid)
            remark = self._remarks.student_remark(engagement, summary, attention_reading)

            result.students.append(StudentResult(
                student_id=sid, box=face.box, engagement=engagement,
                eye=face.eye, emotion=face.emotion, remark=remark,
            ))

        # Classroom aggregates.
        result.faces_present = perception.faces_present
        result.distracted_count = sum(1 for e in engagement_results if e.distracted)
        result.classroom_engagement = EngagementEngine.classroom_average(engagement_results)
        result.dominant_emotion = perception.dominant_emotion

        self._classroom.record(
            classroom_engagement=result.classroom_engagement,
            faces_present=result.faces_present,
            distracted_count=result.distracted_count,
            dominant_emotion=result.dominant_emotion.value,
            now=now,
        )

        # Release state for students who left the frame.
        self._attention.cleanup(active_ids)
        self._engagement.cleanup(active_ids)
        return result

    # -- session-level accessors -------------------------------------------
    @property
    def classroom(self) -> ClassroomAnalytics:
        return self._classroom

    def student_summaries(self) -> list[StudentSummary]:
        return self._student_analytics.all_summaries()

    def session_summary(self) -> SessionSummary:
        return self._classroom.summary()

    def teacher_insights(self) -> TeacherInsights:
        return self._teacher.analyse(self._classroom)

    def session_remarks(self) -> SessionRemarks:
        return self._remarks.session_remarks(self._classroom, self.student_summaries())

    def close_session(self) -> None:
        self._classroom.close()

    # -- demo mode ----------------------------------------------------------
    def use_demo_source(self, source) -> None:
        """Inject a synthetic perception source (Demo Mode)."""
        self._demo_source = source

    def clear_demo_source(self) -> None:
        self._demo_source = None

    @property
    def in_demo_mode(self) -> bool:
        return self._demo_source is not None
