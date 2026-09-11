@echo off
title WakeVerify - AI Accountability Alarm
cd /d "%~dp0"

echo ========================================================
echo   WakeVerify - AI Accountability Alarm Clock
echo ========================================================
echo Starting local server on http://127.0.0.1:8000 ...

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py run.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" run.py
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run.py
    goto :end
)

echo.
echo [ERROR] Python executable not found. Please ensure Python 3.10+ is installed.
pause

:end
