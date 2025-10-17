"""LiveKit Voice AI Agent Integration for Google Meet Bot.

This module provides integration with LiveKit's voice AI agents, enabling
real-time voice interaction within Google Meet sessions.
"""

import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv

try:
    from livekit import rtc
    from livekit.agents import (
        AutoSubscribe,
        JobContext,
        WorkerOptions,
        cli,
        llm,
    )
    from livekit.agents.voice_assistant import VoiceAssistant
    from livekit.plugins import openai
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    logging.warning("LiveKit packages not installed. LiveKit agent features will be unavailable.")


load_dotenv()
logger = logging.getLogger(__name__)


class LiveKitAgentManager:
    """Manager for LiveKit voice AI agent integration with Google Meet."""

    def __init__(self):
        """Initialize LiveKit agent manager."""
        if not LIVEKIT_AVAILABLE:
            raise ImportError(
                "LiveKit packages are not installed. "
                "Please install them with: pip install livekit livekit-agents livekit-plugins-openai"
            )
        
        self.livekit_url = os.getenv('LIVEKIT_URL')
        self.livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        self.livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not all([self.livekit_url, self.livekit_api_key, self.livekit_api_secret]):
            raise ValueError(
                "LiveKit credentials are required. Please set LIVEKIT_URL, "
                "LIVEKIT_API_KEY, and LIVEKIT_API_SECRET environment variables."
            )
        
        self.room: Optional[rtc.Room] = None
        self.assistant: Optional[VoiceAssistant] = None

    async def create_voice_assistant(self, ctx: JobContext) -> VoiceAssistant:
        """Create and configure a voice assistant for the LiveKit session.
        
        Args:
            ctx: The LiveKit job context
            
        Returns:
            Configured VoiceAssistant instance
        """
        initial_ctx = llm.ChatContext().append(
            role="system",
            text=(
                "You are a voice assistant in a Google Meet session. "
                "Your interface with users will be voice. "
                "You should use short and concise responses, and avoid usage of unpronounceable punctuation."
            ),
        )

        assistant = VoiceAssistant(
            vad=ctx.proc.userdata.get("vad"),
            stt=openai.STT(model="whisper-1"),
            llm=openai.LLM(model=os.getenv("GPT_MODEL", "gpt-4o-mini")),
            tts=openai.TTS(voice="alloy"),
            chat_ctx=initial_ctx,
        )
        
        return assistant

    async def entrypoint(self, ctx: JobContext):
        """Entry point for LiveKit agent when joining a room.
        
        Args:
            ctx: The LiveKit job context
        """
        initial_ctx = llm.ChatContext().append(
            role="system",
            text=(
                "You are a voice assistant in a Google Meet session. "
                "Your interface with users will be voice. "
                "You should use short and concise responses, and avoid usage of unpronounceable punctuation."
            ),
        )

        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

        assistant = VoiceAssistant(
            vad=ctx.proc.userdata.get("vad"),
            stt=openai.STT(model="whisper-1"),
            llm=openai.LLM(model=os.getenv("GPT_MODEL", "gpt-4o-mini")),
            tts=openai.TTS(voice="alloy"),
            chat_ctx=initial_ctx,
        )

        assistant.start(ctx.room)

        await asyncio.sleep(1)
        await assistant.say("Hello! I'm your AI assistant for this Google Meet session. How can I help you today?", allow_interruptions=True)

        self.assistant = assistant
        self.room = ctx.room

    def run_agent(self):
        """Run the LiveKit agent worker."""
        if not LIVEKIT_AVAILABLE:
            raise ImportError("LiveKit packages not available")
        
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=self.entrypoint,
            ),
        )

    async def connect_to_room(self, room_name: str, participant_name: str = "AI Assistant") -> rtc.Room:
        """Connect to a LiveKit room.
        
        Args:
            room_name: Name of the LiveKit room to join
            participant_name: Name for the AI participant
            
        Returns:
            Connected Room instance
        """
        from livekit import api
        
        # Generate access token
        token = api.AccessToken(self.livekit_api_key, self.livekit_api_secret)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        
        room = rtc.Room()
        await room.connect(self.livekit_url, token.to_jwt())
        
        self.room = room
        return room

    async def publish_audio_stream(self, audio_source: rtc.AudioSource):
        """Publish an audio stream to the LiveKit room.
        
        Args:
            audio_source: The audio source to publish
        """
        if not self.room:
            raise RuntimeError("Not connected to a room. Call connect_to_room first.")
        
        track = rtc.LocalAudioTrack.create_audio_track("microphone", audio_source)
        options = rtc.TrackPublishOptions()
        options.source = rtc.TrackSource.SOURCE_MICROPHONE
        
        publication = await self.room.local_participant.publish_track(track, options)
        logger.info(f"Published audio track: {publication.sid}")

    async def subscribe_to_audio(self, callback):
        """Subscribe to audio tracks in the room.
        
        Args:
            callback: Callback function to handle incoming audio frames
        """
        if not self.room:
            raise RuntimeError("Not connected to a room. Call connect_to_room first.")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                logger.info(f"Subscribed to audio track from {participant.identity}")
                audio_stream = rtc.AudioStream(track)
                asyncio.create_task(callback(audio_stream))

    async def disconnect(self):
        """Disconnect from the LiveKit room and cleanup resources."""
        if self.assistant:
            # Stop the voice assistant if it's running
            logger.info("Stopping voice assistant...")
        
        if self.room:
            await self.room.disconnect()
            logger.info("Disconnected from LiveKit room")
            self.room = None


