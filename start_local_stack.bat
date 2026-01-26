@echo off
REM ================================================
REM Local LiveKit Stack Startup Script for Windows
REM ================================================

echo ==========================================
echo Starting Local LiveKit Stack
echo ==========================================
echo.

REM Check if Ollama is running
echo [1/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo Ollama is already running
)

REM Start LiveKit Server via Docker
echo.
echo [2/4] Starting LiveKit Server (Docker)...
cd /d "%~dp0"
docker-compose up -d livekit
timeout /t 3 /nobreak >nul

REM Start STT Server
echo.
echo [3/4] Starting STT Server (Faster-Whisper)...
start "STT Server" cmd /c "python local_services\stt_server.py"
timeout /t 5 /nobreak >nul

REM Start TTS Server
echo.
echo [4/4] Starting TTS Server (Edge-TTS)...
start "TTS Server" cmd /c "python local_services\tts_server.py"
timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo All services started!
echo ==========================================
echo.
echo Services running:
echo   - Ollama LLM:     http://localhost:11434
echo   - LiveKit Server: ws://localhost:7880
echo   - STT Server:     http://localhost:8001
echo   - TTS Server:     http://localhost:8002
echo.
echo To run the agent:
echo   cd agent-starter-python
echo   uv run python src/agent_local.py dev
echo.
echo To run the React frontend:
echo   cd agent-starter-react
echo   npm run dev
echo.
pause
