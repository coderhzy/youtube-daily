#!/usr/bin/env python3
"""
Video generation test script
本地测试视频生成流程
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import os

def test_tts():
    """测试TTS模块"""
    print("\n" + "="*50)
    print("Testing TTS (Fish.audio)")
    print("="*50)

    from src.video.tts import TTSGenerator

    try:
        tts = TTSGenerator()
        test_text = "大家好，欢迎来到区块链每日观察。今天比特币价格突破了10万美元大关。"
        output_path = "output/test_audio.mp3"

        tts.generate_audio(test_text, output_path)
        print(f"✓ TTS test passed! Audio saved to: {output_path}")
        return True
    except Exception as e:
        print(f"✗ TTS test failed: {e}")
        return False


def test_director():
    """测试分镜模块"""
    print("\n" + "="*50)
    print("Testing Video Director (LLM)")
    print("="*50)

    from src.video.director import VideoDirector

    try:
        director = VideoDirector()

        test_script = """
大家好，欢迎来到区块链每日观察。

## 市场行情

今天比特币价格突破了10万美元大关，创下历史新高。
以太坊也随之上涨，突破4000美元。
整个加密市场情绪高涨，恐惧贪婪指数达到90，处于极度贪婪状态。

## 政策动态

美国SEC主席表示将对加密货币采取更加开放的态度。
这一消息刺激市场进一步上涨。
        """

        segments = director.generate_storyboard(test_script, target_duration=60)
        print(f"✓ Director test passed! Generated {len(segments)} segments:")
        for i, seg in enumerate(segments[:3]):
            print(f"  {i+1}. [{seg.get('duration', 0)}s] {seg.get('keyword', '')[:40]}...")
        return True
    except Exception as e:
        print(f"✗ Director test failed: {e}")
        return False


def test_pexels():
    """测试Pexels模块"""
    print("\n" + "="*50)
    print("Testing Pexels API")
    print("="*50)

    from src.video.pexels import PexelsClient

    try:
        pexels = PexelsClient()

        # 测试搜索
        video = pexels.search_video("Bitcoin cryptocurrency")
        if video:
            print(f"✓ Found video: {video.get('url', 'N/A')}")
            print(f"  Duration: {video.get('duration', 0)}s")

            # 测试下载
            output_path = "output/test_clip.mp4"
            downloaded = pexels.download_video("Bitcoin cryptocurrency", output_path)
            if downloaded:
                print(f"✓ Video downloaded to: {output_path}")
                return True
        else:
            print("✗ No video found")
            return False
    except Exception as e:
        print(f"✗ Pexels test failed: {e}")
        return False


def test_composer():
    """测试视频合成（需要先有素材）"""
    print("\n" + "="*50)
    print("Testing Video Composer (MoviePy)")
    print("="*50)

    from src.video.composer import VideoComposer

    try:
        composer = VideoComposer()
        print(f"✓ Composer initialized, resolution: {composer.resolution}")
        return True
    except Exception as e:
        print(f"✗ Composer test failed: {e}")
        return False


def test_full_pipeline():
    """测试完整流程"""
    print("\n" + "="*50)
    print("Testing Full Video Generation Pipeline")
    print("="*50)

    from src.video import VideoGenerator

    try:
        generator = VideoGenerator()

        test_script = """
大家好，欢迎来到区块链每日观察。

今天我们来聊聊比特币市场的最新动态。

比特币价格今天突破了历史新高，市场情绪非常火热。
机构投资者持续加仓，显示出对加密货币的长期信心。

同时，以太坊生态也在快速发展，DeFi总锁仓量创新高。

感谢收看，我们下期再见！
        """

        result = generator.generate_video(
            script=test_script,
            date_str="2024-test",
            title="测试视频"
        )

        if result.get('success'):
            print(f"✓ Full pipeline test passed!")
            print(f"  Video: {result['video_path']}")
            print(f"  Duration: {result['duration']:.1f}s")
            print(f"  Size: {result['file_size_mb']:.1f}MB")
            return True
        else:
            print(f"✗ Pipeline test failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"✗ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("VIDEO GENERATION TEST SUITE")
    print("="*60)

    # 确保输出目录存在
    Path("output").mkdir(exist_ok=True)

    # 检查环境变量
    print("\nChecking environment variables...")
    required_vars = {
        'FISH_AUDIO_API_KEY': os.getenv('FISH_AUDIO_API_KEY'),
        'PEXELS_API_KEY': os.getenv('PEXELS_API_KEY'),
        'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
    }

    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print(f"⚠ Missing environment variables: {', '.join(missing)}")
        print("Please set them in .env file")
    else:
        print("✓ All required environment variables are set")

    # 运行测试
    results = {}

    if os.getenv('OPENROUTER_API_KEY'):
        results['Director'] = test_director()

    if os.getenv('PEXELS_API_KEY'):
        results['Pexels'] = test_pexels()

    if os.getenv('FISH_AUDIO_API_KEY'):
        results['TTS'] = test_tts()

    results['Composer'] = test_composer()

    # 如果所有组件都通过，测试完整流程
    if all(results.values()) and len(results) >= 4:
        print("\nAll component tests passed, running full pipeline test...")
        results['Full Pipeline'] = test_full_pipeline()

    # 汇总
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("="*60))
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
