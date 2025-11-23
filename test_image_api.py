"""
Test image generation API directly
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
GEMINI_IMAGE_MODEL = os.getenv('GEMINI_IMAGE_MODEL', 'google/gemini-3-pro-image-preview')

print(f"API Key: {OPENROUTER_API_KEY[:20]}..." if OPENROUTER_API_KEY else "NO API KEY!")
print(f"Base URL: {OPENROUTER_BASE_URL}")
print(f"Model: {GEMINI_IMAGE_MODEL}")
print("-" * 60)

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": GEMINI_IMAGE_MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Create a simple test image with text '测试' in the center"
        }
    ],
    "max_tokens": 4000,
    "temperature": 0.7
}

print("Sending request to OpenRouter...")
response = requests.post(
    OPENROUTER_BASE_URL + "/chat/completions",
    headers=headers,
    json=data,
    timeout=60
)

print(f"Status Code: {response.status_code}")
print("-" * 60)

if response.status_code != 200:
    print(f"ERROR: {response.text}")
else:
    result = response.json()
    print("Response JSON:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Check for images
    if 'choices' in result and len(result['choices']) > 0:
        message = result['choices'][0].get('message', {})

        print("\nMessage keys:", message.keys())

        if 'images' in message:
            print(f"\n✓ Found 'images' field with {len(message['images'])} images!")
        else:
            print("\n✗ No 'images' field in message")

        if 'content' in message:
            print(f"\nContent: {message['content'][:200] if message['content'] else 'EMPTY'}")
