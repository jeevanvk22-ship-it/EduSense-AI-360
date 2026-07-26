"""
Session Analytics view
======================

Summary-metric cards on top, then grouped charts (trends, then distributions) with
professional legends. Charts come from the existing GraphEngine; only the layout and
the summary cards are added.
"""

from __future__ import annotations

import gradio as gr

from frontend.callbacks.handlers import DashboardController
from frontend.components import cards


def build(controller: DashboardController) -> None:
    gr.HTML(cards.hero("Session Analytics", "Trends and distributions for the current session"))
    refresh = gr.Button("Refresh analytics", variant="primary", elem_classes="es-btn")

    overview = gr.HTML("<div class='es-card'>Run a session or the demo to see analytics.</div>")

    gr.HTML("<div class='es-panelhead' style='margin-top:6px'>Engagement &amp; participation</div>")
    with gr.Row():
        engagement_plot = gr.Plot(label="Engagement timeline")
        participation_plot = gr.Plot(label="Participation")

    gr.HTML("<div class='es-panelhead' style='margin-top:6px'>Distributions</div>")
    with gr.Row():
        emotion_plot = gr.Plot(label="Emotion distribution")
        students_plot = gr.Plot(label="Per-student engagement")

    def _refresh():
        return (controller.analytics_overview_html(),
                controller.engagement_figure(),
                controller.participation_figure(),
                controller.emotion_figure(),
                controller.student_bars_figure())

    refresh.click(_refresh,
                  outputs=[overview, engagement_plot, participation_plot, emotion_plot, students_plot])
