import os
import io
import sys
from PIL import Image
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app

client = TestClient(app)

def test_status_endpoint():
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "has_api_key" in data
    assert "engine" in data
    print("[PASS] Status endpoint passed:", data)

def test_alarm_crud():
    alarm_data = {
        "time": "07:30",
        "label": "Test Alarm",
        "reason": "Wake up to complete machine learning research project",
        "dismiss_mode": "either",
        "photo_target": "Desk and monitor",
        "is_active": True
    }
    resp = client.post("/api/alarms", json=alarm_data)
    assert resp.status_code == 200
    created = resp.json()
    assert created["success"] is True
    alarm_id = created["alarm"]["id"]
    print("[PASS] Alarm created:", alarm_id)

    # Get alarms
    resp = client.get("/api/alarms")
    assert resp.status_code == 200
    alarms = resp.json()
    assert any(a["id"] == alarm_id for a in alarms)
    print("[PASS] Alarm listed successfully")

    # Delete alarm
    resp = client.delete(f"/api/alarms/{alarm_id}")
    assert resp.status_code == 200
    print("[PASS] Alarm deleted successfully")

def test_reason_verification():
    alarm_reason = "Hit the gym for a heavy squat session"

    # 1. Test sleepy/dismissive response (MUST FAIL)
    groggy_resp = client.post("/api/verify/reason", json={
        "alarm_reason": alarm_reason,
        "user_explanation": "stop shut up please snooze"
    })
    assert groggy_resp.status_code == 200
    assert groggy_resp.json()["success"] is False
    print("[PASS] Groggy response correctly rejected:", groggy_resp.json()["feedback"])

    # 2. Test articulate, purposeful response (MUST PASS)
    awake_resp = client.post("/api/verify/reason", json={
        "alarm_reason": alarm_reason,
        "user_explanation": "I am awake and going to the gym right now to do my heavy squat session!"
    })
    assert awake_resp.status_code == 200
    assert awake_resp.json()["success"] is True
    print("[PASS] Awake response correctly approved:", awake_resp.json()["feedback"])

def test_photo_verification():
    target = "Running shoes"

    # 1. Pitch black image (MUST FAIL)
    black_img = Image.new("RGB", (200, 200), color=(0, 0, 0))
    black_buf = io.BytesIO()
    black_img.save(black_buf, format="JPEG")
    black_buf.seek(0)

    fail_resp = client.post(
        "/api/verify/photo",
        data={"target_description": target},
        files={"file": ("black.jpg", black_buf, "image/jpeg")}
    )
    assert fail_resp.status_code == 200
    assert fail_resp.json()["success"] is False
    print("[PASS] Blacked out photo correctly rejected:", fail_resp.json()["feedback"])

    # 2. Image with actual visual detail/gradient (MUST PASS in local heuristic)
    valid_img = Image.new("RGB", (200, 200))
    pixels = valid_img.load()
    for x in range(200):
        for y in range(200):
            pixels[x, y] = (x, y, (x + y) % 256)
    valid_buf = io.BytesIO()
    valid_img.save(valid_buf, format="JPEG")
    valid_buf.seek(0)

    pass_resp = client.post(
        "/api/verify/photo",
        data={"target_description": target},
        files={"file": ("test_shoe.jpg", valid_buf, "image/jpeg")}
    )
    assert pass_resp.status_code == 200
    assert pass_resp.json()["success"] is True
    print("[PASS] Clear photo proof correctly verified:", pass_resp.json()["feedback"])

if __name__ == "__main__":
    test_status_endpoint()
    test_alarm_crud()
    test_reason_verification()
    test_photo_verification()
    print("\n================ ALL TESTS PASSED SUCCESSFULLY ================\n")
