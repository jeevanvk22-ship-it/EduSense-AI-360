"""
EduSense AI 360 - Settings View
===============================

Grouped settings cards (appearance & camera, AI thresholds) with section headers and
short descriptions. Values validate on save through the Settings Manager; invalid
values are rejected with a clear message and the prior value retained. Components and
wiring are unchanged - this is a layout/presentation pass.
"""

from __future__ import annotations

import gradio as gr

from frontend.callbacks.handlers import DashboardController
from frontend.components import cards


def _section(title: str, icon: str, color: str, desc: str) -> str:
    return ("<div class='es-setcard-h'>" + cards._icon(icon, color, 16)
            + f"<div><div class='st'>{title}</div><div class='sd'>{desc}</div></div></div>")


def build(controller: DashboardController) -> None:
    cfg = controller.current_settings()
    gr.HTML(cards.hero("Settings", "Tune cameras, thresholds, and appearance"))

    with gr.Row(elem_classes="es-grid2"):
        with gr.Column(elem_classes="es-setcard"):
            gr.HTML(_section("Appearance & Camera", "camera", "#22D3EE",
                             "How the dashboard looks and where it reads video from."))
            theme = gr.Dropdown(["dark", "light", "system"], label="Theme",
                                value=cfg.get("dashboard", {}).get("theme", "dark"))
            device = gr.Number(label="Camera device index",
                               value=cfg.get("camera", {}).get("device_index", 0), precision=0)
            fps = gr.Slider(1, 60, step=1, label="Camera FPS",
                            value=cfg.get("camera", {}).get("fps", 30))
            backend = gr.Dropdown(["fer", "deepface"], label="Emotion backend",
                                  value=cfg.get("emotion", {}).get("backend", "fer"))
            gr.HTML("<div class='es-sethint'>Tip: set the emotion backend weight to 0 in attention-only "
                    "rooms, or when running without the FER model.</div>")
        with gr.Column(elem_classes="es-setcard"):
            gr.HTML(_section("AI Thresholds", "target", "#A78BFA",
                             "Tuning for how strictly attention and engagement are scored."))
            ear = gr.Slider(0.05, 0.5, step=0.01, label="Eye-open threshold (EAR)",
                            value=cfg.get("eye_tracking", {}).get("ear_open_threshold", 0.18))
            gaze = gr.Slider(0.05, 1.0, step=0.01, label="Gaze tolerance",
                             value=cfg.get("eye_tracking", {}).get("gaze_center_tolerance", 0.22))
            distraction = gr.Slider(0, 100, step=1, label="Distraction threshold (score)",
                                    value=cfg.get("engagement", {}).get("distraction_threshold", 31))
            prolonged = gr.Slider(1, 120, step=1, label="Prolonged inattention (seconds)",
                                  value=cfg.get("engagement", {}).get("prolonged_inattention_seconds", 10))
            gr.HTML("<div class='es-sethint'>These affect future sessions only and never alter past "
                    "recordings or generated reports.</div>")

    with gr.Row():
        save_btn = gr.Button("Save settings", variant="primary", elem_classes="es-btn")
        reset_btn = gr.Button("Reset to defaults", elem_classes="es-btn-ghost")
    status = gr.Markdown("")

    def _save(theme, device, fps, backend, ear, gaze, distraction, prolonged):
        changes = {
            "dashboard.theme": theme,
            "camera.device_index": int(device),
            "camera.fps": int(fps),
            "emotion.backend": backend,
            "eye_tracking.ear_open_threshold": float(ear),
            "eye_tracking.gaze_center_tolerance": float(gaze),
            "engagement.distraction_threshold": float(distraction),
            "engagement.prolonged_inattention_seconds": float(prolonged),
        }
        return controller.update_settings(changes)

    save_btn.click(_save,
                   inputs=[theme, device, fps, backend, ear, gaze, distraction, prolonged],
                   outputs=[status])
    reset_btn.click(controller.reset_settings, outputs=[status])
