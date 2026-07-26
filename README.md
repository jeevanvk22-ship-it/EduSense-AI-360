# EduSense AI 360

**AI-Powered Smart Classroom Engagement & Teaching Quality Monitoring System**

A fully software-based platform that monitors classroom engagement from a live
webcam feed using computer vision and deep learning — no sensors, wearables, or
IoT hardware. Just a laptop and a webcam.

> **Status: v1.0.0 — complete.** All 7 build phases done and verified; a 42-test
> suite (unit/integration/system/performance) passes. Runnable via `python main.py`.

---

## What it does

For each student in frame it detects faces, tracks eye movement and gaze, reads
facial emotion, and blends these into a live **engagement score (0–100)** mapped to
a level (Poor / Average / Good / Excellent). From the per-student scores it derives
classroom analytics, flags prolonged inattention, generates supportive student and
teacher remarks, draws live trend graphs, and exports PDF / Excel / CSV reports.

> Teacher analytics describe classroom *engagement patterns* and never evaluate the
> teacher.

---

## Project structure (Part 4 target)

```
edusense_ai_360/
├── main.py                     # ✅ entry point (python main.py)
├── requirements.txt · VERSION · LICENSE · CHANGELOG.md · pyproject.toml
│
├── frontend/                   # Gradio presentation layer
│   ├── ✅ views/ · components/ · callbacks/ · theme/ · app_ui.py
│
├── backend/                    # domain logic
│   ├── pipeline/               # ✅ perception orchestrator (frame_pipeline)
│   ├── camera/                 # ✅ capture, buffering, frame processing, recovery
│   ├── ai_models/              # ✅ face / eye / emotion + model registry
│   ├── analytics/              # ✅ engagement, attention, student, teacher
│   ├── remarks/                # ✅ student + teacher remarks engine
│   ├── session/                # ✅ session lifecycle, timer, persistence
│   ├── reporting/              # ✅ graph + report + export engines (PDF/Excel/CSV)
│   ├── contracts/              # ✅ typed data contracts (+ FrameQuality)
│   └── services/               # ✅ notifications, health, performance
│
├── config/                     # ✅ default_config.json + config & settings managers
├── core/                       # ✅ exceptions · logger · error_handler
├── utilities/                  # ✅ maths · smoothing · validation · safe IO
│
├── assets/  (icons·fonts·themes·images)   models/   data/   exports/   logs/
├── documentation/srs/          # ✅ full SRS (Parts 1B–4)
├── ✅ tests/  (unit·integration·system·performance — 42 passing)
├── ✅ scripts/ (install·run·package) · ✅ samples/ (PDF·Excel·CSV)
```
✅ = implemented in Phase 1.

---

## Configuration

All tunable behaviour lives in `config/default_config.json` and is served through
`ConfigManager` (dot-path access, schema validation, env-var overrides, automatic
engagement-weight normalisation). User changes are handled by `SettingsManager`
(validate → persist to `config/user_config.json` → reset / import / export), never
touching the shipped defaults.

---

## Documentation

The formal Software Requirement Specification lives in `documentation/srs/`:
- **Part 1B — Functional Requirements** — all 16 modules with traceable IDs (`FR-XX-NNN`).
- **Part 2 — UI/UX Design Specification** — full design-token system, layout, components.
- **Part 3 — AI & Backend Architecture** — layers, contracts, pipelines, engines.
- **Part 4 — Development Blueprint** — structure, standards, testing, packaging.
- **Part 6 — AI Decision Logic & Intelligence** — how the AI reasons: attention,
  emotion, engagement, distraction, session, insight, remarks, alert, trend, and
  confidence engines, plus decision priority, false-positive reduction, and ethics.

---

## Setup (once the build completes)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Tech stack:** Python 3.12 · Gradio · OpenCV · MediaPipe · FER/DeepFace ·
NumPy/Pandas · Plotly · ReportLab/OpenPyXL · JSON config · Python logging
