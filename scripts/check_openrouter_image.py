"""
Check OpenRouter API for image generation models
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

def check_available_models():
    """Check what image generation models are available on OpenRouter"""

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )

    print("=" * 70)
    print("Checking OpenRouter for Image Generation Models")
    print("=" * 70)
    print()

    # List of potential image generation models to test
    test_models = [
        "google/gemini-3-pro-image-preview",
        "google/imagen-3.0-generate-001",
        "google/imagen-2",
        "stability-ai/stable-diffusion-xl",
        "openai/dall-e-3",
        "midjourney",
    ]

    for model in test_models:
        print(f"\nTesting: {model}")
        print("-" * 70)

        try:
            # Try to create a simple image
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": "Create a simple test image"
                }],
                max_tokens=1000,
                temperature=0.7
            )

            print(f"✓ Model accessible!")
            print(f"  Response type: {type(response.choices[0].message.content)}")
            print(f"  Content length: {len(response.choices[0].message.content or '')}")

            # Check for reasoning
            if hasattr(response.choices[0].message, 'reasoning'):
                print(f"  Has reasoning field: Yes")

            # Check content
            content = response.choices[0].message.content
            if content:
                if content.startswith('http'):
                    print(f"  Format: URL")
                    print(f"  URL: {content}")
                elif 'base64' in content.lower():
                    print(f"  Format: Base64")
                else:
                    print(f"  Format: Unknown")
                    print(f"  Preview: {content[:200]}")
            else:
                print(f"  ⚠ Empty content!")

        except Exception as e:
            error_str = str(e)
            if "not found" in error_str.lower() or "does not exist" in error_str.lower():
                print(f"✗ Model not available")
            elif "not supported" in error_str.lower():
                print(f"✗ Model doesn't support this operation")
            else:
                print(f"✗ Error: {e}")

if __name__ == "__main__":
    check_available_models()
