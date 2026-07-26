"""
Student Insights view
=====================

Premium per-student analytics cards (status strip, sub-metrics, engagement progress
bar) built from the existing session summaries. Layout-only changes.
"""

from __future__ import annotations

import gradio as gr

from frontend.callbacks.handlers import DashboardController
from frontend.components import cards


def build(controller: DashboardController) -> None:
    gr.HTML(cards.hero("Student Insights", "Observed classroom behaviour, per student"))
    refresh = gr.Button("Refresh insights", variant="primary", elem_classes="es-btn")
    panel = gr.HTML(cards.student_summary_cards([]))
    refresh.click(controller.student_insights_html, outputs=[panel])
