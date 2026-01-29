@echo off
cd /d "C:\Users\maxwe\ml project\fast_test_env\live_kit\agent-starter-python"
start "" ollama serve 2>nul
timeout /t 2 /nobreak >nul
python src/web_agent.py
