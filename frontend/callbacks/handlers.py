"""
EduSense AI 360 - Dashboard Controller
======================================

The mediator between the Gradio views and the backend. It holds the session
manager, graph engine, settings manager, and services, and exposes high-level
methods the views bind to (start/stop, process a streamed frame, refresh analytics,
update settings). It returns plain values - strings, figures, images - so it carries
no Gradio dependency and is testable on its own.
"""

from __future__ import annotations

from typing import Any, Optional

from config.config_manager import ConfigManager, get_config
from config.settings_manager import SettingsManager
from backend.session.session_manager import SessionManager
from backend.reporting.graph_engine import GraphEngine
from backend.reporting.report_engine import ReportEngine
from backend.reporting.export_engine import ExportEngine
from backend.contracts.models import FrameResult
from core.exceptions import ValidationError, ExportError
from core.logger import get_logger
from frontend.components import cards

log = get_logger("application")


class DashboardController:
    """Application controller backing the dashboard views."""

    def __init__(self, config: Optional[ConfigManager] = None) -> None:
        self._config = config or get_config()
        self._session = SessionManager(self._config)
        self._graphs = GraphEngine()
        self._reports = ReportEngine(self._config)
        self._exports = ExportEngine(self._config)
        self._settings = SettingsManager(self._config)
        self._last_result: Optional[FrameResult] = None
        self._cache: dict[str, str] = {}
        self._tick = 0
        from collections import deque
        self._att_hist: deque = deque(maxlen=48)   # presentation-only buffers for sparklines
        self._eng_hist: deque = deque(maxlen=48)
        self._first_frame = True

    def _reset_live_state(self) -> None:
        self._att_hist.clear()
        self._eng_hist.clear()
        self._first_frame = True
        self._cache.clear()
        self._tick = 0

    # -- session controls ---------------------------------------------------
    def start_session(self, name: str) -> str:
        self._reset_live_state()
        self._session.start(name)
        return "🟢 Session running — analysing the live feed."

    def stop_session(self) -> str:
        payload = self._session.stop()
        return f"⏹️ {payload.get('message', 'Stopped.')}"

    def pause_session(self) -> str:
        self._session.pause()
        return "⏸️ Session paused."

    def resume_session(self) -> str:
        self._session.resume()
        return "▶️ Session resumed."

    def is_running(self) -> bool:
        return self._session.is_running

    # -- demo mode ----------------------------------------------------------
    @staticmethod
    def _demo_canvas():
        """A branded dark backdrop the demo source draws detections onto."""
        import numpy as np
        h, w = 432, 720
        grad = np.linspace(14, 28, h, dtype=np.uint8).reshape(h, 1, 1)
        canvas = np.repeat(np.repeat(grad, w, axis=1), 3, axis=2)
        canvas[:, :, 2] = np.clip(canvas[:, :, 2].astype(int) + 18, 0, 255)  # warm R for navy
        return np.ascontiguousarray(canvas)

    def run_demo(self, frames: int = 36):
        """Run a synthetic, camera-free session that populates every screen."""
        import time as _time
        from backend.pipeline.demo_source import DemoSource

        self._session.start("Demo · Class 8B Science")
        self._session.pipeline.use_demo_source(DemoSource())
        canvas = self._demo_canvas()
        t0 = _time.time()
        last = None
        for k in range(frames):
            last = self._session.process_frame(canvas, now=t0 + k)  # 1s/frame simulated
        self._session.stop()
        self._session.pipeline.clear_demo_source()

        if last is None:
            return canvas, self._last_kpis(), self._last_students(), self._status_html(), \
                "⚠️ Demo could not run."
        self._last_result = last
        annotated = last.annotated_frame
        annotated_rgb = annotated[:, :, ::-1] if annotated is not None else canvas
        fps = self._session.performance.snapshot().fps
        msg = ("✅ Demo session complete. Open **Analytics**, **Student Insights**, "
               "**Teacher Insights**, and **Reports** — all populated from this run.")
        return (annotated_rgb, cards.live_kpis(last, fps, self._session.elapsed_display()),
                cards.students_panel(last), self._status_html(), msg)

    # -- dashboard (live, split panels) -------------------------------------
    def _topbar(self) -> str:
        running = self._session.is_running
        demo = self._session.pipeline.in_demo_mode
        return cards.topbar("Live Monitor", self._session.session_name if running else "",
                            self._session.elapsed_display() if running else "00m 00s", running, demo)

    @staticmethod
    def _avg(vals):
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    @staticmethod
    def _pct(v):
        return "—" if v is None else f"{v * 100:.0f}%"

    def _distinct_seen(self) -> int:
        try:
            return len(self._session.pipeline.student_summaries())
        except Exception:
            return 0

    def _tracking_label(self) -> str:
        faces = (self._session.pipeline.classroom.timeseries().get("faces") or [])
        if len(faces) < 3:
            return "Initialising"
        recent = faces[-8:]
        return "Stable" if (max(recent) - min(recent)) <= 1 else "Variable"

    @staticmethod
    def _lighting_label(brightness, demo: bool) -> str:
        if demo:
            return "Simulated"
        if brightness is None:
            return "Unknown"
        if brightness < 55:
            return "Dim"
        if brightness > 205:
            return "Bright"
        return "Good"

    @staticmethod
    def _detection_label(result) -> str:
        students = result.students or []
        if not students:
            return "—"
        c = sum(s.box.confidence for s in students) / len(students)
        return "Excellent" if c >= 0.9 else "Good" if c >= 0.75 else "Fair" if c >= 0.5 else "Low"

    def _overall_conf(self, result):
        return self._avg([s.engagement.confidence for s in (result.students or [])])

    def _gauge_panel(self, result, animate: bool = False) -> str:
        eng = result.classroom_engagement
        eng_conf = self._avg([s.engagement.confidence for s in (result.students or [])])
        return cards.engagement_gauge(eng, cards._status5(eng), eng_conf,
                                      cards._classroom_status(eng), animate)

    def _kpi_panel(self, result, fps: float) -> str:
        return cards.kpi_cards(result, fps, self._session.elapsed_display(), self._distinct_seen(),
                               list(self._att_hist), list(self._eng_hist))

    def _graph_panel(self) -> str:
        return cards.engagement_graph_svg(self._session.pipeline.classroom.timeseries())

    def _insights_and_recs(self) -> tuple:
        ins = self._session.pipeline.teacher_insights()
        return (cards.teacher_insights_card(ins.observations),
                cards.recommendations_card(ins.suggestions))

    def _ai_conf_panel(self, result, brightness, demo: bool) -> str:
        return cards.ai_confidence_card(
            self._overall_conf(result), self._tracking_label(),
            self._lighting_label(brightness, demo), self._detection_label(result),
            self._session.health.overall().value)

    def _ribbon_panel(self, result, brightness, demo: bool) -> str:
        running = self._session.is_running
        health = self._session.health.overall().value
        tracking = self._tracking_label()
        lighting = self._lighting_label(brightness, demo)
        det = self._detection_label(result)
        items = [
            ("Camera Connected" if running else "Camera Idle", "ok" if running else "warn"),
            ("AI Models Loaded" if health == "Healthy" else "Models Degraded", "ok" if health == "Healthy" else "warn"),
            (f"Tracking {tracking}", "ok" if tracking == "Stable" else "warn"),
            (f"Lighting {lighting}", "ok" if lighting in ("Good", "Simulated") else "warn"),
            (f"Face Detection {det}", "ok" if det in ("Excellent", "Good") else "warn"),
            ("Session Recording" if running else "Not Recording", "ok" if running else "warn"),
            (f"{result.faces_present} Students Detected", "ok" if result.faces_present > 0 else "warn"),
        ]
        return cards.status_ribbon(items)

    def _pipeline_panel(self, result) -> str:
        students = result.students or []
        det = self._avg([s.box.confidence for s in students])
        eyec = self._avg([(s.eye.confidence if s.eye else None) for s in students])
        emoc = self._avg([(s.emotion.confidence if (s.emotion and s.emotion.available) else None) for s in students])
        attn = self._avg([(s.eye.attention if s.eye else s.engagement.attention) for s in students])
        engc = self._avg([s.engagement.confidence for s in students])
        running = self._session.is_running
        has = bool(students)
        stages = [
            ("camera", "Camera", "Live" if running else "Idle", running),
            ("users", "Face Detection", self._pct(det), det is not None),
            ("eye", "Eye Tracking", self._pct(eyec), eyec is not None),
            ("smile", "Emotion", self._pct(emoc) if emoc is not None else "n/a", emoc is not None),
            ("brain", "Attention", self._pct(attn), attn is not None),
            ("chart", "Engagement", self._pct(engc), engc is not None),
            ("board", "Teacher Insights", "Live" if has else "—", has),
            ("file", "Reports", "Ready" if has else "—", has),
        ]
        return cards.ai_pipeline(stages)

    def _feedstats_panel(self, result, fps: float, resolution: str, brightness, demo: bool) -> str:
        students = result.students or []
        return cards.feed_stats(fps, resolution, self._overall_conf(result),
                                "Active" if students else "Idle",
                                self._lighting_label(brightness, demo),
                                self._session.health.overall().value)

    def _record_hist(self, result) -> None:
        students = result.students or []
        att = self._avg([(s.eye.attention if s.eye else s.engagement.attention) for s in students])
        self._att_hist.append((att or 0.0) * 100)
        self._eng_hist.append(result.classroom_engagement)

    def idle_dashboard(self) -> tuple:
        """The twelve dashboard panels in their idle state."""
        empty = FrameResult()
        health = self._session.health.overall().value
        return (None,
                cards.status_ribbon([("Camera Idle", "warn"),
                                     ("AI Models Loaded" if health == "Healthy" else "Models Degraded",
                                      "ok" if health == "Healthy" else "warn"),
                                     ("Tracking Idle", "warn"), ("Lighting Unknown", "warn"),
                                     ("Face Detection Idle", "warn"), ("Not Recording", "warn"),
                                     ("0 Students Detected", "warn")]),
                cards.engagement_gauge(0, "—", None, "Waiting for a session", animate=False),
                cards.kpi_cards(empty, 0.0, "00m 00s"),
                self._pipeline_panel(empty),
                cards.student_cards(empty),
                cards.engagement_graph_svg({}),
                cards.teacher_insights_card([]),
                cards.recommendations_card([]),
                cards.ai_confidence_card(None, "Idle", "Unknown", "—", health),
                cards.feed_stats(0.0, "—", None, "Idle", "Unknown", health),
                self._topbar())

    def process_dashboard(self, rgb_frame: Any) -> tuple:
        """Process one streamed frame; return the twelve dashboard panels."""
        if rgb_frame is None or not self._session.is_running:
            return self.idle_dashboard()
        result = self._session.process_frame(rgb_frame)
        if result is None:
            return (rgb_frame, self._cached("ribbon"), self._cached("gauge"), self._cached("kpi"),
                    self._cached("pipeline"), self._cached("students"), self._cached("graph"),
                    self._cached("insights"), self._cached("recommend"), self._cached("aiconf"),
                    self._cached("feedstats"), self._topbar())
        self._last_result = result
        self._record_hist(result)
        annotated = result.annotated_frame
        annotated_rgb = annotated[:, :, ::-1] if annotated is not None else rgb_frame
        fps = self._session.performance.snapshot().fps
        try:
            h, w = rgb_frame.shape[:2]
            resolution = f"{w}×{h}"
            brightness = float(rgb_frame.mean())
        except Exception:
            resolution, brightness = "—", None
        demo = self._session.pipeline.in_demo_mode

        ribbon = self._ribbon_panel(result, brightness, demo)
        gauge = self._gauge_panel(result, animate=self._first_frame)
        self._first_frame = False
        kpi = self._kpi_panel(result, fps)
        pipeline = self._pipeline_panel(result)
        students = cards.student_cards(result)
        aiconf = self._ai_conf_panel(result, brightness, demo)
        feedstats = self._feedstats_panel(result, fps, resolution, brightness, demo)
        self._cache.update(ribbon=ribbon, gauge=gauge, kpi=kpi, pipeline=pipeline,
                           students=students, aiconf=aiconf, feedstats=feedstats)

        # Throttle the heavier panels (graph + teacher analytics) to every ~6 frames.
        self._tick += 1
        if self._tick % 6 == 0 or "graph" not in self._cache:
            self._cache["graph"] = self._graph_panel()
            self._cache["insights"], self._cache["recommend"] = self._insights_and_recs()
        return (annotated_rgb, ribbon, gauge, kpi, pipeline, students, self._cache["graph"],
                self._cache["insights"], self._cache["recommend"], aiconf, feedstats, self._topbar())

    def _cached(self, key: str) -> str:
        return self._cache.get(key, "")

    def run_demo_dashboard(self, frames: int = 36) -> tuple:
        """Run the camera-free demo and return the twelve dashboard panels + a message."""
        import time as _time
        from backend.pipeline.demo_source import DemoSource
        self._reset_live_state()
        self._session.start("Demo · Class 8B Science")
        self._session.pipeline.use_demo_source(DemoSource())
        canvas = self._demo_canvas()
        h, w = canvas.shape[:2]
        resolution = f"{w}×{h}"
        t0 = _time.time()
        last = None
        for k in range(frames):
            last = self._session.process_frame(canvas, now=t0 + k)
            if last is not None:
                self._record_hist(last)
        self._session.stop()
        self._session.pipeline.clear_demo_source()
        if last is None:
            return self.idle_dashboard() + ("⚠️ Demo could not run.",)
        self._last_result = last
        annotated = last.annotated_frame
        annotated_rgb = annotated[:, :, ::-1] if annotated is not None else canvas
        fps = self._session.performance.snapshot().fps
        insights, recommend = self._insights_and_recs()
        msg = ("✅ Demo complete — explore the populated dashboard, then the Analytics, "
               "Reports and Settings sections via the sidebar.")
        return (annotated_rgb, self._ribbon_panel(last, None, True),
                self._gauge_panel(last, animate=True), self._kpi_panel(last, fps),
                self._pipeline_panel(last), cards.student_cards(last), self._graph_panel(),
                insights, recommend, self._ai_conf_panel(last, None, demo=True),
                self._feedstats_panel(last, fps, resolution, None, True), self._topbar(), msg)

    # -- live frame ---------------------------------------------------------
    def process_frame(self, rgb_frame: Any) -> tuple[Any, str, str, str]:
        """Process one streamed frame; return (annotated_rgb, kpis, students, status)."""
        if rgb_frame is None or not self._session.is_running:
            idle = cards.kpi_row([cards.kpi_card("Status", "Idle", "start a session")])
            return rgb_frame, idle, "<div class='es-card'>No active session.</div>", self._status_html()

        result = self._session.process_frame(rgb_frame)
        if result is None:
            return rgb_frame, self._last_kpis(), self._last_students(), self._status_html()

        self._last_result = result
        annotated = result.annotated_frame
        annotated_rgb = annotated[:, :, ::-1] if annotated is not None else rgb_frame
        fps = self._session.performance.snapshot().fps
        kpis = cards.live_kpis(result, fps, self._session.elapsed_display())
        students = cards.students_panel(result)
        return annotated_rgb, kpis, students, self._status_html()

    def _last_kpis(self) -> str:
        if self._last_result is None:
            return cards.kpi_row([cards.kpi_card("Status", "—", "")])
        return cards.live_kpis(self._last_result, self._session.performance.snapshot().fps,
                               self._session.elapsed_display())

    def _last_students(self) -> str:
        if self._last_result is None:
            return "<div class='es-card'>No students detected yet.</div>"
        return cards.students_panel(self._last_result)

    def _status_html(self) -> str:
        snap = self._session.performance.snapshot()
        return cards.status_line(self._session.status.value,
                                 self._session.health.overall().value, snap.within_budget)

    # -- analytics ----------------------------------------------------------
    def engagement_figure(self) -> Any:
        return self._graphs.engagement_timeline(self._session.pipeline.classroom)

    def participation_figure(self) -> Any:
        return self._graphs.participation_timeline(self._session.pipeline.classroom)

    def emotion_figure(self) -> Any:
        return self._graphs.emotion_distribution(self._session.pipeline.classroom)

    def student_bars_figure(self) -> Any:
        return self._graphs.student_engagement_bars(self._session.pipeline.student_summaries())

    def analytics_summary(self) -> str:
        s = self._session.pipeline.session_summary()
        return (
            f"**{s.session_name}** — average {s.average_engagement}/100, "
            f"trend {s.attention_trend.value}, peak {s.peak_engagement}, "
            f"duration {s.duration_seconds}s over {s.frames_recorded} frames."
        )

    # -- insights -----------------------------------------------------------
    def student_insights_html(self) -> str:
        return cards.student_summary_cards(self._session.pipeline.student_summaries())

    def analytics_overview_html(self) -> str:
        s = self._session.pipeline.session_summary().as_dict()
        if not s.get("frames_recorded"):
            return "<div class='es-card'>Run a session or the demo to see analytics.</div>"
        return cards.report_stat_cards(s)

    def teacher_insights_html(self) -> str:
        insights = self._session.pipeline.teacher_insights()
        if not insights.observations:
            return "<div class='es-card'>No teacher insights yet. Run a session first.</div>"
        obs = "".join(f"<div class='es-remark'>{o}</div>" for o in insights.observations)
        sug = "".join(f"<li>{s}</li>" for s in insights.suggestions)
        return (
            "<div class='es-card'><b>Classroom observations</b>" + obs + "</div>"
            "<div class='es-card'><b>Constructive suggestions</b>"
            f"<ul style='margin:8px 0 0 18px;color:#A8B2C7'>{sug}</ul></div>"
            f"<div class='es-card'><b>Overall</b><br><span class='desc'>{insights.overall}</span></div>"
        )

    def teacher_dashboard_html(self) -> str:
        """Premium sectioned teacher dashboard (page) built from existing analytics."""
        ins = self._session.pipeline.teacher_insights()
        summary = self._session.pipeline.session_summary()
        if not ins.observations and summary.frames_recorded == 0:
            return "<div class='es-card'>No teacher insights yet. Run a session or the demo first.</div>"
        alerts = [o for o in ins.observations if cards._ins_kind(o)[0] == "warn"]
        if self._last_result is not None:
            need = sum(1 for s in self._last_result.students if s.engagement.prolonged_inattention)
            if need:
                alerts.append(f"{need} student{'s' if need > 1 else ''} showed prolonged inattention.")
        return cards.teacher_dashboard(ins.overall, summary.attention_trend.value,
                                       ins.observations, ins.suggestions, alerts,
                                       summary.average_engagement)

    # -- reports ------------------------------------------------------------
    def _build_report_data(self):
        return self._reports.build(
            self._session.pipeline.classroom,
            self._session.pipeline.student_summaries(),
            self._session.pipeline.teacher_insights(),
        )

    def report_preview(self) -> str:
        data = self._build_report_data()
        if not data.has_data:
            return "_No session data yet. Run a session, then return here to export._"
        return self._reports.preview_text(data)

    def generate_report(self, fmt: str) -> tuple[Optional[str], str]:
        """Generate a report in the given format; return (file_path, status)."""
        try:
            data = self._build_report_data()
            path = self._exports.export(data, fmt)
            return path, f"✅ {fmt.upper()} report ready: {path.split('/')[-1]}"
        except ExportError as exc:
            return None, f"⚠️ {exc.user_message}"
        except Exception as exc:  # noqa: BLE001
            return None, f"⚠️ Export failed: {exc}"

    @staticmethod
    def _fmt_duration(seconds: float) -> str:
        seconds = int(seconds or 0)
        return f"{seconds // 60:02d}m {seconds % 60:02d}s"

    def report_overview(self) -> tuple:
        """Return (session-statistics card, report-metadata card) for the Reports page."""
        s = self._session.pipeline.session_summary().as_dict()
        duration = (self._session.elapsed_display() if self._session.is_running
                    else self._fmt_duration(s.get("duration_seconds", 0)))
        return cards.report_stat_cards(s), cards.report_meta_card(s, duration)

    def report_files_html(self) -> str:
        """Generated files / recent reports as premium rows."""
        items = self._exports.history()
        if not items:
            return ("<div class='es-card' style='padding:16px'><div class='es-panelhead'>Generated files</div>"
                    "<div class='es-ins info'>No reports generated yet. Export one above.</div></div>")
        icons = {"pdf": "file", "xlsx": "chart", "excel": "chart", "csv": "chart"}
        rows = []
        for i in items[:8]:
            fmt = str(i.get("format", "")).lower()
            ic = icons.get(fmt, "file")
            rows.append(
                "<div class='es-filerow'>"
                f"<span class='iconbox'>{cards._icon(ic, '#6366F1', 15)}</span>"
                f"<div class='fmeta'><div class='fn'>{i['name']}</div>"
                f"<div class='fd'>{i['format']} &middot; {i['size_kb']} KB &middot; {i['modified']}</div></div>"
                "<span class='es-pill ok'><span class='d2'></span>Ready</span></div>"
            )
        return ("<div class='es-card' style='padding:16px'><div class='es-panelhead'>"
                + cards._icon("file", "#6366F1", 15) + " Generated files</div>"
                + "".join(rows) + "</div>")

    def report_history_html(self) -> str:
        items = self._exports.history()
        if not items:
            return "<div class='es-card'>No reports generated yet.</div>"
        rows = "".join(
            f"<tr><td>{i['name']}</td><td>{i['format']}</td>"
            f"<td>{i['size_kb']} KB</td><td>{i['modified']}</td></tr>"
            for i in items
        )
        return (
            "<div class='es-card'><b>Report history</b>"
            "<table style='width:100%;margin-top:8px;font-size:12px;color:#A8B2C7'>"
            "<tr style='color:#6B7693'><th align='left'>File</th><th align='left'>Format</th>"
            "<th align='left'>Size</th><th align='left'>Generated</th></tr>"
            f"{rows}</table></div>"
        )

    # -- settings -----------------------------------------------------------
    def current_settings(self) -> dict[str, Any]:
        return self._settings.current()

    def update_settings(self, changes: dict[str, Any]) -> str:
        try:
            self._settings.update(changes)
            return "✅ Settings saved."
        except ValidationError as exc:
            return f"⚠️ {exc.message}"
        except Exception as exc:  # noqa: BLE001
            return f"⚠️ Could not save settings: {exc}"

    def reset_settings(self) -> str:
        self._settings.reset()
        return "↩️ Settings reset to defaults."

    @property
    def session(self) -> SessionManager:
        return self._session
