@echo off
:: Voice AI Backend - One-Click Start Script
:: Run this to start the backend server

title Voice AI Backend Server
cd /d "%~dp0"

echo ========================================
echo   Voice AI - Backend Server
echo ========================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Check if requirements installed
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    echo [2/4] Installing dependencies...
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: Check Ollama
echo [3/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama...
    start /MIN "" ollama serve
    timeout /t 5 /nobreak >nul
)

:: Start server
echo [4/4] Starting backend server...
echo.
echo ========================================
echo   Server starting on http://0.0.0.0:5000
echo   Press Ctrl+C to stop
echo ========================================
echo.

python src/web_agent.py
