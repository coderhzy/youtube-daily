"""
Detailed Image Generation API Test
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, GEMINI_IMAGE_MODEL

def test_detailed():
    """Test with full response inspection"""

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )

    test_prompt = "Create a simple infographic with the title 'Test Image' in Chinese (测试图片)"

    print("Testing Image Generation API - Detailed Response")
    print("=" * 70)
    print()

    try:
        response = client.chat.completions.create(
            model=GEMINI_IMAGE_MODEL,
            messages=[{"role": "user", "content": test_prompt}],
            max_tokens=4000,
            temperature=0.7
        )

        print("✓ API Response Received")
        print()

        # Full response as dict
        print("Full Response Object:")
        print("-" * 70)
        response_dict = response.model_dump()
        print(json.dumps(response_dict, indent=2, ensure_ascii=False))
        print("-" * 70)
        print()

        # Check choices
        print(f"Number of choices: {len(response.choices)}")
        if response.choices:
            choice = response.choices[0]
            print(f"Choice[0] finish_reason: {choice.finish_reason}")
            print(f"Choice[0] message role: {choice.message.role}")
            print(f"Choice[0] message content type: {type(choice.message.content)}")
            print(f"Choice[0] message content: {choice.message.content}")

            # Check for additional fields
            print()
            print("Message object attributes:")
            for attr in dir(choice.message):
                if not attr.startswith('_'):
                    try:
                        value = getattr(choice.message, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except:
                        pass

        # Check usage
        if hasattr(response, 'usage') and response.usage:
            print()
            print("Token Usage:")
            print(f"  Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  Completion tokens: {response.usage.completion_tokens}")
            print(f"  Total tokens: {response.usage.total_tokens}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_detailed()
