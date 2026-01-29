# Voice AI - Deployment Guide

## �️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USERS                                     │
│     (Mobile, Desktop, Mac, Linux - any browser)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              NETLIFY (Frontend)                                  │
│                                                                  │
│   React/Next.js App                                             │
│   - Serves the UI                                               │
│   - Handles user interactions                                    │
│   - Makes API calls to backend                                  │
│                                                                  │
│   URL: https://your-app.netlify.app                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ API Requests (HTTP/WebSocket)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              YOUR SERVER (Backend)                               │
│                                                                  │
│   Python Flask Server (web_agent.py)                            │
│   - Ollama LLM for AI responses                                 │
│   - Edge-TTS for voice synthesis                                │
│   - Handles all AI processing (GPU intensive)                   │
│                                                                  │
│   URL: http://your-server-ip:5000                               │
│   (Could be: your PC, Raspberry Pi, cloud server, etc.)         │
└─────────────────────────────────────────────────────────────────┘
```

## 🌐 Multi-Device Support

This project **already supports multi-device connectivity**:

- ✅ **Desktop browsers** (Chrome, Firefox, Edge, Safari)
- ✅ **Mobile browsers** (iOS Safari, Android Chrome)
- ✅ **Mac/Linux browsers**
- ✅ **Tablets**

---

## 🚀 Deployment Steps

### Step 1: Deploy Frontend to Netlify

1. **Push to GitHub** (if not already):
   ```bash
   cd agent-starter-react
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/voice-ai-frontend.git
   git push -u origin main
   ```

2. **Connect to Netlify**:
   - Go to [Netlify](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repo
   - Build settings are auto-detected from `netlify.toml`

3. **Set Environment Variables** in Netlify Dashboard:
   - `LIVEKIT_API_KEY` - From LiveKit Cloud
   - `LIVEKIT_API_SECRET` - From LiveKit Cloud  
   - `LIVEKIT_URL` - `wss://your-project.livekit.cloud`
   - `NEXT_PUBLIC_BACKEND_URL` - Your backend server URL (optional, can set at runtime)

### Step 2: Run Backend on Your Server

The backend can run on **any device** that has:
- Python 3.10+
- Ollama installed
- Network access

**Option A: Your Local PC**
```bash
cd agent-starter-python
ollama serve &           # Start Ollama in background
python src/web_agent.py  # Start the backend
```

**Option B: Cloud Server (Railway, Render, Fly.io)**
- Deploy the `agent-starter-python` folder
- Set environment variables for Ollama or use cloud LLM

**Option C: Raspberry Pi / Home Server**
- Same as Option A, just on your always-on device

### Step 3: Connect Frontend to Backend

1. Open your Netlify URL (e.g., https://your-app.netlify.app)
2. Click "⚙️ Backend Setup" at the bottom
3. Enter your backend server URL (e.g., http://192.168.1.100:5000)
4. Click Save - the page will reload and connect

---

## 🔧 Environment Files

### React Frontend (.env.local)
```env
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
NEXT_PUBLIC_BACKEND_URL=http://your-server-ip:5000
```

### Python Backend (.env.local)
```env
HOST=0.0.0.0
PORT=5000
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
CORS_ORIGINS=*
```

---

## 🔒 Security Notes

1. **HTTPS Required for Mobile**: Mobile browsers require HTTPS for microphone access. Netlify provides this automatically.

2. **Backend CORS**: The backend has CORS enabled (`CORS_ORIGINS=*`). For production, restrict this to your Netlify domain.

3. **Firewall**: If running backend at home, you may need to:
   - Open port 5000 on your router
   - Configure firewall to allow incoming connections

---

## 📱 Testing Multi-Device

1. Deploy frontend to Netlify
2. Run backend on your PC
3. Open Netlify URL on your phone
4. Configure backend URL in setup page
5. Start chatting!

Both your phone and PC connect to the same backend server.
