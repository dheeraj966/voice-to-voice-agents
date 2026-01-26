"""Local STT Server using Faster-Whisper"""
import io
import wave
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)

# Load the tiny model for fast CPU inference
print("Loading Whisper model (tiny)...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")
print("Model loaded!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "stt"})

@app.route('/stt', methods=['POST'])
def transcribe():
    """Accept audio and return transcription"""
    try:
        # Get audio data from request
        if 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
        else:
            audio_data = request.data
        
        if not audio_data:
            return jsonify({"error": "No audio data provided"}), 400
        
        # Save to temporary file for faster-whisper
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            # Transcribe
            segments, info = model.transcribe(tmp_path, beam_size=1)
            text = " ".join([segment.text for segment in segments])
            
            return jsonify({
                "text": text.strip(),
                "language": info.language,
                "language_probability": info.language_probability
            })
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting STT server on http://localhost:8001")
    app.run(host='0.0.0.0', port=8001, debug=False)
