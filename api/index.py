"""
Vercel entrypoint — re-exports the FastAPI app from backend/app.py.
Vercel's @vercel/python builder looks for `app` in api/index.py by default.
"""
import sys
import os

# Make sure backend/ is importable as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import app  # noqa: F401  — 'app' is what Vercel needs
