<p align="center">
  <img src="banner.png" width="100%">
</p>

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)

![Gradio](https://img.shields.io/badge/Gradio-Latest-orange)

![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)

![MediaPipe](https://img.shields.io/badge/MediaPipe-AI-purple)

![License](https://img.shields.io/badge/License-MIT-red)

# 🎓 EduSense AI 360

> **AI-Powered Classroom Engagement & Teaching Quality Monitoring System using Computer Vision, Deep Learning and Real-Time Analytics**

---

## 🌟 Overview

EduSense AI 360 is an intelligent classroom analytics platform that leverages Artificial Intelligence and Computer Vision to help educators understand classroom engagement in real time.

The system analyzes classroom activity through a live camera feed and generates meaningful insights such as student engagement, attention trends, AI confidence scores, session analytics, and teacher recommendations.

Instead of evaluating individual students, EduSense AI 360 focuses on overall classroom learning patterns, helping teachers improve teaching effectiveness through data-driven insights.

---

# ✨ Key Features

- 🎥 Live Classroom Monitoring
- 😊 Emotion Detection
- 👀 Eye Tracking
- 🧠 Classroom Engagement Analysis
- 📊 Real-Time Analytics Dashboard
- 📈 Engagement Trend Graphs
- 📉 Analytics Visualization
- 👨‍🏫 AI Teacher Insights
- 📄 Automated Session Reports
- 📦 Exportable Reports
- ⚡ Fast Interactive Dashboard
- 🔒 Privacy-Focused Classroom Analytics

---

# 📸 Screenshots

## Dashboard

![Dashboard](screenshots/dashboard.png)

---

## Live Detection

![Live Detection](screenshots/live%20detection.png)

---

## Live Tracking

![Live Tracking](screenshots/live%20tracking.png)

---

## Analytics Dashboard

![Analytics](screenshots/analytics.png)

---

## Engagement Graph

![Engagement Graph](screenshots/engagement%20graph.png)

---

## Analytics Graph

![Analytics Graph](screenshots/analytics%20graph.png)

---

## Teacher Insights

![Teacher Insights](screenshots/Teacher%20insights.png)

---

## AI Confidence

![AI Confidence](screenshots/AI%20confidence%20.png)

---

## Session Reports

### Report 1

![Session Report](screenshots/session%20report%201.png)

### Report 2

![Session Report](screenshots/session%20report%202.png)

---

# 🏗️ System Architecture

```
Camera
    │
    ▼
OpenCV
    │
    ▼
MediaPipe
    │
    ▼
AI Processing Engine
    ├── Face Detection
    ├── Eye Tracking
    ├── Emotion Detection
    ├── Engagement Analysis
    └── Attention Analysis
            │
            ▼
Analytics Engine
            │
            ▼
Dashboard & Reports
```

---

# ⚙️ Technology Stack

| Category | Technology |
|----------|------------|
| Programming Language | Python 3.12+ |
| User Interface | Gradio |
| Computer Vision | OpenCV |
| AI Framework | MediaPipe |
| Emotion Detection | FER (Facial Emotion Recognition) |
| Data Processing | NumPy, Pandas |
| Interactive Charts | Plotly |
| Report Generation | ReportLab, OpenPyXL |
| Performance Monitoring | psutil |
| Project Structure | Modular Python Architecture |

---

## 📂 Project Structure

```text
EduSense-AI-360/
│
├── main.py                 # Main application
├── backend/                # AI processing modules
├── frontend/               # User interface
├── core/                   # Core logic
├── config/                 # Configuration files
├── models/                 # AI models
├── assets/                 # Images & icons
├── samples/                # Sample videos/images
├── documentation/          # Project documentation
├── tests/                  # Testing utilities
├── utilities/              # Helper functions
├── requirements.txt
└── README.md
---

---
# 🚀 Installation

```bash
git clone https://github.com/jeevanvk22-ship-it/EduSense-AI-360.git
```

```bash
cd EduSense-AI-360
```

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

---
## 🧠 System Workflow

```text
Camera Input
      │
      ▼
Frame Capture (OpenCV)
      │
      ▼
Face & Pose Detection (MediaPipe)
      │
      ▼
AI Engagement Analysis
      │
      ├───────────────┐
      ▼               ▼
Emotion Score     Attention Score
      │               │
      └──────┬────────┘
             ▼
 Engagement Calculation
             │
             ▼
Teacher Insights Engine
             │
             ▼
Dashboard + PDF Report

---
## ⚙️ AI Processing Pipeline

1. Capture live video.
2. Detect students using Computer Vision.
3. Estimate face and body landmarks.
4. Analyze engagement indicators.
5. Calculate engagement score.
6. Generate teacher recommendations.
7. Display analytics dashboard.
8. Export session report.
---
## 📊 Performance Metrics

- Real-Time Processing
- Live Engagement Score
- Teacher Confidence Indicator
- Emotion Analysis
- Attention Detection
- Automated PDF Reports
- Interactive Dashboard
---
# 🚀 Future Roadmap

- Mobile Application
- Cloud Dashboard
- Multi-Camera Classroom Support
- Attendance Integration
- AI Lesson Recommendations
- Advanced Classroom Heatmaps
- Multi-Language Support
- School-Wide Analytics

---

# 🎯 Applications

- Schools
- Colleges
- Smart Classrooms
- Educational Institutions
- Teacher Training
- Academic Research
---

## 🌍 Impact

EduSense AI 360 helps educational institutions improve classroom learning through AI-powered analytics.

### Benefits

- Improves student engagement
- Assists teachers with data-driven insights
- Enables personalized teaching strategies
- Saves teachers' time with automated reports
- Supports smarter classroom management

---

# 👨‍💻 Developer

**JEEVAN V K**

Student Entrepreneur | AI Developer | Building AI Solutions for Education

---

# 📄 License

This project is licensed under the **MIT License**.

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

---

> **EduSense AI 360 — Transforming Classrooms with Artificial Intelligence**
