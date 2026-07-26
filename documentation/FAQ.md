# EduSense AI 360 — FAQ

**Does it need special hardware?**
No. Just a laptop and a webcam. No Arduino, Raspberry Pi, sensors, or IoT.

**Does it use facial recognition / identify students?**
No. It tracks faces only within a session to keep per-student metrics consistent. It
builds no identity database and performs no recognition.

**Does it diagnose students?**
No. It describes *observed classroom behaviour* (e.g. attention, engagement) only —
never medical or psychological conditions.

**Does it grade or rank teachers?**
No. Teacher insights analyse *classroom response* and offer constructive suggestions.
They never evaluate, rank, or blame the teacher.

**Where is my data stored?**
Locally. Sessions are saved as JSON under `data/sessions/`; reports under
`exports/reports/`. Nothing is sent to the cloud.

**Can I change how engagement is scored?**
Yes — thresholds, weights, and bands live in `config/default_config.json` and key ones
are adjustable in Settings.

**What if the emotion model isn't installed?**
The app still runs; emotion is reported as Neutral with reduced detail.

**Is there an offline mode?**
The app runs fully offline after install (the first run may download the emotion model).

**Can engagement be wrong?**
Like any AI it is an estimate. The system lowers confidence under poor conditions and
smooths over time, but readings should be treated as supportive signals, not verdicts.
