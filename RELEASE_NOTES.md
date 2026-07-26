# EduSense AI 360 — Release Notes

## v1.0.0

First complete release of **EduSense AI 360**, an AI-powered classroom engagement and
teaching-quality monitoring system that runs entirely in software on a laptop with a
webcam — no sensors, wearables, or IoT.

### Highlights
- **Live monitoring.** Per-student face detection with stable tracking, eye tracking
  (attention, gaze, blink, drowsiness), and facial emotion — blended into a live
  engagement score (0–100) and level.
- **Analytics.** Engagement, participation, and emotion graphs; per-student trends and
  behaviour patterns; classroom-level time-series and summaries.
- **Insights & remarks.** Supportive, explainable student remarks and constructive,
  non-evaluative teacher insights — bounded by clear ethical principles (no diagnosis,
  no identity recognition, educational use only).
- **Reports.** One-click export to PDF (with charts), Excel, and CSV, with history.
- **Settings.** Adjustable cameras, frame rate, AI thresholds, and appearance.

### Engineering
- Clean, layered, modular architecture (frontend / backend / config / core /
  utilities) with typed contracts, config-driven thresholds, lazy model loading, and
  graceful degradation throughout.
- Built and verified in seven phases; a 42-test suite (unit / integration / system /
  performance) passes.
- Full documentation set and sample reports included.

### Requirements
Python 3.12+, a webcam. CPU-first (no GPU required). See `documentation/INSTALLATION.md`.

### Run
```bash
pip install -r requirements.txt
python main.py
```

### Known limitations
- Live detection requires MediaPipe and FER (installed via `requirements.txt`); if a
  model is unavailable the app degrades gracefully (e.g. emotion → Neutral).
- The Gradio UI uses the browser webcam; the server-side camera manager supports
  device status and a capture mode but is not the primary live path in the web UI.
- Engagement readings are supportive estimates, not verdicts.
