#!/usr/bin/env python3
"""
Quick test script to verify Anthropic API is working
"""

import os
import anthropic

# Remove proxy vars that might interfere
for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if proxy_var in os.environ:
        print(f"Removing proxy env var: {proxy_var}")
        del os.environ[proxy_var]

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

if not ANTHROPIC_API_KEY:
    print("❌ ERROR: ANTHROPIC_API_KEY not set")
    print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
    exit(1)

print("✅ API key found")
print(f"Key prefix: {ANTHROPIC_API_KEY[:10]}...")

try:
    print("\n🔧 Initializing Anthropic client...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("✅ Client initialized successfully")

    print("\n📡 Testing API call...")
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Hello, I'm working!' in exactly those words."}
        ]
    )

    response_text = message.content[0].text
    print(f"✅ API Response: {response_text}")

    print("\n🎉 Everything is working!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
