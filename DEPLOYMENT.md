# Voice AI - Deployment Guide

## 🌐 Multi-Device Support

This project **already supports multi-device connectivity**:

- ✅ **Desktop browsers** (Chrome, Firefox, Edge, Safari)
- ✅ **Mobile browsers** (iOS Safari, Android Chrome)
- ✅ **Mac/Linux browsers**
- ✅ **Tablets**

The LiveKit WebRTC infrastructure handles all cross-platform audio/video streaming automatically.

---

## 📦 Project Architecture

### Two Separate Systems:

1. **React Frontend** (`agent-starter-react/`)
   - Next.js web application
   - Uses LiveKit for real-time voice
   - **Deployable to Netlify**

2. **Python Backend** (`agent-starter-python/src/web_agent.py`)
   - Flask web server with chat API
   - Uses local Ollama for LLM
   - **NOT deployable to Netlify** (requires server)

---

## 🚀 Deployment Options

### Option 1: Full Cloud Deployment (Recommended)

#### Frontend → Netlify
```bash
cd agent-starter-react
pnpm install
netlify deploy --prod
```

**Required Environment Variables** (set in Netlify Dashboard):
- `LIVEKIT_API_KEY` - From LiveKit Cloud
- `LIVEKIT_API_SECRET` - From LiveKit Cloud  
- `LIVEKIT_URL` - `wss://your-project.livekit.cloud`

#### Backend → Railway/Render/Fly.io

The Python backend cannot run on Netlify. Deploy to:

| Platform | Best For | Cost |
|----------|----------|------|
| [Railway](https://railway.app) | Easy deployment | $5-20/mo |
| [Render](https://render.com) | Free tier available | Free-$25/mo |
| [Fly.io](https://fly.io) | Global edge | $5-20/mo |
| [Heroku](https://heroku.com) | Simple setup | $7-25/mo |

For the backend, you'll need to either:
1. Run Ollama on your server (requires GPU)
2. Replace Ollama with cloud LLM (OpenAI, Groq, Together.ai)

---

### Option 2: Local Development + Cloud Frontend

1. Run backend locally:
   ```bash
   cd agent-starter-python
   ollama serve &
   python src/web_agent.py
   ```

2. Deploy frontend to Netlify with your local IP in `.env.local`

---

### Option 3: Docker Compose (Self-hosted)

For full self-hosting with Docker:

```bash
docker-compose up -d
```

This runs:
- LiveKit Server
- Ollama LLM
- Voice AI Backend

---

## 🔧 Environment Setup

### React Frontend (.env.local)
```env
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### Python Backend (.env.local)
```env
FLASK_ENV=production
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=https://your-netlify-site.netlify.app
```

---

## 🎯 LiveKit Cloud Setup

1. Go to [LiveKit Cloud](https://cloud.livekit.io)
2. Create a new project
3. Get your API keys
4. Deploy your Python agent to the cloud using LiveKit Agents CLI:
   ```bash
   lk app deploy
   ```

---

## 📱 Testing Multi-Device

Once deployed:

1. Open your Netlify URL on desktop
2. Scan QR code or share URL to mobile
3. Both devices connect to same LiveKit room
4. Voice streams between all connected devices

---

## ⚠️ Important Notes

- **Netlify limitations**: Cannot run persistent servers or local Ollama
- **LiveKit Cloud**: Required for production multi-device voice
- **Backend hosting**: Choose Railway/Render/Fly.io for Python backend
- **Mobile browsers**: Require HTTPS for microphone access (Netlify provides this)
