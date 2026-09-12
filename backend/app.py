import os
import sys
import json
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Allow absolute import of sibling modules when run as a serverless function
sys.path.insert(0, os.path.dirname(__file__))
try:
    from ai_engine import AIVerificationEngine
except ImportError:
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

# Vercel serverless: only /tmp is writable at runtime.
# Locally, use the repo's data/ directory.
_IS_VERCEL = os.environ.get("VERCEL") == "1"
if _IS_VERCEL:
    DATA_DIR = "/tmp/technova_data"
else:
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

# NOTE: Static frontend files are served by Vercel's static build.
# When running locally via run.py/uvicorn, the frontend is served separately.
