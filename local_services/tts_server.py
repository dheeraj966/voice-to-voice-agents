"""Local TTS Server using Edge-TTS"""
import asyncio
import io
from flask import Flask, request, jsonify, Response
import edge_tts

app = Flask(__name__)

# Default voice
DEFAULT_VOICE = "en-US-AriaNeural"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "tts"})

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    async def get_voices():
        voices = await edge_tts.list_voices()
        return [{"name": v["Name"], "gender": v["Gender"], "locale": v["Locale"]} for v in voices]
    
    voices = asyncio.run(get_voices())
    return jsonify({"voices": voices})

@app.route('/tts', methods=['POST'])
def synthesize():
    """Convert text to speech"""
    try:
        data = request.get_json() or {}
        text = data.get('text') or request.form.get('text') or request.args.get('text')
        voice = data.get('voice', DEFAULT_VOICE)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        async def generate_audio():
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        
        audio = asyncio.run(generate_audio())
        
        return Response(
            audio,
            mimetype='audio/mpeg',
            headers={'Content-Disposition': 'inline; filename=speech.mp3'}
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting TTS server on http://localhost:8002")
    print(f"Default voice: {DEFAULT_VOICE}")
    app.run(host='0.0.0.0', port=8002, debug=False)
