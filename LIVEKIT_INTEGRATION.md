# LiveKit Voice AI Agent Integration

This guide explains how to integrate LiveKit-based voice AI agents with the Google Meet Bot.

## Overview

LiveKit is a real-time communication platform that enables voice AI agents to participate in conversations. This integration allows you to add an AI voice assistant to your Google Meet sessions that can:

- Listen to meeting participants
- Respond to questions in real-time using voice
- Take notes and provide meeting assistance
- Interact naturally using OpenAI's GPT models for conversation and Whisper for speech recognition

## Prerequisites

In addition to the standard Google Meet Bot requirements, you'll need:

1. **LiveKit Server**: Either:
   - Use LiveKit Cloud (https://cloud.livekit.io)
   - Self-host a LiveKit server (https://docs.livekit.io/realtime/self-hosting/)

2. **LiveKit Credentials**:
   - LiveKit URL (WebSocket URL of your LiveKit server)
   - API Key
   - API Secret

3. **OpenAI API Key**: Required for the voice AI agent's:
   - Speech-to-Text (Whisper)
   - Language Model (GPT-4 or GPT-3.5)
   - Text-to-Speech

## Installation

The LiveKit dependencies are included in the package:

```bash
pip install google-meet-bot
```

Or if installing from source:

```bash
pip install -e .
```

This will install:
- `livekit` - LiveKit Python SDK
- `livekit-agents` - LiveKit Agents framework
- `livekit-plugins-openai` - OpenAI plugin for LiveKit

## Configuration

Add the following to your `.env` file:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_ROOM_NAME=google-meet-session
LIVEKIT_TTS_VOICE=alloy

# OpenAI Configuration (required for voice AI)
OPENAI_API_KEY=your_openai_api_key
GPT_MODEL=gpt-4o-mini
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `LIVEKIT_URL` | WebSocket URL of your LiveKit server | Required |
| `LIVEKIT_API_KEY` | Your LiveKit API key | Required |
| `LIVEKIT_API_SECRET` | Your LiveKit API secret | Required |
| `LIVEKIT_ROOM_NAME` | Name of the LiveKit room to join | `google-meet-session` |
| `LIVEKIT_TTS_VOICE` | OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer) | `alloy` |
| `GPT_MODEL` | OpenAI model for conversation | `gpt-4o-mini` |

## Usage

### Method 1: Command Line Interface (Recommended)

Run the bot with LiveKit agent mode enabled:

```bash
google-meet-bot --meet-link "https://meet.google.com/xxx-xxxx-xxx" --duration 300 --livekit
```

This will:
1. Join the Google Meet session
2. Keep the session alive
3. Print instructions for starting the LiveKit agent worker

In a **separate terminal**, start the LiveKit agent worker:

```bash
python -m google_meet_bot.livekit_worker
```

The agent will:
- Connect to the LiveKit room
- Join the audio session
- Greet participants
- Listen and respond to conversations

### Method 2: Programmatic Usage

```python
from google_meet_bot import JoinGoogleMeet

# Initialize with LiveKit enabled
bot = JoinGoogleMeet(enable_livekit=True)
bot.Glogin()
bot.turnOffMicCam("https://meet.google.com/xxx-xxxx-xxx")
bot.AskToJoin(None, 300)  # Duration in seconds

# In a separate process/thread, run the LiveKit worker
# See Method 1 for how to start the worker
```

### Method 3: Standalone LiveKit Worker

You can also run just the LiveKit worker without the Google Meet bot:

```python
from google_meet_bot.livekit_agent import LiveKitAgentManager

# Run the agent
manager = LiveKitAgentManager()
manager.run_agent()
```

## Architecture

The integration consists of three main components:

1. **Google Meet Bot** (`JoinGoogleMeet`):
   - Handles Google Meet login and session management
   - Manages the browser automation
   - Coordinates with LiveKit components

2. **LiveKit Agent Manager** (`LiveKitAgentManager`):
   - Manages LiveKit room connections
   - Handles audio streaming
   - Provides the voice assistant interface

3. **LiveKit Worker** (`livekit_worker.py`):
   - Standalone process that runs the voice AI agent
   - Connects to LiveKit room
   - Processes audio and generates responses

### Audio Flow

```
Google Meet Audio → Browser → LiveKit Room → AI Agent
                                         ↓
                              OpenAI (Whisper STT)
                                         ↓
                              OpenAI (GPT for response)
                                         ↓
                              OpenAI (TTS)
                                         ↓
AI Agent Response → LiveKit Room → Browser → Google Meet
```

## Advanced Usage

### Custom Voice Assistant Behavior

You can customize the voice assistant's behavior by modifying the system prompt in `livekit_worker.py`:

```python
initial_ctx = llm.ChatContext().append(
    role="system",
    text=(
        "You are a [custom role description]. "
        "Your interface with users will be voice. "
        "[Add your custom instructions here]"
    ),
)
```

### Using Different TTS Voices

OpenAI provides several TTS voices. Set the `LIVEKIT_TTS_VOICE` environment variable to one of:
- `alloy` - Neutral and balanced
- `echo` - Male voice
- `fable` - British accent
- `onyx` - Deep male voice
- `nova` - Female voice
- `shimmer` - Soft female voice

### Adjusting Model Selection

For faster responses, use `gpt-4o-mini` (default). For higher quality:

```env
GPT_MODEL=gpt-4o
```

## Troubleshooting

### LiveKit Connection Issues

If you can't connect to LiveKit:

1. Verify your `LIVEKIT_URL` is correct (should start with `wss://`)
2. Check that your API key and secret are valid
3. Ensure your LiveKit server is running and accessible

### Audio Not Working

1. Make sure the LiveKit worker is running in a separate process
2. Check that the `LIVEKIT_ROOM_NAME` matches between the bot and worker
3. Verify OpenAI API key has access to Whisper and TTS

### Import Errors

If you see import errors related to LiveKit:

```bash
pip install livekit livekit-agents livekit-plugins-openai
```

## Limitations

1. **Two-Process Requirement**: Currently requires running the LiveKit worker in a separate process
2. **Audio Routing**: The integration uses LiveKit as an intermediary rather than direct browser audio capture
3. **Network Requirements**: Requires stable internet connection for LiveKit and OpenAI API calls

## Examples

### Example 1: Meeting Assistant

```bash
# Start the Google Meet bot with LiveKit
google-meet-bot --meet-link "https://meet.google.com/abc-defg-hij" \
                --duration 1800 \
                --livekit

# In another terminal, start the agent
python -m google_meet_bot.livekit_worker
```

The AI assistant will join and can:
- Answer questions about the meeting topic
- Take notes when asked
- Provide information or clarifications
- Help with action items

### Example 2: Custom Agent with Specific Role

Modify `livekit_worker.py` to create a specialized agent:

```python
initial_ctx = llm.ChatContext().append(
    role="system",
    text=(
        "You are a technical meeting facilitator specializing in software development. "
        "Help document technical decisions, track action items, and clarify technical concepts. "
        "Keep responses brief and technical."
    ),
)
```

## Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LiveKit Cloud](https://cloud.livekit.io)

## Contributing

To contribute improvements to the LiveKit integration:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Same as the main Google Meet Bot project (MIT License).
