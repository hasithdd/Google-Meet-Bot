# Quick Start Guide: LiveKit Voice AI Agent for Google Meet

This guide will help you quickly set up and use the LiveKit voice AI agent integration with Google Meet Bot.

## Prerequisites

1. **Google Account** with access to Google Meet
2. **OpenAI API Key** from https://platform.openai.com/api-keys
3. **LiveKit Account**:
   - Sign up at https://cloud.livekit.io (free tier available)
   - Or self-host LiveKit server: https://docs.livekit.io/realtime/self-hosting/

## Step 1: Installation

Install the package with LiveKit dependencies:

```bash
pip install google-meet-bot
pip install livekit livekit-agents livekit-plugins-openai
```

Or use the setup script:

```bash
chmod +x setup_livekit.sh
./setup_livekit.sh
```

## Step 2: Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:

   ```env
   # Google credentials
   EMAIL_ID=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   
   # OpenAI
   OPENAI_API_KEY=sk-...
   GPT_MODEL=gpt-4o-mini
   
   # LiveKit (from cloud.livekit.io or your self-hosted server)
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=APIxxxxxxxxx
   LIVEKIT_API_SECRET=xxxxxxxxxxxx
   LIVEKIT_ROOM_NAME=google-meet-ai-assistant
   ```

### Getting LiveKit Credentials

If using LiveKit Cloud:
1. Go to https://cloud.livekit.io
2. Create a new project
3. Go to Settings → API Keys
4. Copy your URL, API Key, and API Secret

## Step 3: Start the Voice AI Agent

**Option A: Using the CLI (Recommended)**

Terminal 1 - Start the Google Meet bot:
```bash
google-meet-bot \
  --meet-link "https://meet.google.com/xxx-xxxx-xxx" \
  --duration 1800 \
  --livekit
```

Terminal 2 - Start the LiveKit agent worker:
```bash
python -m google_meet_bot.livekit_worker
```

**Option B: Using the example script**

```bash
python examples/livekit_example.py
```

This will guide you through the process interactively.

**Option C: Programmatic usage**

```python
from google_meet_bot import JoinGoogleMeet

# Initialize with LiveKit enabled
bot = JoinGoogleMeet(enable_livekit=True)
bot.Glogin()
bot.turnOffMicCam("https://meet.google.com/xxx-xxxx-xxx")
bot.AskToJoin(None, 1800)  # 30 minutes
```

## Step 4: Test the AI Assistant

1. Join the same Google Meet from another device/browser
2. Wait for the AI assistant to greet you (it will say "Hello! I'm your AI assistant...")
3. Try talking to it:
   - "Hello, are you there?"
   - "Can you help me take notes?"
   - "What's the weather like?" (it can answer general questions)

## Troubleshooting

### Connection Issues

**Problem:** Agent can't connect to LiveKit
- Verify your `LIVEKIT_URL` starts with `wss://`
- Check API key and secret are correct
- Ensure your LiveKit server is running

**Problem:** Agent joins but doesn't respond
- Check that OpenAI API key has credits
- Verify the room names match in both terminals
- Check the worker logs for errors

### Audio Issues

**Problem:** Agent can't hear participants
- In LiveKit Cloud console, verify room is created and participants are connected
- Check that audio is being published in the room

**Problem:** Participants can't hear the agent
- Verify TTS is working (check worker logs)
- Ensure browser has audio permissions

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'livekit'`
```bash
pip install livekit livekit-agents livekit-plugins-openai
```

### Authentication Issues

**Problem:** Google login fails
- Use an App Password instead of your regular password
- Enable 2-factor authentication on your Google account first
- Generate an App Password at: https://myaccount.google.com/apppasswords

## Advanced Usage

### Custom Agent Behavior

Edit `src/google_meet_bot/livekit_worker.py` and modify the system prompt:

```python
initial_ctx = llm.ChatContext().append(
    role="system",
    text=(
        "You are a [your custom role]. "
        "[Your custom instructions]"
    ),
)
```

### Different Voice

Change the TTS voice in your `.env`:

```env
LIVEKIT_TTS_VOICE=nova  # Options: alloy, echo, fable, onyx, nova, shimmer
```

### Use Better AI Model

For higher quality responses:

```env
GPT_MODEL=gpt-4o  # Instead of gpt-4o-mini
```

## Architecture Overview

```
┌─────────────────┐
│  Google Meet    │
│  (Browser)      │
└────────┬────────┘
         │
         │ Selenium
         │ automation
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Google Meet    │────▶│  LiveKit Room    │
│  Bot Process    │     │  (Audio Bridge)  │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  LiveKit Agent   │
                        │  Worker Process  │
                        └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
            ┌──────────────┐         ┌──────────────┐
            │   OpenAI     │         │   OpenAI     │
            │   Whisper    │         │   GPT + TTS  │
            │   (STT)      │         │   (LLM+TTS)  │
            └──────────────┘         └──────────────┘
```

## Next Steps

- Read the full [LIVEKIT_INTEGRATION.md](LIVEKIT_INTEGRATION.md) for detailed information
- Explore the example code in `examples/livekit_example.py`
- Check out LiveKit documentation: https://docs.livekit.io/
- Join the LiveKit community: https://livekit.io/community

## Getting Help

- For LiveKit issues: https://livekit.io/community
- For OpenAI issues: https://platform.openai.com/docs
- For this project: https://github.com/hasithdd/Google-Meet-Bot/issues

## Common Use Cases

### 1. Meeting Note Taker
The AI can listen and take notes. Just say:
- "Please take notes on this discussion"
- "What were the key points discussed?"

### 2. Q&A Assistant
Answer questions during the meeting:
- "What's our company policy on [topic]?"
- "Can you explain [concept]?"

### 3. Meeting Facilitator
Help manage the meeting:
- "Please track action items"
- "Summarize what we've discussed so far"

Enjoy your AI-powered Google Meet experience! 🎉
