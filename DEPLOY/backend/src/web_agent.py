"""
Text-to-Audio Agent - Web Interface Backend
CI/CD Ready with proper configuration, logging, and error handling
Works both as script and as frozen PyInstaller executable
"""
import asyncio
import os
import sys
import tempfile
import uuid
import json
import logging
import atexit
import time
import subprocess
import shutil
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
from pathlib import Path

import requests
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import edge_tts

# =============================================================================
# Path Resolution for PyInstaller
# =============================================================================

def get_base_path() -> Path:
    """Get the base path for resources - works for both script and frozen exe"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent

BASE_PATH = get_base_path()

# =============================================================================
# Configuration
# =============================================================================

class Config:
    """Application configuration - CI/CD ready with environment variables"""
    
    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    TESTING = os.getenv("TESTING", "false").lower() == "true"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # LLM Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 60))
    
    # Audio Configuration
    AUDIO_CACHE_DIR = os.getenv("AUDIO_CACHE_DIR", tempfile.gettempdir())
    AUDIO_MAX_CACHE_SIZE = int(os.getenv("AUDIO_MAX_CACHE_SIZE", 100))
    
    # Security
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 10000))
    MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", 100))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging(config: Config) -> logging.Logger:
    """Configure application logging"""
    logger = logging.getLogger("voice-ai")
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
    logger.addHandler(handler)
    
    return logger

# =============================================================================
# Application Factory
# =============================================================================

def create_app(config: Optional[Config] = None) -> Flask:
    """Application factory for CI/CD and testing"""
    
    # Load environment
    load_dotenv(".env.local")
    load_dotenv(".env")
    
    if config is None:
        config = Config()
    
    # Determine template and static folders based on execution context
    template_folder = str(BASE_PATH / 'templates')
    static_folder = str(BASE_PATH / 'static') if (BASE_PATH / 'static').exists() else None
    
    # Create Flask app with proper paths
    app = Flask(
        __name__, 
        template_folder=template_folder, 
        static_folder=static_folder
    )
    app.config.from_object(config)
    
    # Setup CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Setup logging
    logger = setup_logging(config)
    app.logger = logger
    
    # Initialize services
    init_services(app, config)
    
    # Register routes
    register_routes(app, config)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Cleanup on shutdown
    atexit.register(lambda: cleanup(app))
    
    return app

# =============================================================================
# Services
# =============================================================================

VOICES = {
    "aria": {"id": "en-US-AriaNeural", "name": "Aria", "gender": "Female", "accent": "US"},
    "guy": {"id": "en-US-GuyNeural", "name": "Guy", "gender": "Male", "accent": "US"},
    "jenny": {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "Female", "accent": "US"},
    "eric": {"id": "en-US-EricNeural", "name": "Eric", "gender": "Male", "accent": "US"},
    "emma": {"id": "en-GB-SoniaNeural", "name": "Sonia", "gender": "Female", "accent": "UK"},
    "ryan": {"id": "en-GB-RyanNeural", "name": "Ryan", "gender": "Male", "accent": "UK"},
    "natasha": {"id": "en-AU-NatashaNeural", "name": "Natasha", "gender": "Female", "accent": "AU"},
}

DEFAULT_SYSTEM_PROMPT = """You are a helpful voice AI assistant. 
Keep your responses concise and conversational - under 3 sentences when possible.
Don't use special formatting, bullet points, markdown, or emojis.
Speak naturally as if having a conversation."""

def start_ollama_server(logger: logging.Logger) -> bool:
    """Attempt to start Ollama server automatically"""
    # Find ollama executable
    ollama_paths = [
        'ollama',
        os.path.expandvars(r'%LOCALAPPDATA%\Programs\Ollama\ollama.exe'),
        os.path.expandvars(r'%PROGRAMFILES%\Ollama\ollama.exe'),
        r'C:\Program Files\Ollama\ollama.exe',
        '/usr/local/bin/ollama',
        '/usr/bin/ollama',
    ]
    
    ollama_cmd = shutil.which('ollama')
    if not ollama_cmd:
        for path in ollama_paths:
            if os.path.exists(path):
                ollama_cmd = path
                break
    
    if not ollama_cmd:
        logger.error("Could not find Ollama executable")
        return False
    
    try:
        logger.info(f"Starting Ollama server using: {ollama_cmd}")
        if sys.platform == 'win32':
            # Windows: start hidden process
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen(
                [ollama_cmd, 'serve'],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Unix: start in background
            subprocess.Popen(
                [ollama_cmd, 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        logger.info("Ollama server start command issued")
        return True
    except Exception as e:
        logger.error(f"Failed to start Ollama: {e}")
        return False

def check_ollama_connection(config: Config, logger: logging.Logger, max_retries: int = 3, auto_start: bool = True) -> bool:
    """Check if Ollama server is running and accessible, optionally auto-start it"""
    base_url = config.OLLAMA_BASE_URL.replace('/v1', '')
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Ollama connection successful (attempt {attempt + 1})")
                return True
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ollama connection attempt {attempt + 1}/{max_retries} failed - server not reachable")
            # Try to auto-start Ollama on first failure
            if attempt == 0 and auto_start:
                logger.info("Attempting to auto-start Ollama server...")
                if start_ollama_server(logger):
                    time.sleep(5)  # Give Ollama more time to start
                    continue
        except Exception as e:
            logger.warning(f"Ollama connection attempt {attempt + 1}/{max_retries} failed: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2)  # Wait before retry
    
    return False

def init_services(app: Flask, config: Config):
    """Initialize application services"""
    app.llm_client = OpenAI(
        base_url=config.OLLAMA_BASE_URL,
        api_key="ollama",
        timeout=config.LLM_TIMEOUT
    )
    app.conversations = {}
    app.audio_files = {}
    app.ollama_available = False  # Track connection status
    
    # Check Ollama connection at startup
    app.ollama_available = check_ollama_connection(config, app.logger)
    
    if not app.ollama_available:
        app.logger.error("=" * 60)
        app.logger.error("WARNING: Ollama server is not running!")
        app.logger.error("Please start Ollama with: ollama serve")
        app.logger.error("The app will continue but chat will not work until Ollama is running.")
        app.logger.error("=" * 60)
    
    app.logger.info(f"Services initialized - LLM: {config.OLLAMA_MODEL}, Ollama available: {app.ollama_available}")

def cleanup(app: Flask):
    """Cleanup resources on shutdown"""
    for audio_id, path in app.audio_files.items():
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

# =============================================================================
# Helpers
# =============================================================================

def get_or_create_conversation(app: Flask, session_id: str) -> Dict[str, Any]:
    """Get or create a conversation session"""
    if session_id not in app.conversations:
        app.conversations[session_id] = {
            "messages": [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}],
            "history": [],
            "created": datetime.now().isoformat()
        }
    return app.conversations[session_id]

async def text_to_speech(text: str, voice: str = "en-US-AriaNeural", rate: str = "+0%") -> str:
    """Convert text to speech and return audio file path"""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    await communicate.save(temp_file.name)
    return temp_file.name

def validate_request(f):
    """Decorator to validate incoming requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST', 'PUT'] and request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415
        return f(*args, **kwargs)
    return decorated

