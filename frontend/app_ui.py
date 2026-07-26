"""
EduSense AI 360 - Application UI
================================

A professional login screen (fixed demo credentials, dark glassmorphism) gates the
approved single-page dashboard (`edusense_dashboard_mockup.html`): a left sidebar, a
topbar, and the live dashboard (engagement gauge, KPI cards, large webcam feed,
student cards, engagement graph, teacher insights, AI confidence). The sidebar
switches between the live dashboard and the Analytics, Student Insights, Teacher
Insights, Reports and Settings sections.

Custom panels are rendered as HTML/SVG (see ``components/cards.py``) so the design is
reproduced faithfully; native Gradio widgets are used only for the interactive parts
(webcam, buttons, inputs). Authentication is presentation-only - it validates against
fixed demo credentials in the frontend and never touches the backend.
"""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from config.config_manager import get_config
from core.logger import setup_logging, get_logger
from frontend.theme.theme import build_theme, CUSTOM_CSS
from frontend.callbacks.handlers import DashboardController
from frontend.components import cards
from frontend.views import (
    analytics_view, student_insights_view, teacher_insights_view,
    reports_view, settings_view,
)

log = get_logger("application")

# Fixed demo credentials (frontend-only; no backend auth, no database, no network).
TEACHER_EMAIL = "MVM.CHETPET@GMAIL.COM"
TEACHER_PASSWORD = "MVM123"
TEACHER_NAME = "MVM Chetpet"
TEACHER_CLASS = "Class 8B"


def _version(config) -> str:
    v = config.get("app.version")
    if v:
        return str(v)
    try:
        return Path(__file__).resolve().parents[1].joinpath("VERSION").read_text().strip()
    except OSError:
        return "1.0.0"


