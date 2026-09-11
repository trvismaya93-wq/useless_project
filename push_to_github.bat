@echo off
setlocal enabledelayedexpansion
title Push WakeVerify to GitHub
cd /d "%~dp0"

echo ========================================================
echo   WakeVerify - Push Repository to GitHub
echo ========================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Git is not found in your system PATH.
    echo Please install Git for Windows from https://git-scm.com/download/win
    echo After installing Git, re-run this script!
    pause
    exit /b 1
)

set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/wake-verify.git): "

if "%REPO_URL%"=="" (
    echo [!] Repository URL cannot be empty.
    pause
    exit /b 1
)

echo.
echo Initializing Git repository...
git init

echo Adding files to git...
git add .

echo Creating commit...
git commit -m "feat: initial commit for WakeVerify AI accountability alarm"

echo Setting branch to main...
git branch -M main

echo Adding remote origin: %REPO_URL%
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%

echo Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! WakeVerify has been pushed to GitHub!
    echo ========================================================
) else (
    echo.
    echo [!] Push encountered an error. Please check your repo URL and permissions.
)

pause
