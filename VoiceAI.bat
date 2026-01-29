@echo off
:: Voice AI Launcher - Minimizes terminal quickly
:: For completely terminal-free experience, use VoiceAI.vbs instead

title Voice AI
cd /d "%~dp0agent-starter-python"

:: Try pythonw first (no console window), fall back to pyw, then python
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw src\desktop_app.py
    exit
)

where pyw >nul 2>&1
if %errorlevel%==0 (
    start "" pyw src\desktop_app.py
    exit
)

:: Last resort - use python but start minimized
start /min "" python src\desktop_app.py
exit
