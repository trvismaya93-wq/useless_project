import os
import json
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .ai_engine import AIVerificationEngine

# Load environment variables
load_dotenv()

app = FastAPI(title="WakeVerify AI Alarm Server", version="1.0.0")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
ALARMS_FILE = os.path.join(DATA_DIR, "alarms.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

ai_engine = AIVerificationEngine()

# Helpers for JSON persistence
def load_json(path: str, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Pydantic Schemas
class AlarmModel(BaseModel):
    id: Optional[str] = None
    time: str                      # "HH:MM"
    label: str                     # e.g. "Morning Workout"
    reason: str                    # e.g. "Hit the gym for deadlifts"
    dismiss_mode: str = "either"   # "reason" | "photo" | "either" | "both"
    photo_target: Optional[str] = "Running shoes"
    is_active: bool = True
    created_at: Optional[str] = None

class ReasonVerifyRequest(BaseModel):
    alarm_id: Optional[str] = None
    alarm_reason: str
    user_explanation: str

class SettingsRequest(BaseModel):
    gemini_api_key: str

# API Endpoints
@app.get("/api/status")
def get_status():
    status = ai_engine.get_status()
    alarms = load_json(ALARMS_FILE, [])
    history = load_json(HISTORY_FILE, [])
    return {
        **status,
        "alarms_count": len(alarms),
        "history_count": len(history)
    }

@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    ai_engine.set_api_key(req.gemini_api_key)
    # Save to .env in project root
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"GEMINI_API_KEY={req.gemini_api_key.strip()}\n")
    return {"success": True, "message": "API key updated successfully", "has_api_key": bool(req.gemini_api_key.strip())}

@app.get("/api/alarms")
def get_alarms():
    alarms = load_json(ALARMS_FILE, [])
    return alarms

@app.post("/api/alarms")
def create_alarm(alarm: AlarmModel):
    alarms = load_json(ALARMS_FILE, [])
    alarm.id = str(uuid.uuid4())[:8]
    alarm.created_at = datetime.now().isoformat()
    alarms.append(alarm.dict())
    save_json(ALARMS_FILE, alarms)
    return {"success": True, "alarm": alarm}

@app.delete("/api/alarms/{alarm_id}")
def delete_alarm(alarm_id: str):
    alarms = load_json(ALARMS_FILE, [])
    filtered = [a for a in alarms if a.get("id") != alarm_id]
    save_json(ALARMS_FILE, filtered)
    return {"success": True}

@app.post("/api/verify/reason")
def verify_reason(req: ReasonVerifyRequest):
    result = ai_engine.verify_reason(req.alarm_reason, req.user_explanation)
    if result.get("success"):
        # Record into history
        history = load_json(HISTORY_FILE, [])
        history.insert(0, {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "method": "Reason / Cognitive Intent",
            "alarm_reason": req.alarm_reason,
            "proof_text": req.user_explanation,
            "engine": result.get("engine", "AI Evaluator"),
            "feedback": result.get("feedback")
        })
        save_json(HISTORY_FILE, history[:50])
    return result

@app.post("/api/verify/photo")
async def verify_photo(target_description: str = Form(...), file: UploadFile = File(...)):
    contents = await file.read()
    result = ai_engine.verify_photo(target_description, contents)
    if result.get("success"):
        history = load_json(HISTORY_FILE, [])
        history.insert(0, {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "method": "Visual Proof",
            "target": target_description,
            "detected": result.get("detected"),
            "engine": result.get("engine", "Vision AI"),
            "feedback": result.get("feedback")
        })
        save_json(HISTORY_FILE, history[:50])
    return result

@app.get("/api/history")
def get_history():
    return load_json(HISTORY_FILE, [])

# Static frontend assets
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
