"""
Video Composer - MoviePy-based video assembly
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.config import VIDEO_RESOLUTION, VIDEO_FPS, VIDEO_OUTPUT_DIR
from src.utils.logger import get_logger

# MoviePy 2.x 兼容导入
MOVIEPY_V2 = None
VideoFileClip = None
AudioFileClip = None
ImageClip = None
ColorClip = None
TextClip = None
concatenate_videoclips = None
CompositeVideoClip = None
vfx = None

try:
    # MoviePy 2.x
    from moviepy import VideoFileClip, AudioFileClip, ImageClip, ColorClip, TextClip
    from moviepy import concatenate_videoclips, CompositeVideoClip
    import moviepy.video.fx as vfx
    MOVIEPY_V2 = True
except ImportError:
    try:
        # MoviePy 1.x
        from moviepy.editor import (
            VideoFileClip, AudioFileClip, ImageClip, ColorClip, TextClip,
            concatenate_videoclips, CompositeVideoClip
        )
        from moviepy.editor import vfx
        MOVIEPY_V2 = False
    except ImportError:
        pass


class VideoComposer:
    """Compose final video from clips, audio, and overlays"""

    def __init__(self):
        self.logger = get_logger('video_composer')
        self.resolution = VIDEO_RESOLUTION
        self.fps = VIDEO_FPS
        self.output_dir = Path(VIDEO_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 检查MoviePy是否可用
        if VideoFileClip is None:
            import sys
            raise ImportError(
                f"MoviePy not installed in current environment.\n"
                f"Python: {sys.executable}\n"
                f"Run: {sys.executable} -m pip install moviepy"
            )

        self.logger.info(f"VideoComposer initialized (MoviePy {'2.x' if MOVIEPY_V2 else '1.x'})")

    def compose_video(
        self,
        segments: List[Dict[str, Any]],
        audio_path: str,
        output_path: str,
        cover_image: Optional[str] = None,
        add_subtitles: bool = False
    ) -> str:
        """
        Compose final video from segments and audio

        Args:
            segments: List of segments with 'video_path' and 'duration'
            audio_path: Path to audio file
            output_path: Output video path
            cover_image: Optional cover image for intro
            add_subtitles: Whether to add subtitles

        Returns:
            Path to output video
        """

        try:
            self.logger.info(f"Composing video from {len(segments)} segments...")

            # 加载音频获取总时长
            audio = AudioFileClip(audio_path)
            total_duration = audio.duration
            self.logger.info(f"Audio duration: {total_duration:.1f}s")

            # 构建视频片段
            from tqdm import tqdm

            clips = []
            pbar = tqdm(segments, desc="处理视频片段", unit="clip", ncols=80)

            for i, segment in enumerate(pbar):
                video_path = segment.get('video_path')
                target_duration = segment.get('duration', 8)

                if not video_path or not os.path.exists(video_path):
                    # 不应该发生 - Pexels客户端保证返回视频
                    raise ValueError(f"视频片段 {i} 没有有效的视频文件: {video_path}")

                pbar.set_postfix_str(f"clip_{i:03d}")
                clip = self._process_clip(video_path, target_duration)

                if clip:
                    clips.append(clip)

            pbar.close()

            if not clips:
                raise ValueError("No valid video clips to compose")

            # 添加封面（如果有）
            if cover_image and os.path.exists(cover_image):
                intro = self._create_intro(cover_image, duration=3)
                clips.insert(0, intro)

            # 拼接所有片段
            self.logger.info("Concatenating clips...")
            final_video = concatenate_videoclips(clips, method="compose")

            # 调整视频长度匹配音频
            if abs(final_video.duration - total_duration) > 1:
                self.logger.info(f"Adjusting video duration: {final_video.duration:.1f}s -> {total_duration:.1f}s")
                if final_video.duration > total_duration:
                    if MOVIEPY_V2:
                        final_video = final_video.subclipped(0, total_duration)
                    else:
                        final_video = final_video.subclip(0, total_duration)
                else:
                    # 视频太短，循环最后一个片段
                    if MOVIEPY_V2:
                        final_video = final_video.with_effects([vfx.Loop(duration=total_duration)])
                    else:
                        final_video = final_video.fx(vfx.loop, duration=total_duration)

            # 合成音频
            if MOVIEPY_V2:
                final_video = final_video.with_audio(audio)
            else:
                final_video = final_video.set_audio(audio)

            # 导出
            self.logger.info(f"Exporting video to: {output_path}")
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                threads=4,
                preset='medium',
                logger=None  # 禁用moviepy的进度条
            )

            # 清理
            final_video.close()
            audio.close()
            for clip in clips:
                clip.close()

            self.logger.info(f"Video composed successfully: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Video composition failed: {e}")
            raise

    def _process_clip(self, video_path: str, target_duration: float):
        """Process a single video clip with creative editing"""
        import random

        try:
            clip = VideoFileClip(video_path)
            original_duration = clip.duration

            # 随机选择起始点（不总是从头开始，更有变化）
            if original_duration > target_duration + 2:
                max_start = original_duration - target_duration - 1
                start_time = random.uniform(0, max_start)
                end_time = start_time + target_duration

                if MOVIEPY_V2:
                    clip = clip.subclipped(start_time, end_time)
                else:
                    clip = clip.subclip(start_time, end_time)
            elif original_duration > target_duration:
                # 素材刚好够，从随机位置截取
                start_time = random.uniform(0, original_duration - target_duration)
                if MOVIEPY_V2:
                    clip = clip.subclipped(start_time, start_time + target_duration)
                else:
                    clip = clip.subclip(start_time, start_time + target_duration)
            else:
                # 素材不够，循环播放
                if MOVIEPY_V2:
                    clip = clip.with_effects([vfx.Loop(duration=target_duration)])
                else:
                    clip = vfx.loop(clip, duration=target_duration)

            # 随机微调速度（0.95-1.05），增加自然感
            speed_factor = random.uniform(0.95, 1.05)
            if MOVIEPY_V2:
                clip = clip.with_effects([vfx.MultiplySpeed(speed_factor)])
            else:
                clip = clip.fx(vfx.speedx, speed_factor)

            # 调整分辨率
            clip = self._resize_clip(clip)

            # 添加淡入淡出转场
            fade_duration = 0.4
            if MOVIEPY_V2:
                clip = clip.with_effects([
                    vfx.FadeIn(fade_duration),
                    vfx.FadeOut(fade_duration)
                ])
            else:
                clip = clip.fx(vfx.fadein, fade_duration).fx(vfx.fadeout, fade_duration)

            return clip

        except Exception as e:
            self.logger.error(f"Failed to process clip {video_path}: {e}")
            return self._create_placeholder(target_duration)

    def _resize_clip(self, clip):
        """Resize and crop clip to target resolution"""
        target_w, target_h = self.resolution
        target_ratio = target_w / target_h

        clip_ratio = clip.w / clip.h

        if clip_ratio > target_ratio:
            # 视频更宽，按高度缩放后裁剪宽度
            if MOVIEPY_V2:
                clip = clip.resized(height=target_h)
            else:
                clip = clip.resize(height=target_h)
            # 居中裁剪
            x_center = clip.w / 2
            clip = clip.cropped(
                x1=x_center - target_w / 2,
                x2=x_center + target_w / 2,
                y1=0,
                y2=target_h
            ) if MOVIEPY_V2 else clip.crop(
                x1=x_center - target_w / 2,
                x2=x_center + target_w / 2,
                y1=0,
                y2=target_h
            )
        else:
            # 视频更高，按宽度缩放后裁剪高度
            if MOVIEPY_V2:
                clip = clip.resized(width=target_w)
            else:
                clip = clip.resize(width=target_w)
            y_center = clip.h / 2
            clip = clip.cropped(
                x1=0,
                x2=target_w,
                y1=y_center - target_h / 2,
                y2=y_center + target_h / 2
            ) if MOVIEPY_V2 else clip.crop(
                x1=0,
                x2=target_w,
                y1=y_center - target_h / 2,
                y2=y_center + target_h / 2
            )

        return clip

    def _create_placeholder(self, duration: float):
        """Create a placeholder clip with gradient effect"""
        import numpy as np

        # 创建一个深蓝色渐变背景，比纯黑好看
        def make_gradient_frame(t):
            """Generate a subtle animated gradient"""
            w, h = self.resolution
            # 创建垂直渐变：从深蓝到更深的蓝
            gradient = np.zeros((h, w, 3), dtype=np.uint8)
            for y in range(h):
                # 深蓝色渐变 (15,25,45) 到 (5,10,25)
                ratio = y / h
                r = int(15 - 10 * ratio)
                g = int(25 - 15 * ratio)
                b = int(45 - 20 * ratio)
                gradient[y, :] = [r, g, b]
            return gradient

        try:
            # 使用 make_frame 创建动态背景
            from moviepy import VideoClip
            clip = VideoClip(make_gradient_frame, duration=duration)
            if MOVIEPY_V2:
                clip = clip.with_fps(self.fps)
            else:
                clip = clip.set_fps(self.fps)
            return clip
        except Exception:
            # 如果动态背景失败，回退到静态颜色
            return ColorClip(
                size=self.resolution,
                color=(15, 25, 45),  # 深蓝色
                duration=duration
            )

    def _create_intro(self, image_path: str, duration: float = 3):
        """Create intro from cover image"""
        try:
            intro = ImageClip(image_path, duration=duration)
            intro = self._resize_clip(intro)
            if MOVIEPY_V2:
                intro = intro.with_effects([
                    vfx.FadeIn(0.5),
                    vfx.FadeOut(0.5)
                ])
            else:
                intro = intro.fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5)
            return intro
        except Exception as e:
            self.logger.error(f"Failed to create intro: {e}")
            return self._create_placeholder(duration)

    def add_watermark(
        self,
        video_path: str,
        watermark_text: str = "区块链每日观察",
        output_path: Optional[str] = None
    ) -> str:
        """Add watermark to video"""
        try:
            video = VideoFileClip(video_path)

            # 创建水印
            watermark = TextClip(
                text=watermark_text,
                font_size=24,
                color='white',
                font='PingFang-SC-Regular'  # macOS 中文字体
            )

            if MOVIEPY_V2:
                watermark = watermark.with_opacity(0.6).with_position(('right', 'bottom')).with_duration(video.duration)
            else:
                watermark = watermark.set_opacity(0.6).set_position(('right', 'bottom')).set_duration(video.duration)

            # 合成
            final = CompositeVideoClip([video, watermark])

            output = output_path or video_path.replace('.mp4', '_watermarked.mp4')
            final.write_videofile(output, fps=self.fps, codec='libx264', audio_codec='aac')

            video.close()
            final.close()

            return output

        except Exception as e:
            self.logger.error(f"Failed to add watermark: {e}")
            return video_path

    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        with VideoFileClip(video_path) as clip:
            return clip.duration
