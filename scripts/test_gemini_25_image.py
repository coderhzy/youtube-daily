"""
Test Gemini 2.5 Flash Image Preview (Nano Banana)
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_gemini_25_image():
    """Test Gemini 2.5 Flash Image Preview"""

    api_key = os.getenv('OPENROUTER_API_KEY')
    model = "google/gemini-2.5-flash-image-preview"

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    # PPT-style prompt for blockchain news
    prompt = """Create a professional PowerPoint-style infographic for a blockchain presentation.

Title: "区块链市场动态 - 2025年11月"

Layout: Modern business presentation slide (16:9)
Style: Professional, clean, suitable for YouTube video presentation

Content to include:
1. Bold Chinese title at the top
2. Three key statistics with icons:
   - Bitcoin price trend (up arrow, green)
   - Trading volume (bar chart icon, blue)
   - Market sentiment (emoji, purple)
3. Gradient background (blue to purple)
4. High contrast for video recording
5. Professional business color scheme

Make it look like a professional PowerPoint slide that would appear in a business presentation or YouTube video about blockchain news."""

    print("=" * 70)
    print("Testing Gemini 2.5 Flash Image Preview")
    print("=" * 70)
    print(f"Model: {model}")
    print()
    print("Prompt:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)
    print()

    try:
        print("Calling API...")
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4000,
            temperature=0.7
        )

        print("✓ API call successful!")
        print()

        # Full response
        print("Full Response Structure:")
        print("-" * 70)
        response_dict = response.model_dump()
        print(json.dumps(response_dict, indent=2, ensure_ascii=False)[:2000])
        print("-" * 70)
        print()

        # Check content
        content = response.choices[0].message.content
        print(f"Content type: {type(content)}")
        print(f"Content length: {len(content) if content else 0}")

        if content:
            if content.startswith('http'):
                print("✅ Response format: URL")
                print(f"Image URL: {content}")

                # Try to download
                import requests
                img_response = requests.get(content, timeout=30)
                if img_response.status_code == 200:
                    output_path = Path("output/test_image.png")
                    output_path.parent.mkdir(exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"✓ Image downloaded: {output_path}")
                    print(f"  Size: {len(img_response.content)} bytes")
            elif 'base64' in content.lower():
                print("✅ Response format: Base64")
                print(f"First 200 chars: {content[:200]}")
            else:
                print("⚠️  Unexpected format")
                print(f"Content: {content[:500]}")
        else:
            print("❌ Empty content!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print()
        print("Full traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_gemini_25_image()
