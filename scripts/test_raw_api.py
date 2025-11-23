"""
Test raw API response from Gemini 2.5 Flash Image
"""

import os
import sys
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def test_raw_api():
    """Test with raw requests to see actual API response"""

    api_key = os.getenv('OPENROUTER_API_KEY')
    model = "google/gemini-2.5-flash-image-preview"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Create a simple test image with the text 'Hello World' on a blue background"
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }

    print("=" * 70)
    print("Testing Gemini 2.5 Flash Image with RAW API")
    print("=" * 70)
    print()

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("Full JSON Response:")
            print("-" * 70)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 70)
            print()

            # Check for images
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})

                print("Message object keys:")
                print(list(message.keys()))
                print()

                if 'images' in message:
                    print(f"✅ Found 'images' field!")
                    print(f"   Number of images: {len(message['images'])}")

                    if message['images']:
                        first_image = message['images'][0]
                        print(f"   Image structure: {list(first_image.keys())}")

                        if 'image_url' in first_image:
                            url = first_image['image_url'].get('url', '')
                            if url.startswith('data:image'):
                                print(f"   ✓ Base64 data URL (length: {len(url)})")
                            elif url.startswith('http'):
                                print(f"   ✓ HTTP URL: {url[:100]}...")
                else:
                    print("❌ No 'images' field in message")

                if 'content' in message:
                    content = message['content']
                    print(f"\nContent field: {content[:200] if content else 'Empty'}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_raw_api()
