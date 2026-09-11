import os
import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 60)
    print(" ⏰ Starting WakeVerify - The Unstoppable AI Alarm Clock")
    print(" Web UI: http://127.0.0.1:8000")
    print(" Press CTRL+C to stop the server")
    print("=" * 60)

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run FastAPI app
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)
