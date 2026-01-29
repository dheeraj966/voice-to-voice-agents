"""
Voice AI Desktop Application
Native Windows app - no terminal, no browser
Just double-click to run
"""
import os
import sys
import socket
import threading
import time
import subprocess
from pathlib import Path

# Suppress console output when running windowless
if not sys.stdout:
    sys.stdout = open(os.devnull, 'w')
if not sys.stderr:
    sys.stderr = open(os.devnull, 'w')

# Path resolution for both script and frozen exe
def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

BASE_PATH = get_base_path()
sys.path.insert(0, str(BASE_PATH))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DEBUG', 'false')


def is_ollama_running():
    """Check if Ollama server is running"""
    try:
        import urllib.request
        req = urllib.request.Request('http://127.0.0.1:11434/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except:
        return False


def start_ollama():
    """Start Ollama server in background"""
    try:
        # Find ollama executable
        ollama_paths = [
            'ollama',
            os.path.expandvars(r'%LOCALAPPDATA%\Programs\Ollama\ollama.exe'),
            os.path.expandvars(r'%PROGRAMFILES%\Ollama\ollama.exe'),
            r'C:\Program Files\Ollama\ollama.exe',
        ]
        
        ollama_cmd = None
        for path in ollama_paths:
            if os.path.exists(path) or path == 'ollama':
                ollama_cmd = path
                break
        
        if not ollama_cmd:
            return False
        
        # Hide the console window on Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        
        subprocess.Popen(
            [ollama_cmd, 'serve'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Wait for Ollama to start
        for _ in range(40):  # Wait up to 8 seconds
            time.sleep(0.2)
            if is_ollama_running():
                return True
        return False
    except Exception as e:
        return False


def ensure_ollama():
    """Ensure Ollama is running, start if not"""
    if is_ollama_running():
        return True
    return start_ollama()


class VoiceAIApp:
    """Native desktop application for Voice AI"""
    
    def __init__(self):
        self.port = self._find_free_port()
        self.server = None
        self.error = None
    
    def _find_free_port(self):
        """Find available port"""
        for port in range(5000, 5100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return 5000
    
    def _start_server(self):
        """Start Flask server"""
        try:
            from werkzeug.serving import make_server
            
            # Import web_agent from the bundled location
            import importlib.util
            web_agent_path = BASE_PATH / 'web_agent.py'
            if web_agent_path.exists():
                spec = importlib.util.spec_from_file_location('web_agent', web_agent_path)
                web_agent = importlib.util.module_from_spec(spec)
                sys.modules['web_agent'] = web_agent
                spec.loader.exec_module(web_agent)
            else:
                import web_agent
            
            app = web_agent.create_app()
            self.server = make_server('127.0.0.1', self.port, app, threaded=True)
            self.server.serve_forever()
        except Exception as e:
            self.error = str(e)
    
    def _wait_for_server(self):
        """Wait for server to start"""
        for _ in range(50):
            if self.error:
                return False
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(('127.0.0.1', self.port)) == 0:
                        return True
            except:
                pass
            time.sleep(0.2)
        return False
    
    def _show_error(self, message):
        """Show error dialog"""
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0, message, "Voice AI - Error", 0x10
            )
        except:
            pass
    
    def run(self):
        """Run the application"""
        # Ensure Ollama is running first
        if not ensure_ollama():
            self._show_error(
                "Could not start Ollama server.\n\n"
                "Please install Ollama from https://ollama.ai\n"
                "or start it manually with 'ollama serve'"
            )
            return
        
        # Start server in background
        thread = threading.Thread(target=self._start_server, daemon=True)
        thread.start()
        time.sleep(1)
        
        # Check for startup errors
        if self.error:
            self._show_error(f"Failed to start:\n\n{self.error}\n\nMake sure Ollama is running!")
            return
        
        # Wait for server
        if not self._wait_for_server():
            self._show_error("Server failed to start.\n\nCheck if port 5000 is available.")
            return
        
        # Open native window
        try:
            import webview
            window = webview.create_window(
                'Voice AI',
                f'http://127.0.0.1:{self.port}',
                width=1200,
                height=800,
                resizable=True,
                min_size=(800, 600)
            )
            webview.start()
        except Exception as e:
            self._show_error(f"Failed to open window:\n\n{e}")
        
        # Cleanup
        if self.server:
            self.server.shutdown()


if __name__ == '__main__':
    app = VoiceAIApp()
    app.run()
