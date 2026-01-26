@echo off
title Voice AI
echo.
echo ==================================================
echo    Voice AI - Starting...
echo ==================================================
echo.

:: Change to the app directory
cd /d "%~dp0agent-starter-python"

:: Run the desktop app (native window, not browser)
python src/desktop_app.py

pause
