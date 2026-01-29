#!/bin/bash

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY environment variable is not set"
    echo ""
    echo "Please set it with:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    exit 1
fi

echo "🚀 Starting Website Evolution Tracker..."
echo "📍 Server will run at: http://localhost:5000"
echo "⌨️  Press Ctrl+C to stop"
echo ""

python3 app.py