class GoogleMeetLiveKitBridge:
    """Bridge to connect Google Meet audio with LiveKit agent."""

    def __init__(self, livekit_manager: LiveKitAgentManager):
        """Initialize the bridge.
        
        Args:
            livekit_manager: LiveKit agent manager instance
        """
        self.livekit_manager = livekit_manager
        self.audio_source: Optional[rtc.AudioSource] = None
        self.is_streaming = False

    async def start_audio_streaming(self, sample_rate: int = 48000, channels: int = 1):
        """Start streaming audio from Google Meet to LiveKit.
        
        Args:
            sample_rate: Audio sample rate (default: 48000 Hz)
            channels: Number of audio channels (default: 1 for mono)
        """
        self.audio_source = rtc.AudioSource(sample_rate, channels)
        await self.livekit_manager.publish_audio_stream(self.audio_source)
        self.is_streaming = True
        logger.info(f"Started audio streaming: {sample_rate}Hz, {channels} channel(s)")

    async def push_audio_frame(self, audio_data, sample_rate: int = 48000):
        """Push an audio frame to the LiveKit stream.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Audio sample rate
        """
        if not self.is_streaming or not self.audio_source:
            raise RuntimeError("Audio streaming not started. Call start_audio_streaming first.")
        
        # Convert numpy array to AudioFrame
        import numpy as np
        if isinstance(audio_data, np.ndarray):
            # Ensure audio data is in the correct format (int16)
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            
            frame = rtc.AudioFrame(
                data=audio_data.tobytes(),
                sample_rate=sample_rate,
                num_channels=1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                samples_per_channel=len(audio_data) if len(audio_data.shape) == 1 else audio_data.shape[0],
            )
            await self.audio_source.capture_frame(frame)

    async def stop_audio_streaming(self):
        """Stop streaming audio to LiveKit."""
        self.is_streaming = False
        logger.info("Stopped audio streaming")

    async def handle_livekit_audio(self, audio_stream):
        """Handle incoming audio from LiveKit agent.
        
        Args:
            audio_stream: The audio stream from LiveKit
        """
        async for audio_frame in audio_stream:
            # Process audio frame from LiveKit agent
            # This audio needs to be played back in Google Meet
            # Implementation would depend on how we capture/play audio in the browser
            logger.debug(f"Received audio frame: {audio_frame.samples_per_channel} samples")
            # TODO: Implement audio playback to Google Meet


def create_livekit_agent():
    """Factory function to create a LiveKit agent manager.
    
    Returns:
        LiveKitAgentManager instance
        
    Raises:
        ImportError: If LiveKit packages are not installed
        ValueError: If required credentials are not configured
    """
    return LiveKitAgentManager()


def is_livekit_available() -> bool:
    """Check if LiveKit packages are available.
    
    Returns:
        True if LiveKit is available, False otherwise
    """
    return LIVEKIT_AVAILABLE
