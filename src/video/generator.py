"""
Video Generator - Main orchestrator for video generation pipeline
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from src.config import VIDEO_OUTPUT_DIR, ENABLE_VIDEO_GENERATION
from src.utils.logger import get_logger

from .tts import TTSGenerator
from .director import VideoDirector
from .pexels import PexelsClient
from .composer import VideoComposer


class VideoGenerator:
    """
    Main video generation pipeline orchestrator.

    Pipeline:
    1. Script → TTS → Audio
    2. Script → Director → Storyboard
    3. Storyboard → Pexels → Video clips
    4. Audio + Clips → Composer → Final video
    """

    def __init__(self):
        self.logger = get_logger('video_generator')
        self.output_dir = Path(VIDEO_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 延迟初始化各模块（按需）
        self._tts = None
        self._director = None
        self._pexels = None
        self._composer = None

        self.logger.info("VideoGenerator initialized")

    @property
    def tts(self) -> TTSGenerator:
        if self._tts is None:
            self._tts = TTSGenerator()
        return self._tts

    @property
    def director(self) -> VideoDirector:
        if self._director is None:
            self._director = VideoDirector()
        return self._director

    @property
    def pexels(self) -> PexelsClient:
        if self._pexels is None:
            self._pexels = PexelsClient()
        return self._pexels

    @property
    def composer(self) -> VideoComposer:
        if self._composer is None:
            self._composer = VideoComposer()
        return self._composer

    def generate_video(
        self,
        script: str,
        date_str: str,
        title: str = "",
        cover_image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete video from script

        Args:
            script: Video script text
            date_str: Date string (YYYY-MM-DD)
            title: Video title
            cover_image: Optional cover image path

        Returns:
            Dict with video_path, audio_path, duration, etc.
        """
        if not ENABLE_VIDEO_GENERATION:
            self.logger.info("Video generation is disabled")
            return {'success': False, 'reason': 'disabled'}

        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting video generation pipeline")
            self.logger.info("=" * 60)

            # 创建工作目录
            work_dir = self.output_dir / date_str
            work_dir.mkdir(parents=True, exist_ok=True)

            clips_dir = work_dir / "clips"
            clips_dir.mkdir(exist_ok=True)

            # Step 1: 生成音频
            self.logger.info("\n[Video Step 1/4] Generating audio with TTS...")
            self.logger.info("  → 正在调用 Fish.audio API...")
            audio_path = str(work_dir / "narration.mp3")
            self.tts.generate_audio(script, audio_path)
            self.logger.info("  ✓ 音频生成完成")

            # 获取音频时长
            try:
                from moviepy import AudioFileClip
            except ImportError:
                from moviepy.editor import AudioFileClip
            with AudioFileClip(audio_path) as audio:
                audio_duration = audio.duration
            self.logger.info(f"Audio duration: {audio_duration:.1f}s")

            # Step 2: 生成分镜
            self.logger.info("\n[Video Step 2/4] Generating storyboard...")
            self.logger.info("  → 正在调用 LLM 分析脚本生成分镜...")
            segments = self.director.generate_storyboard(
                script,
                target_duration=int(audio_duration)
            )
            self.logger.info(f"  ✓ 生成 {len(segments)} 个分镜片段")

            # 调整分镜时长匹配音频
            segments = self.director.sync_with_audio(segments, audio_duration)

            # Step 3: 下载视频素材
            self.logger.info("\n[Video Step 3/4] Downloading video clips from Pexels...")
            self.logger.info(f"  → 需要下载 {len(segments)} 个视频片段...")
            segments = self.pexels.download_videos_for_segments(
                segments,
                str(clips_dir)
            )
            self.logger.info("  ✓ 视频素材下载完成")

            # Step 4: 合成视频
            self.logger.info("\n[Video Step 4/4] Composing final video...")
            self.logger.info("  → 正在合成视频（这一步可能需要1-3分钟）...")
            video_filename = f"blockchain-daily-{date_str}.mp4"
            video_path = str(work_dir / video_filename)

            self.composer.compose_video(
                segments=segments,
                audio_path=audio_path,
                output_path=video_path,
                cover_image=cover_image
            )
            self.logger.info("  ✓ 视频合成完成")

            # 获取最终视频信息
            final_duration = self.composer.get_video_duration(video_path)
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB

            self.logger.info("\n" + "=" * 60)
            self.logger.info("Video generation completed!")
            self.logger.info(f"  Output: {video_path}")
            self.logger.info(f"  Duration: {final_duration:.1f}s")
            self.logger.info(f"  Size: {file_size:.1f}MB")
            self.logger.info("=" * 60)

            # 清理临时文件（可选）
            # shutil.rmtree(clips_dir)

            return {
                'success': True,
                'video_path': video_path,
                'audio_path': audio_path,
                'duration': final_duration,
                'file_size_mb': file_size,
                'segments_count': len(segments)
            }

        except Exception as e:
            self.logger.error(f"Video generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def generate_video_simple(
        self,
        article_data: Dict[str, Any],
        date_str: str
    ) -> Dict[str, Any]:
        """
        Simplified video generation from article data

        Args:
            article_data: Dict with 'content', 'title', 'cover_image' etc
            date_str: Date string

        Returns:
            Generation result
        """
        script = article_data.get('content', '')
        title = article_data.get('title', '')
        cover_image = article_data.get('cover_image')

        # 如果有单独的封面图路径
        if not cover_image:
            # 尝试从输出目录找封面
            cover_candidates = [
                f"output/images/cover_{date_str}.png",
                f"output/images/cover_{date_str}.jpg",
            ]
            for candidate in cover_candidates:
                if os.path.exists(candidate):
                    cover_image = candidate
                    break

        return self.generate_video(
            script=script,
            date_str=date_str,
            title=title,
            cover_image=cover_image
        )
