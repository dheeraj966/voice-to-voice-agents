"""
Text-to-Audio Agent
- Type your question (text input)
- Ollama generates response (local LLM)
- Edge-TTS speaks the response (audio output)
"""
import asyncio
import os
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
import edge_tts
import pygame

load_dotenv(".env.local")

# Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TTS_VOICE = "en-US-AriaNeural"  # Natural female voice

SYSTEM_PROMPT = """You are a helpful voice AI assistant. 
Keep your responses concise and conversational - under 3 sentences when possible.
Don't use special formatting, bullet points, or emojis.
Speak naturally as if having a conversation."""

# Initialize pygame for audio
pygame.mixer.init()

async def text_to_speech(text: str) -> str:
    """Convert text to speech and return audio file path"""
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    await communicate.save(temp_file.name)
    return temp_file.name

def play_audio(file_path: str):
    """Play audio file"""
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
    # Clean up
    pygame.mixer.music.unload()
    os.unlink(file_path)

async def main():
    print("=" * 50)
    print("🎤 Text-to-Audio Agent")
    print(f"   LLM: {OLLAMA_MODEL} (Ollama)")
    print(f"   TTS: {TTS_VOICE} (Edge-TTS)")
    print("=" * 50)
    print("Type your message and press Enter.")
    print("Type 'quit' to exit.\n")
    
    # Create OpenAI client for Ollama
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama"
    )
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        try:
            user_input = input("\n📝 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            if not user_input:
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            print("\n🤔 Thinking...", end="", flush=True)
            
            # Get LLM response
            response = client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=messages,
            )
            
            assistant_text = response.choices[0].message.content
            print(f"\r💬 Assistant: {assistant_text}")
            
            messages.append({"role": "assistant", "content": assistant_text})
            
            # Convert to speech and play
            print("🔊 Speaking...", end="", flush=True)
            audio_file = await text_to_speech(assistant_text)
            print("\r" + " " * 20 + "\r", end="")  # Clear the "Speaking..." text
            play_audio(audio_file)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
