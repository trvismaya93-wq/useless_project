import os
import sys
import webbrowser
import threading
import time
import uvicorn

import socket

def is_port_in_use(port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print(" [WakeVerify] Starting WakeVerify - The Unstoppable AI Alarm Clock")
    print(" Web UI: http://127.0.0.1:8000")
    print(" Press CTRL+C to stop the server")
    print("=" * 60)

    # Check if port is already running
    if is_port_in_use(8000):
        print("\n[INFO] WakeVerify is already running on http://127.0.0.1:8000!")
        print("Opening browser to your active session...")
        webbrowser.open("http://127.0.0.1:8000")
        sys.exit(0)

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run FastAPI app
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)

