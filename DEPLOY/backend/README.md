# Voice AI - Backend Server

## ⚡ QUICK START (Copy-Paste Commands)

### Windows (One-liner)
```cmd
cd backend && pip install -r requirements.txt && ollama serve & timeout 5 && python src/web_agent.py
```

### Windows (Step by step)
```cmd
cd backend
pip install -r requirements.txt
start ollama serve
python src/web_agent.py
```

### Mac/Linux (One-liner)
```bash
cd backend && pip install -r requirements.txt && ollama serve & sleep 5 && python src/web_agent.py
```

### Mac/Linux (Step by step)
```bash
cd backend
pip install -r requirements.txt
ollama serve &
python src/web_agent.py
```

### Using Start Scripts
```cmd
# Windows
START_SERVER.bat

# Mac/Linux
chmod +x START_SERVER.sh && ./START_SERVER.sh
```

**Server URL:** `http://0.0.0.0:5000` or `http://YOUR_IP:5000`

---

## 📁 Location
```
C:\Users\maxwe\ml project\fast_test_env\live_kit\DEPLOY\backend
```

**Copy this entire `backend` folder to any device where you want to run the AI server.**

---

## 🖥️ Requirements

- Python 3.10 or higher
- Ollama (for AI/LLM)

---

## 🚀 Setup & Run Commands

### Windows

```cmd
:: Step 1: Install Python dependencies (first time only)
cd backend
pip install -r requirements.txt

:: Step 2: Install and start Ollama (if not installed)
:: Download from: https://ollama.ai
:: Then run:
ollama serve

:: Step 3: Pull the AI model (first time only)
ollama pull llama3.2

:: Step 4: Start the backend server
python src/web_agent.py
```

### Mac / Linux

```bash
# Step 1: Install Python dependencies (first time only)
cd backend
pip install -r requirements.txt

# Step 2: Install Ollama (if not installed)
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Step 3: Start Ollama
ollama serve &

# Step 4: Pull the AI model (first time only)
ollama pull llama3.2

# Step 5: Start the backend server
python src/web_agent.py
```

---

## ✅ When Running Successfully

You'll see:
```
==================================================
🎤 Text-to-Audio Agent - Web Interface
   Environment: development
   LLM: llama3.2 (Ollama)
   URL: http://0.0.0.0:5000
==================================================
```

**The backend is now running on port 5000!**

---

## 🌐 Find Your IP Address

### Windows
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100`)

### Mac
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### Linux
```bash
hostname -I
```

---

## 🔗 Connect Frontend to Backend

1. Your backend URL will be: `http://YOUR_IP:5000`
   - Example: `http://192.168.1.100:5000`

2. Open your Netlify frontend
3. Go to `/setup` page
4. Enter the backend URL
5. Click Save

---

## 📂 Files Included

```
backend/
├── src/
│   ├── web_agent.py      # Main server (run this!)
│   ├── agent.py          # LiveKit voice agent
│   ├── templates/
│   │   └── index.html    # Web UI template
│   └── ...
├── requirements.txt      # Python dependencies
└── .env.example         # Environment variables template
```

---

## ⚙️ Configuration (Optional)

Copy `.env.example` to `.env.local` and customize:

```env
# Server settings
HOST=0.0.0.0
PORT=5000

# AI Model
OLLAMA_MODEL=llama3.2

# Allow connections from your Netlify site
CORS_ORIGINS=*
```

---

## 🔧 Troubleshooting

### "Ollama not running"
```cmd
ollama serve
```

### "Model not found"
```cmd
ollama pull llama3.2
```

### "Port 5000 already in use"
```cmd
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### "Cannot connect from phone/other device"
- Make sure both devices are on the same WiFi network
- Check your firewall allows port 5000
- Use your computer's local IP, not `localhost`
