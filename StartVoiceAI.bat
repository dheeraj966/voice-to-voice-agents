@echo off
:: Voice AI Complete Launcher
:: This script ensures Ollama is running before starting Voice AI

title Voice AI Launcher
cd /d "%~dp0"

echo ================================================
echo   Voice AI - Starting Services
echo ================================================
echo.

:: Check if Ollama is running
echo Checking if Ollama is running...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama is already running
) else (
    echo [..] Starting Ollama server...
    start "" /MIN ollama serve
    :: Wait a moment for Ollama to start
    timeout /t 3 /nobreak >nul
    echo [OK] Ollama started
)

echo.
echo Starting Voice AI...

:: Use VBS for completely windowless operation
if exist "VoiceAI.vbs" (
    cscript //nologo VoiceAI.vbs
) else if exist "agent-starter-python\dist\VoiceAI.exe" (
    start "" "agent-starter-python\dist\VoiceAI.exe"
) else (
    echo Error: Could not find VoiceAI.vbs or VoiceAI.exe
    pause
    exit /b 1
)

:: This window will close automatically
exit
