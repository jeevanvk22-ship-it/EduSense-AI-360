# EduSense AI 360 — Developer Guide

This guide orients a new contributor. For the full design, see the SRS under
`documentation/srs/` (Parts 1B, 2, 3, 4, 6).

## Layout
```
frontend/   Gradio presentation (views, components, callbacks, theme, app_ui)
backend/    domain logic
  camera/      capture, buffering, frame processing
  ai_models/   face / eye / emotion detectors + model registry
  analytics/   attention, engagement, student & teacher analytics
  remarks/     student/teacher rules + remarks engine
  session/     session lifecycle
  reporting/   graph, report, export engines
  pipeline/    frame (perception) + analysis (full) pipelines
  contracts/   typed data objects shared between modules
  services/    notifications, health, performance
config/     default_config.json + config & settings managers
core/       exceptions, logging, error handling
utilities/  maths, smoothing, validation, safe IO
tests/      unit / integration / system / performance
```

## Architectural rules
- **Layered, inward dependencies.** `frontend → backend → analytics/ai/reporting →
  config/core/utilities/contracts`. Lower layers never import upper ones.
- **Contract-first.** Modules exchange the typed objects in `backend/contracts/`
  (`FaceBox`, `EyeSignals`, `EmotionResult`, `EngagementResult`, `FrameResult`,
  `FrameRecord`, `SessionSummary`, …). Replace a module freely if it keeps the contract.
- **Config-driven.** All thresholds/weights live in `config/default_config.json`,
  validated by `ConfigManager`. No magic numbers in code.
- **Fail soft.** Faults are contained (`core/error_handler.py`); modules degrade to
  neutral output and report health instead of crashing.
- **Lazy heavy imports.** MediaPipe / FER / ReportLab / OpenPyXL / Plotly are imported
  inside the methods that use them, so modules import without the full stack.

## The two pipelines
- `pipeline/frame_pipeline.py` — **perception**: detect → eyes → emotion → annotate,
  emitting a `PerceptionResult`.
- `pipeline/analysis_pipeline.py` — **full analysis**: composes perception with the
  attention/engagement engines, remarks, and analytics to emit a `FrameResult` and
  feed the session time-series.

## Adding a new module (pattern)
1. Define or reuse a contract in `backend/contracts/models.py`.
2. Implement the module with a single responsibility, type hints, docstrings,
   logging, and a testing seam for any external model call.
3. Read configuration via `ConfigManager`; add validated keys to the schema if needed.
4. Compose it where appropriate (usually the analysis pipeline) — never reach across
   modules' internals.
5. Add unit tests under `tests/unit/`.

## Coding standards
PEP 8 / PEP 257, full type hints, Black + Ruff (`pyproject.toml`), composition over
inheritance, dependency injection where it aids testing. Conventional Commits and
Semantic Versioning (`VERSION`).

## Testing
The engines are testable without the CV stack via their seams (e.g. mock
`_run_detection`, `_predict`, or `_perception.process`). Run:
```bash
pytest
```
