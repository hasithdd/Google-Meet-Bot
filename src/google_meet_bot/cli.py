import argparse
import os
import tempfile

from .join_google_meet import JoinGoogleMeet
from .speech_to_text import SpeechToText


def main():
    parser = argparse.ArgumentParser(description="Join a Google Meet, record audio, and summarize it.")
    parser.add_argument("--meet-link", dest="meet_link", default=os.getenv("MEET_LINK"), help="Google Meet link")
    parser.add_argument("--duration", dest="duration", type=int, default=int(os.getenv("RECORDING_DURATION", 60)), help="Recording duration in seconds")
    parser.add_argument("--no-analysis", dest="no_analysis", action="store_true", help="Skip analysis phase")
    parser.add_argument("--livekit", dest="enable_livekit", action="store_true", help="Enable LiveKit voice AI agent mode")
    args = parser.parse_args()

    if not args.meet_link:
        raise SystemExit("--meet-link (or MEET_LINK env) is required")

    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "output.wav")

    bot = JoinGoogleMeet(enable_livekit=args.enable_livekit)
    bot.Glogin()
    bot.turnOffMicCam(args.meet_link)
    bot.AskToJoin(audio_path, args.duration)

    if not args.no_analysis and not args.enable_livekit:
        SpeechToText().transcribe(audio_path)



