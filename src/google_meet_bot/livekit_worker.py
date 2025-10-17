"""Standalone LiveKit worker for Google Meet integration.

This worker connects to a LiveKit room and provides voice AI agent capabilities.
Run this in a separate process to enable LiveKit voice interaction in Google Meet.
"""

import logging
from dotenv import load_dotenv

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai
import os

load_dotenv()

logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """Entry point for LiveKit agent when joining a room.
    
    This function is called when the agent joins a LiveKit room.
    It sets up the voice assistant with OpenAI integration.
    """
    logger.info(f"Starting LiveKit agent for room: {ctx.room.name}")
    
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a helpful AI voice assistant participating in a Google Meet session. "
            "Your interface with users will be voice. "
            "You should use short and concise responses, and avoid usage of unpronounceable punctuation. "
            "Be conversational and helpful. If asked about the meeting, you can help take notes, "
            "answer questions, or provide information."
        ),
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    assistant = VoiceAssistant(
        vad=ctx.proc.userdata.get("vad"),
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model=os.getenv("GPT_MODEL", "gpt-4o-mini")),
        tts=openai.TTS(voice=os.getenv("LIVEKIT_TTS_VOICE", "alloy")),
        chat_ctx=initial_ctx,
    )

    assistant.start(ctx.room)

    # Greet the participants
    await assistant.say(
        "Hello! I'm your AI assistant for this meeting. How can I help you today?",
        allow_interruptions=True
    )

    logger.info("Voice assistant started and ready")


if __name__ == "__main__":
    # Run the LiveKit agent worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )
