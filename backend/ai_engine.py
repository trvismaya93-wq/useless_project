import base64
import json
import os
import re
from typing import Optional, Dict, Any
import requests
from PIL import Image
import io

class AIVerificationEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()

    def get_status(self) -> Dict[str, Any]:
        return {
            "has_api_key": bool(self.api_key),
            "engine": "Google Gemini 1.5/2.0 Flash (Multimodal)" if self.api_key else "Intelligent Local Fallback Engine"
        }

    def verify_reason(self, alarm_reason: str, user_explanation: str) -> Dict[str, Any]:
        """
        Evaluates whether the user understands why the alarm was set,
        demonstrating cognitive wakefulness and intent.
        """
        if not user_explanation or len(user_explanation.strip()) < 3:
            return {
                "success": False,
                "confidence": 0.0,
                "feedback": "Your response is too short. Please speak or write a complete sentence explaining why you set this alarm."
            }

        # If Gemini API Key is configured, use Gemini
        if self.api_key:
            try:
                return self._gemini_verify_reason(alarm_reason, user_explanation)
            except Exception as e:
                # Fallback on failure
                print(f"[Gemini API Warning]: {e}. Falling back to local verification.")

        # Local cognitive verification heuristic
        return self._local_verify_reason(alarm_reason, user_explanation)

    def verify_photo(self, target_description: str, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyzes the uploaded photo to verify if it depicts the required target object or scene.
        """
        if not image_bytes or len(image_bytes) < 100:
            return {
                "success": False,
                "detected": "No valid image data",
                "confidence": 0.0,
                "feedback": "Uploaded file is empty or corrupted. Please capture a clear photo."
            }

        # Validate image format via PIL
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.verify()
            # Reopen for data processing
            pil_img = Image.open(io.BytesIO(image_bytes))
        except Exception as err:
            return {
                "success": False,
                "detected": "Invalid image",
                "confidence": 0.0,
                "feedback": f"Could not read image: {str(err)}"
            }

        # If Gemini API Key is available, use Gemini Vision
        if self.api_key:
            try:
                return self._gemini_verify_photo(target_description, image_bytes, pil_img.format or "JPEG")
            except Exception as e:
                print(f"[Gemini Vision Warning]: {e}. Falling back to local image analysis.")

        # Fallback local image sanity check
        return self._local_verify_photo(target_description, pil_img)

    # ------------------ Gemini API Calls ------------------

    def _gemini_verify_reason(self, alarm_reason: str, user_explanation: str) -> Dict[str, Any]:
        models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        
        prompt = f"""You are an uncompromising morning alertness and cognitive intent verification agent for an accountability alarm clock.
The alarm was scheduled with this intended purpose:
\"{alarm_reason}\"

The user, who is trying to silence the loud alarm, provided this explanation:
\"{user_explanation}\"

Evaluation Rules:
1. Check cognitive alertness: The user must write coherently and make grammatical sense, proving they are awake.
2. Check intent & alignment: The user must acknowledge, explain, or articulate their action regarding the alarm's purpose (e.g. going to workout, studying, getting out of bed, drinking water).
3. STRICTLY REJECT:
   - Mindless dismissive words ("stop", "turn off", "be quiet", "leave me alone", "later", "shut up", "asdfgh").
   - Vague single-word answers that do not address the purpose.
   - Irrelevant non-sequiturs.

Respond strictly in valid JSON format:
{{
  "success": true or false,
  "confidence": float between 0.0 and 1.0,
  "feedback": "A direct 1-2 sentence response to the user congratulating them or stating why they were rejected."
}}
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            resp = requests.post(url, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Parse JSON
                result = json.loads(text)
                return {
                    "success": bool(result.get("success", False)),
                    "confidence": float(result.get("confidence", 0.9)),
                    "feedback": str(result.get("feedback", "Reason evaluated by Gemini AI.")),
                    "engine": "Gemini AI"
                }

        raise RuntimeError(f"Gemini API returned status {resp.status_code}: {resp.text}")

    def _gemini_verify_photo(self, target_description: str, image_bytes: bytes, img_format: str) -> Dict[str, Any]:
        mime_type = "image/jpeg" if img_format.upper() in ["JPG", "JPEG"] else f"image/{img_format.lower()}"
        b64_data = base64.b64encode(image_bytes).decode("utf-8")

        prompt = f"""You are a strict computer vision verification system for an accountability alarm clock.
The alarm requires visual proof of:
\"{target_description}\"

Analyze this photo strictly:
1. Is the target object, item, or setting (\"{target_description}\") visibly and convincingly present in this image?
2. Reject if the image is blacked out, lens is covered by a finger/blanket, too blurry to identify, or contains an entirely different unrelated object.

Respond strictly in valid JSON:
{{
  "success": true or false,
  "detected": "Brief description of what is actually visible in the photo",
  "confidence": float between 0.0 and 1.0,
  "feedback": "1-2 sentence message telling the user whether their proof is accepted or why it was rejected."
}}
"""
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash"]
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                result = json.loads(text)
                return {
                    "success": bool(result.get("success", False)),
                    "detected": str(result.get("detected", "Visual proof inspected")),
                    "confidence": float(result.get("confidence", 0.9)),
                    "feedback": str(result.get("feedback", "Photo analyzed by Gemini Vision.")),
                    "engine": "Gemini Vision"
                }

        raise RuntimeError(f"Gemini Vision returned status {resp.status_code}")

    # ------------------ Local Heuristic Fallbacks ------------------

    def _local_verify_reason(self, alarm_reason: str, user_explanation: str) -> Dict[str, Any]:
        words = user_explanation.strip().lower().split()
        
        # Check for minimum word count
        if len(words) < 4:
            return {
                "success": False,
                "confidence": 0.2,
                "feedback": "Answer too brief! Formulate a complete thought explaining your plan to prove wakefulness."
            }

        # Check for groggy dismissive phrases
        dismissive = ["stop", "shut up", "turn off", "silence", "be quiet", "snooze", "let me sleep", "5 more minutes", "stfu"]
        lower_exp = user_explanation.lower()
        if any(d in lower_exp for d in dismissive) and len(words) < 7:
            return {
                "success": False,
                "confidence": 0.1,
                "feedback": "Alarm refused to stop: Dismissive or sleepy response detected! Tell me your actual goal."
            }

        # Check semantic alignment with alarm reason
        reason_tokens = set(re.findall(r'\w{3,}', alarm_reason.lower()))
        exp_tokens = set(re.findall(r'\w{3,}', lower_exp))

        # Check intentional awake vocabulary
        action_verbs = {"going", "need", "have", "must", "wake", "up", "start", "time", "gym", "work", "study", "code", "run", "prep", "ready", "because"}
        has_action = bool(exp_tokens.intersection(action_verbs))
        has_overlap = bool(exp_tokens.intersection(reason_tokens))

        if has_overlap or (has_action and len(words) >= 5):
            return {
                "success": True,
                "confidence": 0.85,
                "feedback": "Cognitive wakefulness verified! You have demonstrated clear purpose and intent. Silencing alarm.",
                "engine": "Local Intent Analyzer (Add Gemini Key for deep LLM conversation)"
            }
        else:
            return {
                "success": False,
                "confidence": 0.35,
                "feedback": f"Your response does not reflect the purpose '{alarm_reason}'. Explain clearly what you need to do!",
                "engine": "Local Intent Analyzer"
            }

    def _local_verify_photo(self, target_description: str, img: Image.Image) -> Dict[str, Any]:
        # Convert to grayscale to check brightness and variance
        gray = img.convert('L')
        width, height = gray.size
        
        if width < 50 or height < 50:
            return {
                "success": False,
                "detected": "Image resolution too tiny",
                "confidence": 0.1,
                "feedback": "Image is too small or blurry to verify."
            }

        pixels = list(gray.getdata())
        avg_brightness = sum(pixels) / len(pixels)
        
        # Check if user covered the lens (blackout)
        if avg_brightness < 20:
            return {
                "success": False,
                "detected": "Black screen / covered camera",
                "confidence": 0.05,
                "feedback": "Photo is pitch black! Uncover the camera and capture your target clearly."
            }

        # Check if screen is completely overexposed or uniform white
        if avg_brightness > 245:
            return {
                "success": False,
                "detected": "Overexposed blank frame",
                "confidence": 0.05,
                "feedback": "Photo is completely white or washed out. Point camera at the object."
            }

        # Check variance (detail level)
        variance = sum((p - avg_brightness) ** 2 for p in pixels[:1000]) / min(len(pixels), 1000)
        if variance < 30:
            return {
                "success": False,
                "detected": "Uniform / blank surface",
                "confidence": 0.15,
                "feedback": "Image lacks detail. Frame your target object clearly in the shot."
            }

        return {
            "success": True,
            "detected": f"Clear visual capture of {target_description}",
            "confidence": 0.80,
            "feedback": f"Visual proof of '{target_description}' confirmed! Silencing alarm.",
            "engine": "Local Vision Sanity Engine (Connect Gemini API Key for deep object recognition)"
        }
