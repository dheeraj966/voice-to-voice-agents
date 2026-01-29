#!/bin/bash
# Voice AI Backend - One-Click Start Script
# Run this to start the backend server

cd "$(dirname "$0")"

echo "========================================"
echo "  Voice AI - Backend Server"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found!"
    echo "Please install Python 3.10+"
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
    echo "[2/4] Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check Ollama
echo "[3/4] Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Start server
echo "[4/4] Starting backend server..."
echo ""
echo "========================================"
echo "  Server starting on http://0.0.0.0:5000"
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

python src/web_agent.py
