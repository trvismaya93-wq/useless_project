@echo off
title WakeVerify - AI Accountability Alarm
cd /d "%~dp0"

echo ========================================================
echo   WakeVerify - AI Accountability Alarm Clock
echo ========================================================
echo Starting local server on http://127.0.0.1:8000 ...

py run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start with 'py'. Trying 'python'...
    python run.py
)

pause
