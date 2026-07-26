"""
Teacher Insights view (sectioned dashboard)
===========================================

A premium recommendation dashboard: Class Summary, Positive Observations, Attention
Trends, Recommended Teaching Actions, Priority Alerts and a Next Suggested Action.
All sections are composed from the existing teacher-analytics output - no new logic.
"""

from __future__ import annotations

import gradio as gr

from frontend.callbacks.handlers import DashboardController
from frontend.components import cards


def build(controller: DashboardController) -> None:
    gr.HTML(cards.hero("Teacher Insights",
                       "Constructive, classroom-level analysis — describes engagement patterns, "
                       "never individual teacher performance"))
    refresh = gr.Button("Refresh insights", variant="primary", elem_classes="es-btn")
    panel = gr.HTML("<div class='es-card'>No teacher insights yet. Run a session or the demo first.</div>")
    refresh.click(controller.teacher_dashboard_html, outputs=[panel])
