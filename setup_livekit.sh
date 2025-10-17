#!/bin/bash
# Setup script for LiveKit integration

echo "=========================================="
echo "Google Meet Bot - LiveKit Integration Setup"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Python 3 found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi
echo "✓ pip3 found"

# Install the package with LiveKit dependencies
echo ""
echo "Installing google-meet-bot with LiveKit dependencies..."
pip3 install livekit livekit-agents livekit-plugins-openai

if [ $? -ne 0 ]; then
    echo "❌ Failed to install LiveKit dependencies"
    exit 1
fi
echo "✓ LiveKit dependencies installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your credentials:"
    echo "   - EMAIL_ID and EMAIL_PASSWORD (Google)"
    echo "   - OPENAI_API_KEY"
    echo "   - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET"
    echo ""
else
    echo "✓ .env file exists"
fi

# Check if required environment variables are set
echo ""
echo "Checking environment variables..."
source .env 2>/dev/null || true

REQUIRED_VARS=("EMAIL_ID" "EMAIL_PASSWORD" "OPENAI_API_KEY" "LIVEKIT_URL" "LIVEKIT_API_KEY" "LIVEKIT_API_SECRET")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "⚠️  Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please edit your .env file and add these values."
    echo "Then run this script again."
else
    echo "✓ All required environment variables are set"
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "To use LiveKit voice AI agent with Google Meet:"
    echo ""
    echo "1. Start the Google Meet bot:"
    echo "   google-meet-bot --meet-link \"YOUR_MEET_LINK\" --duration 300 --livekit"
    echo ""
    echo "2. In a separate terminal, start the LiveKit agent worker:"
    echo "   python -m google_meet_bot.livekit_worker"
    echo ""
    echo "Or run the example script:"
    echo "   python examples/livekit_example.py"
    echo ""
    echo "For more information, see LIVEKIT_INTEGRATION.md"
fi
