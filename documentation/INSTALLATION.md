# EduSense AI 360 — Installation Guide

## Requirements
- **Python 3.12 or later**
- A **laptop** with an **external USB webcam** (or built-in camera)
- Internet access for the one-time dependency install (and first-run model download)
- OS: **Windows** (primary), macOS, or Linux

CPU-first — **no GPU required** (a GPU, if present, can accelerate inference).

## 1. Get the project
Extract the `edusense_ai_360` folder to a location of your choice.

## 2. Create a virtual environment
```bash
cd edusense_ai_360
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```
This installs Gradio, OpenCV, MediaPipe, FER, NumPy, Pandas, Plotly, ReportLab,
OpenPyXL, and (optionally) psutil. The first run may download the emotion model
into `models/`.

> **Tip (scripts):** `scripts/install.*` and `scripts/run.*` can automate the venv
> and launch steps once populated for your platform.

## 4. Run
```bash
python main.py
```
Gradio prints a local URL (e.g. `http://127.0.0.1:7860`). Open it, grant the browser
camera permission, name your session, and press **Start session**.

## Verifying the install
On startup the application checks for required libraries and reports any that are
missing, disabling only the affected features. If the camera or a model is
unavailable, the app still launches and shows a clear status rather than crashing.

## Common install issues
See `documentation/TROUBLESHOOTING.md` for camera permissions, MediaPipe/FER install
notes, and performance tuning.