# =============================================================================
# Routes
# =============================================================================

def register_routes(app: Flask, config: Config):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint for CI/CD"""
        # Re-check Ollama status on health check
        ollama_status = check_ollama_connection(config, app.logger, max_retries=1)
        app.ollama_available = ollama_status
        
        return jsonify({
            "status": "healthy" if ollama_status else "degraded",
            "version": "1.0.0",
            "environment": config.ENV,
            "model": config.OLLAMA_MODEL,
            "ollama_available": ollama_status,
            "message": None if ollama_status else "Ollama server not running. Start with 'ollama serve'"
        })
    
    @app.route('/api/config')
    def get_config():
        """Get public configuration"""
        return jsonify({
            "model": config.OLLAMA_MODEL,
            "voices": VOICES,
            "max_message_length": config.MAX_MESSAGE_LENGTH,
            "features": {"tts": True, "streaming": False, "vision": False}
        })
    
    @app.route('/api/voices', methods=['GET'])
    def get_voices():
        return jsonify(VOICES)
    
    @app.route('/api/models', methods=['GET'])
    def get_models():
        try:
            import requests
            resp = requests.get(f"{config.OLLAMA_BASE_URL.replace('/v1', '')}/api/tags", timeout=5)
            models = [m["name"] for m in resp.json().get("models", [])]
            return jsonify({"models": models, "current": config.OLLAMA_MODEL})
        except Exception as e:
            app.logger.warning(f"Could not fetch models: {e}")
            return jsonify({"models": [config.OLLAMA_MODEL], "current": config.OLLAMA_MODEL})
    
    @app.route('/api/chat', methods=['POST'])
    @validate_request
    def chat():
        data = request.json or {}
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        voice_id = data.get('voice', 'aria')
        speed = data.get('speed', 0)
        generate_audio = data.get('generate_audio', True)
        custom_system = data.get('system_instructions')
        model_params = data.get('model_params', {})
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        if len(message) > config.MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"Message exceeds {config.MAX_MESSAGE_LENGTH} characters"}), 400
        
        conv = get_or_create_conversation(app, session_id)
        
        if custom_system:
            conv["messages"][0] = {"role": "system", "content": custom_system}
        
        conv["messages"].append({"role": "user", "content": message})
        
        if len(conv["messages"]) > config.MAX_HISTORY_LENGTH:
            conv["messages"] = [conv["messages"][0]] + conv["messages"][-config.MAX_HISTORY_LENGTH:]
        
        # Check if Ollama is available, try to reconnect and auto-start if not
        if not app.ollama_available:
            app.logger.info("Ollama not available, attempting reconnection with auto-start...")
            app.ollama_available = check_ollama_connection(config, app.logger, max_retries=3, auto_start=True)
        
        if not app.ollama_available:
            # Remove the user message we just added since we can't process it
            conv["messages"].pop()
            return jsonify({
                "error": "Ollama server is not running and could not be auto-started. Please start Ollama with 'ollama serve' command.",
                "error_type": "connection_error",
                "suggestion": "Run 'ollama serve' in a terminal, then try again."
            }), 503
        
        try:
            api_params = {"model": config.OLLAMA_MODEL, "messages": conv["messages"]}
            
            if model_params:
                if 'temperature' in model_params:
                    api_params['temperature'] = float(model_params['temperature'])
                if 'top_p' in model_params:
                    api_params['top_p'] = float(model_params['top_p'])
                if 'max_tokens' in model_params:
                    api_params['max_tokens'] = int(model_params['max_tokens'])
                if 'frequency_penalty' in model_params:
                    api_params['frequency_penalty'] = float(model_params['frequency_penalty'])
                if 'presence_penalty' in model_params:
                    api_params['presence_penalty'] = float(model_params['presence_penalty'])
                if 'seed' in model_params and model_params['seed'] != -1:
                    api_params['seed'] = int(model_params['seed'])
                
                extra_options = {}
                if 'top_k' in model_params:
                    extra_options['top_k'] = int(model_params['top_k'])
                if 'repeat_penalty' in model_params:
                    extra_options['repeat_penalty'] = float(model_params['repeat_penalty'])
                
                if extra_options:
                    api_params['extra_body'] = {'options': extra_options}
            
            response = app.llm_client.chat.completions.create(**api_params)
            assistant_text = response.choices[0].message.content
            
            conv["messages"].append({"role": "assistant", "content": assistant_text})
            conv["history"].append({
                "id": str(uuid.uuid4()),
                "user": message,
                "assistant": assistant_text,
                "timestamp": datetime.now().isoformat(),
                "voice": voice_id
            })
            
            result = {"text": assistant_text, "session_id": session_id, "audio_url": None}
            
            if generate_audio:
                voice = VOICES.get(voice_id, VOICES["aria"])["id"]
                rate = f"{speed:+d}%" if speed != 0 else "+0%"
                audio_path = asyncio.run(text_to_speech(assistant_text, voice, rate))
                
                audio_id = str(uuid.uuid4())
                app.audio_files[audio_id] = audio_path
                
                if len(app.audio_files) > config.AUDIO_MAX_CACHE_SIZE:
                    oldest = list(app.audio_files.keys())[0]
                    try:
                        os.remove(app.audio_files[oldest])
                    except:
                        pass
                    del app.audio_files[oldest]
                
                result["audio_url"] = f"/api/audio/{audio_id}"
            
            app.logger.info(f"Chat processed - session: {session_id[:8]}...")
            return jsonify(result)
            
        except Exception as e:
            error_msg = str(e).lower()
            # Check if it's a connection error to Ollama
            if 'connection' in error_msg or 'refused' in error_msg or 'timeout' in error_msg:
                app.ollama_available = False
                app.logger.error(f"Ollama connection lost: {e}")
                
                # Try to auto-restart Ollama
                app.logger.info("Attempting to auto-restart Ollama...")
                app.ollama_available = check_ollama_connection(config, app.logger, max_retries=3, auto_start=True)
                
                # Remove the user message since we couldn't process it
                if conv["messages"] and conv["messages"][-1]["role"] == "user":
                    conv["messages"].pop()
                
                if app.ollama_available:
                    return jsonify({
                        "error": "Ollama was restarted. Please try your message again.",
                        "error_type": "connection_restored",
                        "suggestion": "Ollama is now running. Please resend your message."
                    }), 503
                else:
                    return jsonify({
                        "error": "Lost connection to Ollama server and could not auto-restart. Please ensure Ollama is running.",
                        "error_type": "connection_error",
                        "suggestion": "Run 'ollama serve' in a terminal, then try again."
                    }), 503
            
            app.logger.error(f"Chat error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/audio/<audio_id>', methods=['GET'])
    def get_audio(audio_id):
        if audio_id in app.audio_files:
            path = app.audio_files[audio_id]
            if os.path.exists(path):
                return send_file(path, mimetype='audio/mpeg')
        return jsonify({"error": "Audio not found"}), 404
    
    @app.route('/api/history/<session_id>', methods=['GET'])
    def get_history(session_id):
        conv = app.conversations.get(session_id)
        if conv:
            return jsonify({"history": conv["history"]})
        return jsonify({"history": []})
    
    @app.route('/api/clear/<session_id>', methods=['POST'])
    def clear_history(session_id):
        if session_id in app.conversations:
            del app.conversations[session_id]
        return jsonify({"success": True})
    
    @app.route('/api/tts', methods=['POST'])
    @validate_request
    def tts_only():
        data = request.json or {}
        text = data.get('text', '').strip()
        voice_id = data.get('voice', 'aria')
        speed = data.get('speed', 0)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        try:
            voice = VOICES.get(voice_id, VOICES["aria"])["id"]
            rate = f"{speed:+d}%" if speed != 0 else "+0%"
            audio_path = asyncio.run(text_to_speech(text, voice, rate))
            
            audio_id = str(uuid.uuid4())
            app.audio_files[audio_id] = audio_path
            
            return jsonify({"audio_url": f"/api/audio/{audio_id}"})
        except Exception as e:
            app.logger.error(f"TTS error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/export/<session_id>', methods=['GET'])
    def export_conversation(session_id):
        conv = app.conversations.get(session_id)
        if conv:
            return jsonify({
                "session_id": session_id,
                "created": conv["created"],
                "history": conv["history"]
            })
        return jsonify({"error": "Session not found"}), 404

# =============================================================================
# Error Handlers
# =============================================================================

def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# =============================================================================
# Main Entry Point
# =============================================================================

app = create_app()

if __name__ == '__main__':
    config = Config()
    print("=" * 50)
    print("🎤 Text-to-Audio Agent - Web Interface")
    print(f"   Environment: {config.ENV}")
    print(f"   LLM: {config.OLLAMA_MODEL} (Ollama)")
    print(f"   URL: http://{config.HOST}:{config.PORT}")
    print("=" * 50)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
