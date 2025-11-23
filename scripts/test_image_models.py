"""
Test different image generation models on OpenRouter
To find one that works for PPT-style infographics
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

def test_image_model(client, model_name, prompt):
    """Test a single image generation model"""
    print(f"\n{'='*70}")
    print(f"Testing: {model_name}")
    print('='*70)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=4000,
            temperature=0.7
        )

        content = response.choices[0].message.content

        if content:
            if content.startswith('http'):
                print(f"✅ SUCCESS - Returns URL")
                print(f"   URL: {content[:100]}...")
                return True, "url"
            elif 'base64' in content.lower() or len(content) > 1000:
                print(f"✅ SUCCESS - Returns base64 data")
                print(f"   Data length: {len(content)} chars")
                return True, "base64"
            else:
                print(f"⚠️  PARTIAL - Returns text")
                print(f"   Content: {content[:200]}")
                return False, "text"
        else:
            print(f"❌ FAILED - Empty response")
            return False, "empty"

    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f"❌ Model not available on OpenRouter")
        else:
            print(f"❌ Error: {e}")
        return False, "error"

def main():
    """Test available image generation models"""

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )

    # PPT-style infographic prompt
    ppt_prompt = """Create a professional PowerPoint-style infographic about blockchain technology.
Style: Clean, modern business presentation
Layout: Title at top, 3 key points with icons, professional color scheme (blue/purple gradient)
Text: Bold headings, bullet points, suitable for presentation slides
Format: Horizontal layout (16:9), high contrast for projection"""

    print("🎯 Testing Image Generation Models for PPT-Style Infographics")
    print("="*70)

    # Models to test (from most likely to work)
    test_models = [
        # Free/cheap options
        ("google/gemini-2.0-flash-exp:free", "Gemini Flash (Free - with image understanding)"),
        ("meta-llama/llama-3.2-90b-vision-instruct:free", "Llama Vision (Free)"),

        # Image generation specific (if available)
        ("black-forest-labs/flux-1.1-pro", "FLUX 1.1 Pro (Best quality)"),
        ("black-forest-labs/flux-pro", "FLUX Pro"),
        ("black-forest-labs/flux-dev", "FLUX Dev"),
        ("stability-ai/stable-diffusion-xl", "Stable Diffusion XL"),

        # OpenAI (expensive but reliable)
        ("openai/dall-e-3", "DALL-E 3"),

        # Google
        ("google/gemini-3-pro-image-preview", "Gemini 3 Pro Image (Current)"),
    ]

    results = []

    for model_id, description in test_models:
        print(f"\n📋 {description}")
        success, response_type = test_image_model(client, model_id, ppt_prompt)
        results.append({
            'model': model_id,
            'description': description,
            'success': success,
            'type': response_type
        })

    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)

    working_models = [r for r in results if r['success']]

    if working_models:
        print(f"\n✅ Working models ({len(working_models)}):")
        for r in working_models:
            print(f"   • {r['description']}")
            print(f"     Model ID: {r['model']}")
            print(f"     Response type: {r['type']}")
            print()

        print("💡 Recommendation:")
        print(f"   Use: {working_models[0]['model']}")
        print()
        print("   Update your .env file:")
        print(f"   GEMINI_IMAGE_MODEL={working_models[0]['model']}")
    else:
        print("\n❌ No working image generation models found")
        print("\n💡 Alternative solution:")
        print("   Consider using external image generation APIs:")
        print("   • Replicate API (FLUX, Stable Diffusion)")
        print("   • Stability AI API")
        print("   • OpenAI DALL-E API directly")
        print("   • Midjourney API")

if __name__ == "__main__":
    main()
