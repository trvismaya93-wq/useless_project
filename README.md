# ⏰ WakeVerify — Aggressive Accountability Alarm Clock

> **The AI-Enforced Accountability Alarm Clock that refuses to silence until it understands why you woke up or verifies visual proof of your goal.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-1.5_%2F_2.0_Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.28+-499848?style=for-the-badge&logo=gunicorn&logoColor=white)](https://www.uvicorn.org)
[![Web Audio API](https://img.shields.io/badge/Web_Audio_API-Synthesized_Siren-FF5722?style=for-the-badge)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 💡 The Problem

Standard alarms are too easy to snooze or dismiss while half-asleep. You swat your phone screen unconsciously, drift back to sleep, and wake up hours later filled with regret. Physical puzzle alarms or math challenges often become muscle memory or get bypassed by powering off the device.

## 🚀 The Solution: WakeVerify

**WakeVerify** is an inescapable, smart accountability alarm system. When an alarm triggers, it activates an urgent, frequency-modulated dual-oscillator siren loop that **cannot be silenced with a simple dismiss button**.

To silence the siren, you must satisfy multimodal AI challenges that prove you are genuinely awake and actively moving toward your morning goal.

```
+-------------------------------------------------------------------------+
|                         WakeVerify Architecture                         |
+-------------------------------------------------------------------------+
|                                                                         |
|   +-----------------------------------------------------------------+   |
|   |                  Frontend Web UI (Browser)                      |   |
|   |   - Live Digital Clock & Next Alarm Countdown                   |   |
|   |   - Web Audio Dual-Oscillator Siren (Synthesized in Real-time)  |   |
|   |   - HTML5 Camera Viewfinder (getUserMedia & Snapshot)           |   |
|   |   - Web Speech API Microphone Listener                          |   |
|   |   - Wakeup Streak & Audit Log Feed                              |   |
|   +--------------------------------+--------------------------------+   |
|                                    | HTTP / REST                        |
|                                    v                                    |
|   +--------------------------------+--------------------------------+   |
|   |               FastAPI Server (Unified Host :8000)               |   |
|   |   - /api/alarms        : Schedule & Manage Alarms               |   |
|   |   - /api/verify/reason : Cognitive Wakefulness Analysis         |   |
|   |   - /api/verify/photo  : Computer Vision Proof Inspection       |   |
|   |   - /api/history       : Wakeup Consistency Audit Log           |   |
|   |   - Static Hosting     : Serves frontend assets                 |   |
|   +--------------------------------+--------------------------------+   |
|                                    |                                    |
|         +--------------------------+--------------------------+         |
|         v                                                     v         |
|   +--------------------------+          +---------------------------+   |
|   | Google Gemini Multimodal |          | Intelligent Local Fallback|   |
|   | (gemini-1.5 / 2.0-flash) |          | (Heuristic NLP & Vision)  |   |
|   +--------------------------+          +---------------------------+   |
+-------------------------------------------------------------------------+
```

---

## 🎯 Dismissal Modes & Verification Challenges

| Challenge Mode | How It Works | Acceptance Criteria | Rejection Criteria |
| :--- | :--- | :--- | :--- |
| **🧠 Reason & Cognitive Intent** | Speak or type your reason for waking up and your immediate morning plan. | Articulate, purposeful explanations aligning with the goal (e.g., *"I'm going to the gym for leg day"*). | Sleepy gibberish, dismissive slang (*"shut up"*, *"let me sleep"*, *"snooze"*). |
| **📸 Visual Photo Proof** | Capture or upload a photo of your pre-set target location or object. | High visual clarity displaying the designated target (e.g., bathroom sink, running shoes, study desk). | Pitch-black images, covered lenses, fingers over the camera, or blank walls. |
| **⚡ Either Mode** | Complete either the cognitive reason check OR submit visual photo proof. | Passing either challenge silences the siren. | Neither challenge satisfies the AI threshold. |
| **🔒 Hardcore Mode** | For heavy sleepers who require total discipline. | **Both** cognitive reasoning AND visual photo proof must pass AI verification. | Siren continues ringing if either step is incomplete. |

---

## ✨ Key Features

- 🔊 **Web Audio FM Siren Engine** — Custom dual-oscillator synthesizer (sawtooth + square wave frequency modulation) running entirely in the browser. Impervious to missing audio files or network drops.
- 🤖 **Multimodal Dual-Engine AI**:
  - **Google Gemini Flash** — Ultra-fast vision & text inference for deep contextual understanding.
  - **Intelligent Local Fallback** — Works immediately offline without requiring an API key.
- 🎙️ **Hands-Free Speech Recognition** — Speak your intentions directly into your microphone via the browser's native Web Speech API.
- 📷 **Live Camera Integration** — Instant viewfinder with single-tap snapshot capturing and file upload fallback.
- ⚡ **Instant Interlock Test Mode** — Test the emergency ringing modal and siren at any time with the **"⚡ Ring Alarm Now"** button.
- 🛡️ **Conflict-Free Auto-Launcher** — `run.py` automatically detects active sessions on port 8000 and opens the running browser instance without socket collisions (`Errno 10048`).
- 📈 **Audit Trail & Streak Counter** — Keeps a local record of wakeup timestamps, verification methods, and AI confidence logs.

---

## 📂 Project Structure

```
Agrassive-clock/
├── .vscode/
│   └── settings.json         # Workspace Python interpreter configuration
├── backend/
│   ├── __init__.py
│   ├── app.py                # FastAPI REST API & static asset server
│   └── ai_engine.py          # Multimodal Gemini & heuristic verification engine
├── frontend/
│   ├── index.html            # Dark-mode dashboard, modal interlock & controls
│   ├── app.js                # Siren synthesizer, camera, speech & scheduler logic
│   └── styles.css            # Glassmorphism, pulse animations & strobe effects
├── data/
│   ├── alarms.json           # Scheduled alarms persistence
│   └── history.json          # Wakeup audit log history
├── tests/
│   └── test_verification.py  # End-to-end automated API test suite
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules for Python & data
├── push_to_github.bat        # Automated one-click GitHub deployment script
├── push_to_github.py         # Python-based GitHub push automation
├── README.md                 # Complete project documentation
├── requirements.txt          # Python package dependencies
├── run.bat                   # Resilient one-click Windows launcher
└── run.py                    # Python launcher with port checks & browser launch
```

---

## 🚀 Quickstart Guide

### Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- A modern web browser (Google Chrome, Microsoft Edge, Brave, or Firefox)

### 1. Clone the Repository

```bash
git clone https://github.com/trvismaya93-wq/Agrassive-clock.git
cd Agrassive-clock
```

### 2. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

This installs:

| Package | Version | Purpose |
| :--- | :--- | :--- |
| `fastapi` | ≥ 0.110.0 | REST API framework |
| `uvicorn` | ≥ 0.28.0 | ASGI web server |
| `pydantic` | ≥ 2.6.0 | Data validation |
| `python-multipart` | ≥ 0.0.9 | File upload handling |
| `python-dotenv` | ≥ 1.0.1 | `.env` configuration |
| `requests` | ≥ 2.31.0 | HTTP client |
| `pillow` | ≥ 10.0.0 | Image processing |

### 3. Launch the Application

#### Option A: Windows One-Click (Recommended)

Double-click **`run.bat`**. It automatically selects the active Python 3.10 environment, verifies port availability, and launches the application.

#### Option B: Terminal / PowerShell

```bash
py run.py
```

The server will start at **`http://127.0.0.1:8000`** and automatically open your default browser.

---

## 🔑 AI Configuration (Optional)

WakeVerify works fully offline out of the box using its built-in heuristic cognitive and visual engines.

To enable **Google Gemini 1.5 / 2.0 Flash** for enhanced AI accuracy:

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Alternatively, click the **Settings ⚙️** button in the top navigation bar of the web app and paste your key directly — no restart required.

---

## 📡 REST API Reference

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description | Payload / Parameters | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/status` | System health & active AI engine | None | `{"has_api_key": bool, "engine": str, "alarms_count": int}` |
| `GET` | `/api/alarms` | List all scheduled alarms | None | `[{"id": "...", "time": "07:00", "label": "...", ...}]` |
| `POST` | `/api/alarms` | Create a new scheduled alarm | JSON `AlarmModel` | `{"success": true, "alarm": {...}}` |
| `DELETE` | `/api/alarms/{id}` | Delete a scheduled alarm by ID | URL path `id` | `{"success": true}` |
| `POST` | `/api/verify/reason` | Verify cognitive wakefulness via text/speech | `{"alarm_reason": "...", "user_explanation": "..."}` | `{"success": bool, "feedback": str, "score": int}` |
| `POST` | `/api/verify/photo` | Verify target visual proof via image | Multipart `file` (image) + `target_description` (text) | `{"success": bool, "feedback": str, "engine": str}` |
| `GET` | `/api/history` | Retrieve full wakeup audit trail | None | `[{"id": "...", "timestamp": "...", "method": "..."}]` |

---

## 🧪 Automated Testing

Run the included test suite to verify endpoints, validation rules, and heuristic sanity checks:

```bash
py tests/test_verification.py
```

### Test Coverage

- ✅ **API Health** — Status checks and engine identification.
- ✅ **Alarm CRUD** — Create, read, and delete operations with JSON persistence.
- ✅ **Reason Challenge** — Rejects dismissive input (*"stop please snooze"*) and approves clear wakefulness explanations.
- ✅ **Photo Proof Challenge** — Detects and rejects blacked-out frames; accepts clear visual targets.

---

## 📤 Publishing to GitHub

You can push updates to GitHub in seconds:

1. Ensure you have an existing remote or create a new repo at [github.com/new](https://github.com/new).
2. Double-click **`push_to_github.bat`** and paste your repository URL when prompted:
   ```text
   Enter your GitHub Repository URL: https://github.com/trvismaya93-wq/Agrassive-clock.git
   ```
3. The script initializes Git, stages all files, commits, and pushes to `main`.

Or use the Python script directly:

```bash
py push_to_github.py
```

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Audio doesn't play automatically** | Modern browsers require a user interaction before playing audio. Click anywhere on the dashboard or use the **"Test Sound"** button to grant audio permissions. |
| **Port 8000 already in use** | `run.py` has a built-in port conflict guard. If the server is already active, it will safely open your active browser session instead of crashing with `Errno 10048`. |
| **Microphone / Camera not working** | Go to your browser's site permissions for `http://127.0.0.1:8000` and allow **Camera** and **Microphone** access. |
| **Gemini API key not detected** | Ensure your `.env` file is in the **project root** (same directory as `run.py`) and the key is named exactly `GEMINI_API_KEY`. |
| **`pip install` fails** | Try `py -m pip install --upgrade pip` first, then re-run `py -m pip install -r requirements.txt`. |

---

## 📄 License

Distributed under the **MIT License**. Created for heavy sleepers, students, and professionals striving for morning discipline.

---

<div align="center">
  Made with 🔥 by <a href="https://github.com/trvismaya93-wq">trvismaya93-wq</a>
</div>
