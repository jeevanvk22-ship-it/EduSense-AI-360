"""
EduSense AI 360 - Application Entry Point
========================================

Launches the Gradio desktop application.

Run:
    python main.py
"""

from __future__ import annotations

from core.logger import get_logger


def main() -> None:
    from frontend.app_ui import build_app
    log = get_logger("application")
    log.info("Starting EduSense AI 360 ...")
    app = build_app()
    app.launch(**getattr(app, "_es_launch_kwargs", {}))


if __name__ == "__main__":
    main()
