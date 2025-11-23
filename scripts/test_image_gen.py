"""
Test Image Generation API
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, GEMINI_IMAGE_MODEL

def test_image_generation():
    """Test image generation with Nano Banana Pro"""

    print("=" * 60)
    print("Testing Image Generation API")
    print("=" * 60)
    print(f"Model: {GEMINI_IMAGE_MODEL}")
    print(f"API Base URL: {OPENROUTER_BASE_URL}")
    print()

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )

    # Simple test prompt
    test_prompt = """Create a professional business infographic titled '区块链市场动态' (Blockchain Market Dynamics).
Layout: vertical composition with header, 3 key statistics sections, and footer.
Include: bold Chinese title at top, three large numbers with icons (representing market cap, trading volume, growth rate),
trend chart showing upward movement, modern blue-green gradient color scheme, clean white background,
professional business presentation style.
Text: clearly readable Chinese labels and percentage numbers.
Style: minimalist, data-driven, suitable for PowerPoint presentation."""

    print("Test Prompt:")
    print("-" * 60)
    print(test_prompt)
    print("-" * 60)
    print()

    try:
        print("Calling API...")
        response = client.chat.completions.create(
            model=GEMINI_IMAGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": test_prompt
                }
            ],
            max_tokens=4000,
            temperature=0.7
        )

        print("✓ API call successful!")
        print()
        print("Response object:")
        print(f"  ID: {response.id}")
        print(f"  Model: {response.model}")
        print(f"  Created: {response.created}")
        print()

        result = response.choices[0].message.content
        print("Response content:")
        print("-" * 60)
        print(f"Type: {type(result)}")
        print(f"Length: {len(result) if result else 0}")
        print(f"Content preview: {result[:500] if result else 'None'}")
        print("-" * 60)
        print()

        # Check response format
        if result:
            if result.startswith('http'):
                print("✓ Response format: URL")
                print(f"  URL: {result}")
            elif 'base64' in result.lower():
                print("✓ Response format: Base64 encoded data")
            else:
                print("⚠ Unknown response format")
                print(f"  Full content:\n{result}")
        else:
            print("❌ Empty response!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print()
        print("Full traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_image_generation()
