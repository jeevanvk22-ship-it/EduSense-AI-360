# EduSense AI 360 — Troubleshooting Guide

## Camera
- **No camera / black feed.** Check the browser's camera permission for the Gradio
  URL. Close other apps using the webcam. Try a different **Camera device index** in
  Settings.
- **Camera disconnected mid-session.** The app pauses analysis, shows a status, and
  attempts automatic reconnection. Reconnect the USB device; streaming resumes.

## Dependencies
- **`mediapipe` won't install.** Ensure Python 3.12 and an up-to-date `pip`
  (`python -m pip install --upgrade pip`). MediaPipe wheels are platform-specific.
- **`fer` / emotion model issues.** FER pulls TensorFlow; if it fails, the app still
  runs with emotion reported as Neutral (reduced detail). You may switch the **Emotion
  backend** to `deepface` in Settings if installed.
- **Missing libraries on startup.** The app names what's missing and disables only the
  affected features.

## Detection quality
- **Faces not detected.** Improve lighting and framing; ensure faces are reasonably
  large in frame. Lower the **detection confidence** is not exposed by default; adjust
  lighting first.
- **Attention seems wrong.** Tune **Eye-open threshold (EAR)** and **Gaze tolerance**
  in Settings. Poor lighting lowers confidence by design.
- **Too many "distracted" flags.** Raise the **Distraction threshold** or the
  **Prolonged inattention** seconds in Settings.

## Performance
- **Low FPS / high CPU.** Reduce camera resolution/FPS in Settings. The app
  frame-skips under load (latest-wins) and analyses a down-scaled frame to bound cost.
- **Memory growth.** Restart the session; sessions persist to `data/sessions/` and the
  app prunes old reports per the retention setting.

## Reports
- **Export disabled / "no data".** Run a session first; export needs recorded frames.
- **Export failed.** Check that the export location (`exports/reports/`) is writable.
  Your session data is preserved regardless.

## Logs
Detailed logs are under `logs/` (application, camera, ai, errors, performance,
session). Errors aggregate in `logs/errors/errors.log`.
