@echo off
REM ================================================
REM Voice Model - Universal Launcher
REM This is the ONLY startup script you need
REM ================================================

title Voice AI Launcher
cd /d "%~dp0"

echo ========================================
echo   Voice AI - Starting Services
echo ========================================
echo.

REM Step 1: Check and start Ollama
echo [1/2] Checking Ollama...
curl -s -o nul -w "" http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo       Starting Ollama server...
    where ollama >nul 2>&1
    if %errorlevel%==0 (
        start /MIN "" ollama serve
        echo       Waiting for Ollama to initialize...
        timeout /t 5 /nobreak >nul
    ) else (
        echo [ERROR] Ollama not found! Please install from https://ollama.ai
        pause
        exit /b 1
    )
) else (
    echo       Ollama is already running
)

REM Step 2: Start the web interface
echo.
echo [2/2] Starting Voice AI Web Interface...
cd agent-starter-python

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

REM Start the web server
echo.
echo ========================================
echo   Voice AI is starting...
echo   Open http://localhost:5000 in browser
echo ========================================
echo.
python src/web_agent.py
