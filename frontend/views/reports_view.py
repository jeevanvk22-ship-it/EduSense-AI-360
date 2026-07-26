"""
Reports view (enterprise layout)
================================

Large preview card, export panel with metadata + status, session-statistics grid,
and a generated-files list. Functionality is unchanged - every button still calls
the same controller/report/export methods; only the presentation is elevated.
"""

from __future__ import annotations

import gradio as gr

from frontend.callbacks.handlers import DashboardController
from frontend.components import cards


def build(controller: DashboardController) -> None:
    gr.HTML(cards.hero("Reports",
                       "Generate a full engagement report for this session — export to PDF, Excel, or CSV"))

    load_btn = gr.Button("Load latest session data", variant="primary", elem_classes="es-btn")

    with gr.Row(elem_classes="es-grid2"):
        with gr.Column(scale=2, elem_classes="es-reportprev"):
            gr.HTML("<div class='es-panelhead'>Report preview</div>")
            preview = gr.Markdown(
                "_Run a session or the demo, then press **Load latest session data** to preview "
                "the report here._")
        with gr.Column(scale=1):
            meta = gr.HTML(cards.report_meta_card({}, "00m 00s"))
            gr.HTML("<div class='es-panelhead' style='margin-top:6px'>Export</div>")
            pdf_btn = gr.Button("Export PDF", variant="primary", elem_classes="es-btn")
            excel_btn = gr.Button("Export Excel", elem_classes="es-btn-ghost")
            csv_btn = gr.Button("Export CSV", elem_classes="es-btn-ghost")
            status = gr.Markdown("")
            download = gr.File(label="Download")

    stats = gr.HTML(cards.report_stat_cards({}))
    files = gr.HTML(controller.report_files_html())

    # ----- wiring (functionality unchanged) -----
    def _load():
        stats_html, meta_html = controller.report_overview()
        return controller.report_preview(), stats_html, meta_html, controller.report_files_html()

    load_btn.click(_load, outputs=[preview, stats, meta, files])

    def _export(fmt: str):
        path, msg = controller.generate_report(fmt)
        return path, msg, controller.report_files_html()

    pdf_btn.click(lambda: _export("pdf"), outputs=[download, status, files])
    excel_btn.click(lambda: _export("xlsx"), outputs=[download, status, files])
    csv_btn.click(lambda: _export("csv"), outputs=[download, status, files])
