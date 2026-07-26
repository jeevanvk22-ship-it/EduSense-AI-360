"""
EduSense AI 360 - Session Manager
=================================

Owns the session lifecycle and is the bridge between the UI and the analysis
pipeline (Architecture Part 3 §15). It starts/pauses/resumes/stops sessions, keeps
the authoritative timer, processes each incoming frame through the pipeline, and
persists the finished session to disk.

In the Gradio app, frames arrive from the browser webcam as RGB images; this manager
converts them to the BGR working space, runs the full :class:`AnalysisPipeline`, and
records performance. It contains no UI code, so it is fully testable on its own.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from config.config_manager import ConfigManager
from backend.ai_models.model_registry import ModelRegistry
from backend.camera.frame_processor import FrameProcessor
from backend.pipeline.analysis_pipeline import AnalysisPipeline
from backend.services.notification_manager import NotificationManager
from backend.services.health_monitor import HealthMonitor
from backend.services.performance_monitor import PerformanceMonitor
from backend.contracts.models import FrameResult
from core.exceptions import SessionError
from core.error_handler import handle
from core.logger import get_logger
from utilities.helpers import safe_json_write, format_duration

log = get_logger("session")


class SessionStatus(str, Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"


class SessionManager:
    """Coordinates a monitoring session end to end."""

    def __init__(
        self,
        config: ConfigManager,
        registry: Optional[ModelRegistry] = None,
        notifications: Optional[NotificationManager] = None,
        health: Optional[HealthMonitor] = None,
        performance: Optional[PerformanceMonitor] = None,
    ) -> None:
        self._config = config
        self._health = health or HealthMonitor()
        self._registry = registry or ModelRegistry(config, self._health)
        self._notifications = notifications or NotificationManager()
        self._performance = performance or PerformanceMonitor(config)
        self._frame_processor = FrameProcessor(config)

        self._pipeline = AnalysisPipeline(config, self._registry)
        self._status = SessionStatus.IDLE
        self._session_id = ""
        self._session_name = ""
        self._started_at: Optional[float] = None
        self._paused_total = 0.0
        self._paused_at: Optional[float] = None

    # -- properties ---------------------------------------------------------
    @property
    def status(self) -> SessionStatus:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._status == SessionStatus.RUNNING

    @property
    def session_name(self) -> str:
        return self._session_name

    @property
    def pipeline(self) -> AnalysisPipeline:
        return self._pipeline

    @property
    def performance(self) -> PerformanceMonitor:
        return self._performance

    @property
    def health(self) -> HealthMonitor:
        return self._health

    @property
    def notifications(self) -> NotificationManager:
        return self._notifications

    def elapsed_seconds(self) -> float:
        if self._started_at is None:
            return 0.0
        end = self._paused_at if self._paused_at is not None else time.time()
        return max(0.0, end - self._started_at - self._paused_total)

    def elapsed_display(self) -> str:
        return format_duration(self.elapsed_seconds())

    # -- lifecycle ----------------------------------------------------------
    def start(self, session_name: str = "") -> str:
        """Start a new session; returns the session id."""
        self._session_id = uuid.uuid4().hex[:12]
        self._session_name = session_name.strip() or f"Session {time.strftime('%Y-%m-%d %H:%M')}"
        self._pipeline.reset(self._session_id, self._session_name)
        self._performance.reset()
        self._registry.check_health()
        self._started_at = time.time()
        self._paused_total = 0.0
        self._paused_at = None
        self._status = SessionStatus.RUNNING
        log.info("Session started: %s (%s)", self._session_name, self._session_id)
        self._notifications.success("Session started", self._session_name)
        return self._session_id

    def pause(self) -> None:
        if self._status == SessionStatus.RUNNING:
            self._status = SessionStatus.PAUSED
            self._paused_at = time.time()
            self._notifications.info("Session paused")

    def resume(self) -> None:
        if self._status == SessionStatus.PAUSED:
            if self._paused_at is not None:
                self._paused_total += time.time() - self._paused_at
            self._paused_at = None
            self._status = SessionStatus.RUNNING
            self._notifications.info("Session resumed")

    def stop(self) -> dict[str, Any]:
        """Stop the session, persist it, and return a summary payload."""
        if self._status == SessionStatus.IDLE:
            return {"saved": False, "message": "No active session."}
        self._pipeline.close_session()
        self._status = SessionStatus.IDLE
        payload = self._persist()
        self._notifications.success("Session completed", f"Saved: {self._session_name}")
        log.info("Session stopped and saved: %s", self._session_id)
        return payload

    # -- per-frame ----------------------------------------------------------
    def process_frame(self, rgb_frame: Any, now: Optional[float] = None) -> Optional[FrameResult]:
        """Process one RGB frame (from the browser webcam) through the pipeline."""
        if not self.is_running or rgb_frame is None:
            return None
        try:
            start = time.time()
            bgr = rgb_frame[:, :, ::-1]   # RGB -> BGR view (NumPy)
            processed = self._frame_processor.process(bgr)
            if processed is None:
                return None
            result = self._pipeline.analyze(processed, now=now)
            self._performance.record_frame(processing_ms=(time.time() - start) * 1000.0)
            return result
        except Exception as exc:  # noqa: BLE001 - a bad frame must not break streaming
            handle(exc, context="session frame processing", category="ai")
            return None

    # -- persistence --------------------------------------------------------
    def _persist(self) -> dict[str, Any]:
        try:
            summary = self._pipeline.session_summary()
            students = self._pipeline.student_summaries()
            insights = self._pipeline.teacher_insights()
            sessions_dir = Path(self._config.resolve_path("sessions_dir"))
            path = sessions_dir / f"{self._session_id}.json"
            data = {
                "summary": summary.as_dict(),
                "model_versions": self._registry.versions(),
                "frames": [asdict(f) for f in self._pipeline.classroom.frames],
                "student_summaries": [asdict(s) for s in students],
                "teacher_insights": {
                    "observations": insights.observations,
                    "suggestions": insights.suggestions,
                    "drop_points": insights.drop_points,
                    "overall": insights.overall,
                },
            }
            ok = safe_json_write(path, data)
            return {"saved": ok, "path": str(path), "summary": summary.as_dict(),
                    "message": f"Session saved ({summary.frames_recorded} frames)."}
        except Exception as exc:  # noqa: BLE001
            handle(SessionError(f"Failed to persist session: {exc}"),
                   context="session persistence", category="session")
            return {"saved": False, "message": "Session could not be saved."}
