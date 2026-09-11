# ⏰ WakeVerify (ProofAlarm)

> **The AI-Enforced Accountability Alarm Clock that refuses to silence until it understands why you woke up or verifies visual proof of your goal.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_/_2.0_Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![Web Audio API](https://img.shields.io/badge/Web_Audio_API-Synthesized_Siren-FF5722?style=for-the-badge)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 💡 The Problem

Standard alarms are too easy to snooze or dismiss half-asleep. You turn off the alarm unconsciously, drift back to sleep, and wake up hours later filled with regret.

## 🚀 The Solution: WakeVerify

**WakeVerify** is an inescapable, smart accountability alarm system. When it rings, it triggers an irritating, pulsating Web Audio siren loop that **cannot be silenced normally**.

To silence the alarm, you must satisfy one (or both) of two AI challenges:

1. **🧠 Reason & Cognitive Intent Verification**:
   - You must speak or write explaining **why** you scheduled this alarm and what your immediate plan is.
   - An LLM (powered by Google Gemini Flash or the built-in local cognitive analyzer) assesses your cognitive wakefulness. If you provide groggy gibberish (*"stop", "shut up", "let me sleep"*), the alarm **refuses to stop and continues ringing**.
2. **📸 Visual Photo Proof Verification**:
   - You must capture or upload a live photo of a designated object or location (e.g. *gym shoes, bathroom sink with toothbrush, kitchen coffee maker, study desk with open book*).
   - Computer Vision (Gemini Vision or local image sanity analyzer) inspects the frame to verify the object is present, rejecting blacked-out screens or blankets over the lens.
3. **🔒 Hardcore Mode**:
   - For heavy sleepers: enforces passing **BOTH** Reason understanding AND Visual Photo Proof before granting dismissal!

---

## ✨ Key Features

- 🔊 **Unstoppable Dual-Oscillator Siren**: Synthesized directly via browser Web Audio API—impervious to network disconnects or missing media files.
- 🤖 **Multimodal AI Verification Engine**:
  - Google Gemini 1.5/2.0 Flash for lightning-fast multimodal reasoning.
  - Intelligent offline heuristic analyzer that allows immediate testing without an external API key.
- 🎙️ **Voice & Speech Recognition**: Speak your reason directly to your device via the Web Speech API.
- 📷 **Live Camera Snapshot & File Picker**: Integrated camera viewfinder with instant frame capture.
- ⚡ **Instant Test Mode**: "⚡ Ring Alarm Now" button to simulate and test the alarm interlock immediately.
- 📈 **Wake-up Audit Log & Consistency Stats**: Tracks timestamps, proof methods, and AI confidence logs.

---

## 🛠️ Project Structure

```
wake-verify/
├── backend/
│   ├── __init__.py
│   ├── app.py            # FastAPI REST & Static server
│   └── ai_engine.py      # Gemini Vision & Cognitive reason verification
├── frontend/
│   ├── index.html        # Modern dark-mode UI
│   ├── app.js            # Web Audio siren, camera, & scheduler
│   └── styles.css        # Animations & siren strobe effects
├── data/                 # JSON persistence for alarms & history
├── run.py                # Python auto-launcher with browser opening
├── run.bat               # One-click Windows launch script
├── push_to_github.bat    # Automated GitHub publish script
├── requirements.txt      # Python dependencies
└── .env.example          # Environment configuration
```

---

## 🏁 Quickstart

### 1. Prerequisites
- Python 3.10 or newer.

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/<your-username>/wake-verify.git
cd wake-verify
pip install -r requirements.txt
```

### 3. Run the Application
On Windows, simply double-click **`run.bat`**, or run:
```bash
python run.py
```
This starts the local server and automatically opens `http://127.0.0.1:8000` in your web browser.

---

## 🔑 AI Configuration (Optional)

WakeVerify works immediately out of the box with built-in heuristic verification. For state-of-the-art vision and conversational reasoning:

1. Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Click **Settings** in the WakeVerify top navigation bar and paste your key, or add it to `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 📤 Pushing to GitHub

To push your repository to GitHub:
1. Create a new repository on [GitHub](https://github.com/new).
2. Double-click `push_to_github.bat` and paste your repository URL, or run:
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit for WakeVerify AI accountability alarm"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

---

## 📜 License
MIT License. Created with ❤️ for heavy sleepers and high achievers.