def build_app() -> "gr.Blocks":
    """Construct and return the full Gradio dashboard application."""
    config = get_config()
    setup_logging(config)
    for warning in config.warnings:
        log.warning("Config: %s", warning)

    controller = DashboardController(config)
    app_name = config.get("app.name", "EduSense AI 360")
    version = _version(config)
    idle = controller.idle_dashboard()

    # Gradio 6 moved `theme`/`css` from the Blocks constructor to launch().
    theme = build_theme()
    gradio_major = int(gr.__version__.split(".")[0])
    blocks_kwargs = {"title": app_name}
    if gradio_major < 6:
        blocks_kwargs["theme"] = theme
        blocks_kwargs["css"] = CUSTOM_CSS

    with gr.Blocks(**blocks_kwargs) as app:

        # ============================= LOGIN =============================
        with gr.Column(visible=True, elem_classes="es-login") as login_page:
            with gr.Column(elem_classes="es-logincard"):
                gr.HTML(cards.login_brand(app_name), elem_classes="es-flush")
                email_in = gr.Textbox(label="Email", placeholder="you@school.edu",
                                      interactive=True, elem_classes="es-loginfield")
                password_in = gr.Textbox(label="Password", type="password",
                                         placeholder="Your password", interactive=True,
                                         elem_classes="es-loginfield")
                with gr.Row(elem_classes="es-loginopts"):
                    show_pw = gr.Checkbox(label="Show password", value=False)
                    remember = gr.Checkbox(label="Remember me", value=True)
                signin_btn = gr.Button("Sign in", variant="primary", elem_classes="es-btn es-loginbtn")
                login_msg = gr.HTML("", elem_classes="es-flush")
                gr.HTML(cards.login_hint(TEACHER_EMAIL, TEACHER_PASSWORD), elem_classes="es-flush")

        # ============================ APP SHELL =========================
        with gr.Column(visible=False, elem_classes="es-app-shell") as app_shell:
            with gr.Row(elem_classes="es-app"):

                # ---------------- Sidebar ----------------
                with gr.Column(elem_classes="es-side"):
                    gr.HTML(cards.sidebar_brand(app_name), elem_classes="es-flush")
                    gr.HTML("<div class='es-navlabel'>Workspace</div>", elem_classes="es-flush")
                    nav_live = gr.Button("Live Monitor", elem_classes=["es-nav", "on"])
                    nav_analytics = gr.Button("Analytics", elem_classes="es-nav")
                    nav_students = gr.Button("Student Insights", elem_classes="es-nav")
                    nav_teacher = gr.Button("Teacher Insights", elem_classes="es-nav")
                    nav_reports = gr.Button("Reports", elem_classes="es-nav")
                    nav_settings = gr.Button("Settings", elem_classes="es-nav")
                    sidebar_foot = gr.HTML(cards.sidebar_profile(TEACHER_NAME, TEACHER_CLASS,
                                                                 version, "Not started"),
                                           elem_classes="es-flush")

                # ---------------- Main ----------------
                with gr.Column(elem_classes="es-main"):
                    with gr.Row(elem_classes="es-topbar"):
                        topbar_html = gr.HTML(idle[11], elem_classes="es-flush")

                    # ===== LIVE DASHBOARD =====
                    with gr.Column(visible=True, elem_classes="es-section") as sec_live:
                        ribbon_html = gr.HTML(idle[1], elem_classes="es-flush")

                        with gr.Row(elem_classes="es-controls"):
                            session_name = gr.Textbox(
                                placeholder="e.g. Class 8B – Science",
                                show_label=False, interactive=True, container=False,
                                elem_classes="es-sessioninput", scale=3)
                            start_btn = gr.Button("Start session", elem_classes="es-btn", scale=1)
                            pause_btn = gr.Button("Pause", elem_classes="es-btn-ghost", scale=1)
                            stop_btn = gr.Button("Stop & save", elem_classes="es-btn-ghost", scale=1)

                        gr.HTML(cards.demo_banner(), elem_classes="es-flush")
                        demo_btn = gr.Button("Run demo (no camera needed)", elem_classes="es-btn")
                        status_md = gr.Markdown("")

                        pipeline_html = gr.HTML(idle[4], elem_classes="es-flush")

                        with gr.Row(elem_classes="es-hero"):
                            with gr.Column(elem_classes="es-gaugecol"):
                                gauge_html = gr.HTML(idle[2], elem_classes="es-flush")
                            with gr.Column(elem_classes="es-kpicol"):
                                kpi_html = gr.HTML(idle[3], elem_classes="es-flush")

                        with gr.Row(elem_classes="es-grid2"):
                            with gr.Column(elem_classes="es-feedcol"):
                                gr.HTML("<div class='es-feedbar'><span class='t'>Classroom feed</span>"
                                        "<span class='s'>engagement overlay</span></div>",
                                        elem_classes="es-flush")
                                annotated = gr.Image(show_label=False, interactive=False,
                                                     elem_classes="es-stage", height=452)
                                feedstats_html = gr.HTML(idle[10], elem_classes="es-flush")
                                webcam = gr.Image(sources=["webcam"], streaming=True, type="numpy",
                                                  label="Camera source", elem_classes="es-source", height=120)
                            with gr.Column(elem_classes="es-studcol"):
                                students_html = gr.HTML(idle[5], elem_classes="es-flush")

                        graph_html = gr.HTML(idle[6], elem_classes="es-flush")

                        with gr.Row(elem_classes="es-grid3"):
                            teacher_html = gr.HTML(idle[7], elem_classes="es-flush")
                            recommend_html = gr.HTML(idle[8], elem_classes="es-flush")
                            aiconf_html = gr.HTML(idle[9], elem_classes="es-flush")

                    # ===== SECONDARY SECTIONS =====
                    with gr.Column(visible=False, elem_classes="es-section") as sec_analytics:
                        analytics_view.build(controller)
                    with gr.Column(visible=False, elem_classes="es-section") as sec_students:
                        student_insights_view.build(controller)
                    with gr.Column(visible=False, elem_classes="es-section") as sec_teacher:
                        teacher_insights_view.build(controller)
                    with gr.Column(visible=False, elem_classes="es-section") as sec_reports:
                        reports_view.build(controller)
                    with gr.Column(visible=False, elem_classes="es-section") as sec_settings:
                        settings_view.build(controller)

        # ---------------- Auth wiring (frontend-only) ----------------
        def _signin(email, pw, _remember):
            ok = ((email or "").strip().lower() == TEACHER_EMAIL.lower()
                  and (pw or "") == TEACHER_PASSWORD)
            if ok:
                prof = cards.sidebar_profile(TEACHER_NAME, TEACHER_CLASS, version, "Not started")
                return (gr.update(visible=False), gr.update(visible=True),
                        "<div class='es-login-ok'>✓ Signed in — opening your dashboard…</div>", prof)
            return (gr.update(), gr.update(),
                    "<div class='es-login-err'>Invalid email or password.</div>", gr.update())

        auth_out = [login_page, app_shell, login_msg, sidebar_foot]
        signin_btn.click(_signin, inputs=[email_in, password_in, remember], outputs=auth_out)
        email_in.submit(_signin, inputs=[email_in, password_in, remember], outputs=auth_out)
        password_in.submit(_signin, inputs=[email_in, password_in, remember], outputs=auth_out)
        show_pw.change(lambda s: gr.update(type="text" if s else "password"),
                       inputs=[show_pw], outputs=[password_in])

        # ---------------- Dashboard wiring ----------------
        # Order must match controller.process_dashboard / idle_dashboard return.
        dash_out = [annotated, ribbon_html, gauge_html, kpi_html, pipeline_html,
                    students_html, graph_html, teacher_html, recommend_html,
                    aiconf_html, feedstats_html, topbar_html]

        # Skip re-rendering the dashboard while idle so the webcam stream never steals
        # focus from the session-name box (and to save work when no session is running).
        def _stream(frame):
            if frame is None or not controller.is_running():
                return tuple(gr.skip() for _ in dash_out)
            return controller.process_dashboard(frame)

        webcam.stream(_stream, inputs=[webcam], outputs=dash_out,
                      stream_every=0.5, show_progress="hidden")

        def _start(name):
            msg = controller.start_session(name)
            prof = cards.sidebar_profile(TEACHER_NAME, TEACHER_CLASS, version,
                                         (name or "Live session").strip() or "Live session")
            return msg, prof

        def _stop():
            msg = controller.stop_session()
            return msg, cards.sidebar_profile(TEACHER_NAME, TEACHER_CLASS, version, "Ended")

        start_btn.click(_start, inputs=[session_name], outputs=[status_md, sidebar_foot])
        pause_btn.click(controller.pause_session, outputs=[status_md])
        stop_btn.click(_stop, outputs=[status_md, sidebar_foot])
        demo_btn.click(controller.run_demo_dashboard, outputs=dash_out + [status_md])

        sections = [sec_live, sec_analytics, sec_students, sec_teacher, sec_reports, sec_settings]

        def _show(target: int):
            return [gr.update(visible=(i == target)) for i in range(len(sections))]

        nav_live.click(lambda: _show(0), outputs=sections)
        nav_analytics.click(lambda: _show(1), outputs=sections)
        nav_students.click(lambda: _show(2), outputs=sections)
        nav_teacher.click(lambda: _show(3), outputs=sections)
        nav_reports.click(lambda: _show(4), outputs=sections)
        nav_settings.click(lambda: _show(5), outputs=sections)

    app._es_launch_kwargs = {"theme": theme, "css": CUSTOM_CSS} if gradio_major >= 6 else {}
    log.info("Gradio dashboard assembled.")
    return app
