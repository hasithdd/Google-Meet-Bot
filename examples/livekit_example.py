"""Example: Using LiveKit Voice AI Agent with Google Meet Bot

This example demonstrates how to use the LiveKit voice AI agent integration
to add an AI assistant to your Google Meet sessions.

Prerequisites:
1. Set up your .env file with all required credentials:
   - Google credentials (EMAIL_ID, EMAIL_PASSWORD)
   - OpenAI API key (OPENAI_API_KEY)
   - LiveKit credentials (LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
   
2. Install all dependencies:
   pip install google-meet-bot
   
3. Have a Google Meet link ready

Usage:
    python examples/livekit_example.py

Note: You'll need to run the LiveKit worker in a separate terminal:
    python -m google_meet_bot.livekit_worker
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_prerequisites():
    """Check if all required environment variables are set."""
    required_vars = [
        'EMAIL_ID',
        'EMAIL_PASSWORD',
        'MEET_LINK',
        'OPENAI_API_KEY',
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file")
        return False
    
    return True


def main():
    """Run the Google Meet bot with LiveKit agent integration."""
    print("=" * 60)
    print("Google Meet Bot - LiveKit Voice AI Agent Example")
    print("=" * 60)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Check if LiveKit is available
    try:
        from google_meet_bot import is_livekit_available
        if not is_livekit_available():
            print("Error: LiveKit packages not installed")
            print("Install with: pip install livekit livekit-agents livekit-plugins-openai")
            sys.exit(1)
    except ImportError:
        print("Error: google_meet_bot package not installed")
        print("Install with: pip install google-meet-bot")
        sys.exit(1)
    
    print("✓ All prerequisites met")
    print()
    
    # Get configuration
    meet_link = os.getenv('MEET_LINK')
    duration = int(os.getenv('RECORDING_DURATION', 300))  # Default 5 minutes
    livekit_room = os.getenv('LIVEKIT_ROOM_NAME', 'google-meet-session')
    
    print(f"Configuration:")
    print(f"  Meet Link: {meet_link}")
    print(f"  Duration: {duration} seconds")
    print(f"  LiveKit Room: {livekit_room}")
    print()
    
    # Import and initialize bot
    from google_meet_bot import JoinGoogleMeet
    
    print("Initializing Google Meet Bot with LiveKit integration...")
    bot = JoinGoogleMeet(enable_livekit=True)
    
    print()
    print("=" * 60)
    print("IMPORTANT: Start the LiveKit worker in a separate terminal:")
    print("=" * 60)
    print()
    print("  python -m google_meet_bot.livekit_worker")
    print()
    print("Press Enter to continue once the worker is running...")
    input()
    
    try:
        # Login to Google
        print("\n[1/3] Logging into Google...")
        bot.Glogin()
        print("✓ Login successful")
        
        # Turn off mic and camera
        print("\n[2/3] Joining meeting and turning off mic/camera...")
        bot.turnOffMicCam(meet_link)
        print("✓ Meeting joined, mic and camera off")
        
        # Start the session with LiveKit agent
        print(f"\n[3/3] Starting LiveKit agent session ({duration} seconds)...")
        print("\nThe AI assistant should now be active in the meeting!")
        print("Participants can talk to the AI assistant, and it will respond.")
        print()
        bot.AskToJoin(None, duration)
        
        print("\n✓ Session completed successfully")
        
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    finally:
        print("\nCleaning up...")
        # The driver will be cleaned up when the script ends
    
    print("\nExample completed!")


if __name__ == "__main__":
    main()
