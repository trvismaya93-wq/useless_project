@echo off
title Push WakeVerify to GitHub
cd /d "%~dp0"

echo ========================================================
echo   WakeVerify - Push Repository to GitHub
echo ========================================================
echo Target: https://github.com/trvismaya93-wq/useless_project
echo.

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py push_to_github.py %*
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" push_to_github.py %*
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python push_to_github.py %*
    goto :end
)

echo.
echo [ERROR] Python not found. Please ensure Python 3.10+ is installed.

:end
echo.
pause
