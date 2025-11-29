"""
TTS Generator using Fish.audio API
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.config import FISH_AUDIO_API_KEY, FISH_AUDIO_VOICE_ID
from src.utils.logger import get_logger


class TTSGenerator:
    """Text-to-Speech generator using Fish.audio"""

    def __init__(self):
        self.logger = get_logger('tts_generator')

        if not FISH_AUDIO_API_KEY:
            raise ValueError("FISH_AUDIO_API_KEY must be set in environment variables")

        self._use_legacy_sdk = False

        try:
            from fishaudio import FishAudio
            self.client = FishAudio(api_key=FISH_AUDIO_API_KEY)
            self.logger.info("Using new fishaudio SDK")
        except ImportError:
            # 尝试旧版SDK
            try:
                import fish_audio_sdk
                self.client = fish_audio_sdk.Session(FISH_AUDIO_API_KEY)
                self._use_legacy_sdk = True
                self.logger.info("Using legacy fish_audio_sdk")
            except ImportError:
                raise ImportError("Please install fish-audio-sdk: pip install fish-audio-sdk")

        self.voice_id = FISH_AUDIO_VOICE_ID
        self.logger.info(f"TTS Generator initialized with voice: {self.voice_id or 'default'}")

    def generate_audio(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        use_preprocessor: bool = True
    ) -> str:
        """
        Generate audio from text

        Args:
            text: Text to convert to speech
            output_path: Output file path
            voice_id: Optional voice ID (uses default if not specified)
            use_preprocessor: Whether to use TTS preprocessor for emotion tags

        Returns:
            Path to generated audio file
        """
        try:
            self.logger.info(f"Generating audio for {len(text)} characters...")

            # 使用预处理器添加情绪标签
            if use_preprocessor:
                from .tts_preprocessor import TTSPreprocessor
                preprocessor = TTSPreprocessor()
                clean_text = preprocessor.process(text)
            else:
                # 简单清理
                clean_text = self._clean_text(text)

            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            vid = voice_id or self.voice_id

            if self._use_legacy_sdk:
                return self._generate_with_legacy_sdk(clean_text, output_path, vid)
            else:
                return self._generate_with_new_sdk(clean_text, output_path, vid)

        except Exception as e:
            self.logger.error(f"TTS generation failed: {e}")
            raise

    def _generate_with_new_sdk(self, text: str, output_path: str, voice_id: str) -> str:
        """Generate audio using new fishaudio SDK"""
        from fishaudio import TTSConfig
        from fishaudio.utils import save

        config = TTSConfig(
            reference_id=voice_id if voice_id else None,
            format="mp3",
        )

        audio = self.client.tts.convert(text=text, config=config)
        save(audio, output_path)

        self.logger.info(f"Audio saved to: {output_path}")
        return output_path

    def _generate_with_legacy_sdk(self, text: str, output_path: str, voice_id: str) -> str:
        """Generate audio using legacy fish_audio_sdk"""
        import fish_audio_sdk

        with open(output_path, 'wb') as f:
            for chunk in self.client.tts(
                fish_audio_sdk.TTSRequest(
                    text=text,
                    reference_id=voice_id if voice_id else None,
                    format="mp3",
                )
            ):
                f.write(chunk)

        self.logger.info(f"Audio saved to: {output_path}")
        return output_path

    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        # 移除Markdown格式
        clean = re.sub(r'#{1,6}\s*', '', text)  # 移除标题标记
        clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)  # 移除粗体
        clean = re.sub(r'\*([^*]+)\*', r'\1', clean)  # 移除斜体
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)  # 移除链接
        clean = re.sub(r'```[^`]+```', '', clean)  # 移除代码块
        clean = re.sub(r'`([^`]+)`', r'\1', clean)  # 移除行内代码
        clean = re.sub(r'^[-*]\s+', '', clean, flags=re.MULTILINE)  # 移除列表标记
        clean = re.sub(r'^>\s+', '', clean, flags=re.MULTILINE)  # 移除引用
        clean = re.sub(r'---+', '', clean)  # 移除分隔线

        # 移除表情符号（保留中文标点）
        clean = re.sub(r'[📊🏛️💰🔧💼✨✓⚠️❌✅]', '', clean)

        # 清理多余空白
        clean = re.sub(r'\n{3,}', '\n\n', clean)
        clean = clean.strip()

        return clean

    def generate_audio_segments(
        self,
        segments: List[Dict[str, Any]],
        output_dir: str,
        voice_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate audio for multiple text segments

        Args:
            segments: List of segment dicts with 'text' key
            output_dir: Directory to save audio files
            voice_id: Optional voice ID

        Returns:
            List of segments with 'audio_path' added
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        results = []
        for i, segment in enumerate(segments):
            text = segment.get('text', '')
            if not text.strip():
                continue

            audio_path = os.path.join(output_dir, f"segment_{i:03d}.mp3")

            try:
                self.generate_audio(text, audio_path, voice_id)
                segment_result = segment.copy()
                segment_result['audio_path'] = audio_path
                results.append(segment_result)
            except Exception as e:
                self.logger.error(f"Failed to generate audio for segment {i}: {e}")
                continue

        self.logger.info(f"Generated {len(results)} audio segments")
        return results
