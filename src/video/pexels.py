"""
Pexels API Client for video stock footage
"""

import os
import random
import hashlib
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
import urllib.request

from src.config import (
    PEXELS_API_KEY,
    VIDEO_ORIENTATION,
    FALLBACK_ASSETS_DIR
)
from src.utils.logger import get_logger


class PexelsClient:
    """Client for Pexels video API"""

    BASE_URL = "https://api.pexels.com/videos/search"

    # 备用关键词列表 - 这些在 Pexels 上一定有很多结果
    FALLBACK_QUERIES = [
        "technology abstract blue",
        "digital network data",
        "city skyline night",
        "business office meeting",
        "computer screen code",
        "futuristic technology",
        "financial chart graph",
        "global network connection",
        "data visualization",
        "modern office workspace"
    ]

    def __init__(self, cache_dir: str = "cache/pexels"):
        self.logger = get_logger('pexels_client')

        if not PEXELS_API_KEY:
            raise ValueError("PEXELS_API_KEY must be set in environment variables")

        self.api_key = PEXELS_API_KEY
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.fallback_dir = Path(FALLBACK_ASSETS_DIR)

        self.logger.info("Pexels client initialized")

    def search_video(
        self,
        query: str,
        orientation: str = None,
        min_duration: int = 5,
        per_page: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a video on Pexels

        Args:
            query: Search query (English)
            orientation: landscape/portrait/square
            min_duration: Minimum video duration in seconds
            per_page: Number of results to fetch

        Returns:
            Video data dict or None
        """
        try:
            headers = {"Authorization": self.api_key}
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": orientation or VIDEO_ORIENTATION,
                "size": "medium"  # medium is usually HD (1080p)
            }

            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data.get("total_results", 0) == 0:
                self.logger.warning(f"No results for query: {query}")
                return None

            # 过滤符合时长要求的视频
            videos = data.get("videos", [])
            suitable = [v for v in videos if v.get("duration", 0) >= min_duration]

            if not suitable:
                suitable = videos  # 如果都不符合时长，用全部

            # 随机选一个避免重复
            video = random.choice(suitable)

            return video

        except requests.RequestException as e:
            self.logger.error(f"Pexels API error: {e}")
            return None

    def get_download_url(
        self,
        video_data: Dict[str, Any],
        min_width: int = 1280
    ) -> Optional[str]:
        """
        Get download URL for video

        Args:
            video_data: Video data from search
            min_width: Minimum video width

        Returns:
            Download URL or None
        """
        video_files = video_data.get("video_files", [])

        if not video_files:
            return None

        # 找到合适尺寸的文件
        suitable = [v for v in video_files if v.get("width", 0) >= min_width]

        if suitable:
            # 选择最小的合适尺寸（避免下载太大的文件）
            suitable.sort(key=lambda x: x.get("width", 0))
            return suitable[0].get("link")
        else:
            # 选择最大的
            video_files.sort(key=lambda x: x.get("width", 0), reverse=True)
            return video_files[0].get("link")

    def download_video(
        self,
        query: str,
        output_path: str,
        min_duration: int = 5
    ) -> str:
        """
        Search and download a video - GUARANTEED to return a video path

        Args:
            query: Search query
            output_path: Path to save video
            min_duration: Minimum duration in seconds

        Returns:
            Path to downloaded video (always returns a valid path)
        """
        import shutil

        # 检查缓存
        cache_key = hashlib.md5(query.encode()).hexdigest()[:16]
        cache_path = self.cache_dir / f"{cache_key}.mp4"

        if cache_path.exists():
            self.logger.info(f"Using cached video for: {query}")
            shutil.copy(cache_path, output_path)
            return output_path

        # 搜索视频
        video_data = self.search_video(query, min_duration=min_duration)

        if video_data:
            download_url = self.get_download_url(video_data)
            if download_url:
                try:
                    self.logger.info(f"Downloading video for: {query}")
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Referer': 'https://www.pexels.com/'
                    }
                    req = urllib.request.Request(download_url, headers=headers)

                    with urllib.request.urlopen(req, timeout=60) as response:
                        with open(str(cache_path), 'wb') as f:
                            f.write(response.read())

                    shutil.copy(cache_path, output_path)
                    self.logger.info(f"Video downloaded: {output_path}")
                    return output_path

                except Exception as e:
                    self.logger.warning(f"Download failed for '{query}': {e}")

        # 原始查询失败，使用备用方案（必须成功）
        return self._get_fallback_video_guaranteed(output_path)

    def _get_fallback_video_guaranteed(self, output_path: str) -> str:
        """
        Get a fallback video - GUARANTEED to return a valid video path
        Will try multiple strategies until one succeeds
        """
        import shutil

        # 策略1: 使用本地备用视频
        if self.fallback_dir.exists():
            fallback_videos = list(self.fallback_dir.glob("*.mp4"))
            if fallback_videos:
                fallback = random.choice(fallback_videos)
                shutil.copy(fallback, output_path)
                self.logger.info(f"Using local fallback: {fallback.name}")
                return output_path

        # 策略2: 使用已缓存的任意视频
        cached_videos = list(self.cache_dir.glob("*.mp4"))
        if cached_videos:
            cached = random.choice(cached_videos)
            shutil.copy(cached, output_path)
            self.logger.info(f"Using cached video: {cached.name}")
            return output_path

        # 策略3: 尝试所有备用关键词直到成功
        self.logger.info("Trying ALL fallback queries from Pexels...")
        random.shuffle(self.FALLBACK_QUERIES)

        for fallback_query in self.FALLBACK_QUERIES:
            self.logger.info(f"Trying: {fallback_query}")

            video_data = self.search_video(fallback_query, min_duration=3)
            if not video_data:
                continue

            download_url = self.get_download_url(video_data)
            if not download_url:
                continue

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Referer': 'https://www.pexels.com/'
                }
                req = urllib.request.Request(download_url, headers=headers)

                cache_key = hashlib.md5(fallback_query.encode()).hexdigest()[:16]
                cache_path = self.cache_dir / f"{cache_key}.mp4"

                with urllib.request.urlopen(req, timeout=60) as response:
                    with open(str(cache_path), 'wb') as f:
                        f.write(response.read())

                shutil.copy(cache_path, output_path)
                self.logger.info(f"Downloaded fallback: {fallback_query}")
                return output_path

            except Exception as e:
                self.logger.warning(f"Failed: {fallback_query} - {e}")
                continue

        # 策略4: 最后的备用 - 再次检查缓存（可能上面的尝试已经缓存了一些）
        cached_videos = list(self.cache_dir.glob("*.mp4"))
        if cached_videos:
            cached = random.choice(cached_videos)
            shutil.copy(cached, output_path)
            self.logger.info(f"Using newly cached video: {cached.name}")
            return output_path

        # 如果真的全部失败，抛出异常让用户知道
        raise RuntimeError(
            "无法获取任何视频素材！请检查:\n"
            "1. PEXELS_API_KEY 是否正确\n"
            "2. 网络连接是否正常\n"
            "3. 可以手动添加视频到 assets/fallback/ 目录"
        )

    def download_videos_for_segments(
        self,
        segments: List[Dict[str, Any]],
        output_dir: str
    ) -> List[Dict[str, Any]]:
        """
        Download videos for all storyboard segments

        Args:
            segments: List of segment dicts with 'keyword' key
            output_dir: Directory to save videos

        Returns:
            Segments with 'video_path' added
        """
        from tqdm import tqdm

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        results = []
        pbar = tqdm(segments, desc="下载视频素材", unit="clip", ncols=80)

        for i, segment in enumerate(pbar):
            # 使用备用关键词池确保有好的搜索词
            keyword = segment.get('keyword') or self.FALLBACK_QUERIES[i % len(self.FALLBACK_QUERIES)]
            duration = segment.get('duration', 8)

            pbar.set_postfix_str(keyword[:25])

            video_path = os.path.join(output_dir, f"clip_{i:03d}.mp4")

            # download_video 保证返回有效路径
            downloaded = self.download_video(
                query=keyword,
                output_path=video_path,
                min_duration=int(duration)
            )

            segment_result = segment.copy()
            segment_result['video_path'] = downloaded
            results.append(segment_result)

        pbar.close()

        self.logger.info(f"All {len(segments)} videos downloaded successfully")

        return results

    def clear_cache(self):
        """Clear the video cache"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Cache cleared")
