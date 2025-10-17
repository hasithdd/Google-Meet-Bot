"""Google Meet Bot package.

Automate joining Google Meet, record audio, transcribe with Whisper, and summarize using GPT.
"""

from .record_audio import AudioRecorder
from .speech_to_text import SpeechToText
from .join_google_meet import JoinGoogleMeet

# Import LiveKit components if available
try:
    from .livekit_agent import (
        LiveKitAgentManager,
        GoogleMeetLiveKitBridge,
        create_livekit_agent,
        is_livekit_available,
    )
    __all__ = [
        "AudioRecorder",
        "SpeechToText",
        "JoinGoogleMeet",
        "LiveKitAgentManager",
        "GoogleMeetLiveKitBridge",
        "create_livekit_agent",
        "is_livekit_available",
    ]
except ImportError:
    __all__ = [
        "AudioRecorder",
        "SpeechToText",
        "JoinGoogleMeet",
    ]



