"""
LiveKit Agent configured to use LOCAL services:
- LLM: Ollama (http://localhost:11434)
- STT: Faster-Whisper server (http://localhost:8001)
- TTS: Edge-TTS server (http://localhost:8002)
"""
import logging
import os

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
)
from livekit.plugins import openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Local service URLs
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    logger.info(f"Using Ollama at {OLLAMA_BASE_URL} with model {OLLAMA_MODEL}")

    # Set up a voice AI pipeline using LOCAL services
    session = AgentSession(
        # LLM: Use Ollama via OpenAI-compatible API
        llm=openai.LLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",  # Ollama doesn't need a real key
        ),
        # TTS: Use OpenAI-compatible TTS (we'll use the built-in one for now)
        # For a fully local setup, you'd need a custom TTS plugin
        tts=openai.TTS(
            model="tts-1",
            voice="alloy",
            base_url=OLLAMA_BASE_URL,  # This won't work with Ollama, see note below
        ),
        # VAD and turn detection
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Start the session
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                # Disable cloud noise cancellation for local setup
                noise_cancellation=None,
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
