"""
Video Director - LLM-powered storyboard generator
"""

import json
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI

from src.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    KEYWORD_MAPPING
)
from src.utils.logger import get_logger


class VideoDirector:
    """
    LLM-powered video director that analyzes script and generates storyboard.
    Converts Chinese text into Pexels-searchable English keywords.
    """

    def __init__(self):
        self.logger = get_logger('video_director')

        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY must be set")

        # 创建不带代理的 httpx client
        import httpx
        http_client = httpx.Client(
            base_url=OPENROUTER_BASE_URL,
            timeout=60.0
        )

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            http_client=http_client
        )
        self.model = OPENROUTER_MODEL
        self.keyword_mapping = KEYWORD_MAPPING

        self.logger.info(f"Video Director initialized with model: {self.model}")

    def generate_storyboard(
        self,
        script: str,
        target_duration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate storyboard from script

        Args:
            script: The video script text
            target_duration: Target video duration in seconds (optional)

        Returns:
            List of storyboard segments with text, keyword, and duration
        """
        try:
            self.logger.info("Generating storyboard from script...")

            prompt = self._create_director_prompt(script, target_duration)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的视频分镜导演。你的任务是将中文脚本分解成多个视频片段，
并为每个片段生成适合在Pexels视频库搜索的英文关键词。

关键规则:
1. Pexels是英文素材库，关键词必须是英文
2. 关键词要具体、可视化（如 "Bitcoin gold coin"，不是抽象的 "crypto"）
3. 每个片段5-15秒
4. 返回严格的JSON格式"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )

            result = response.choices[0].message.content
            self.logger.info(f"LLM response length: {len(result)} chars")
            self.logger.debug(f"LLM response preview: {result[:300]}...")

            segments = self._parse_storyboard(result)

            # 如果解析失败，使用简单分段
            if not segments:
                self.logger.warning("LLM storyboard parsing failed, using simple segmentation")
                self.logger.info(f"Raw LLM response: {result[:500]}")
                segments = self._simple_segmentation(script)

            # 应用关键词映射优化
            segments = self._optimize_keywords(segments)

            self.logger.info(f"Generated {len(segments)} storyboard segments")
            return segments

        except Exception as e:
            self.logger.error(f"Storyboard generation failed: {e}")
            # 返回简单的分段作为兜底
            return self._simple_segmentation(script)

    def _create_director_prompt(self, script: str, target_duration: Optional[int]) -> str:
        """Create prompt for director LLM"""
        # 只取脚本前1500字，避免太长
        script_preview = script[:1500]

        return f"""将下面的中文脚本分成5-8个视频片段，每个片段配一个英文搜索词（用于Pexels素材库）。

脚本:
{script_preview}

直接返回JSON数组，格式如下:
[
  {{"text": "片段1中文内容", "keyword": "Bitcoin gold coin", "duration": 8}},
  {{"text": "片段2中文内容", "keyword": "Stock market chart", "duration": 6}}
]

关键词示例:
- 比特币 → "Bitcoin cryptocurrency"
- 涨跌 → "Stock chart arrow"
- 监管 → "Government meeting"
- 科技 → "Technology network"

只输出JSON数组，不要其他文字。"""

    def _parse_storyboard(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into storyboard segments"""
        try:
            if not llm_response or not llm_response.strip():
                self.logger.warning("Empty LLM response")
                return []

            # 提取JSON
            json_str = None

            # 方法1: 从 ```json ``` 代码块提取
            json_match = re.search(r'```json\s*(.*?)\s*```', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)

            # 方法2: 从 ``` ``` 代码块提取
            if not json_str:
                json_match = re.search(r'```\s*(.*?)\s*```', llm_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)

            # 方法3: 直接找 [ ] 数组
            if not json_str:
                json_str = llm_response.strip()
                start = json_str.find('[')
                end = json_str.rfind(']') + 1
                if start != -1 and end > start:
                    json_str = json_str[start:end]
                else:
                    self.logger.warning("No JSON array found in response")
                    return []

            segments = json.loads(json_str)

            # 验证格式
            validated = []
            for seg in segments:
                if isinstance(seg, dict) and 'text' in seg:
                    validated.append({
                        'text': seg.get('text', ''),
                        'keyword': seg.get('keyword', 'technology abstract background'),
                        'duration': seg.get('duration', 8),
                        'mood': seg.get('mood', 'neutral')
                    })

            return validated

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse storyboard JSON: {e}")
            self.logger.debug(f"Raw response: {llm_response[:500]}...")
            return []

    def _optimize_keywords(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize keywords using mapping table"""
        optimized = []

        for seg in segments:
            text = seg.get('text', '')
            keyword = seg.get('keyword', '')

            # 检查是否有更好的映射
            for cn_term, en_keyword in self.keyword_mapping.items():
                if cn_term.lower() in text.lower():
                    # 如果原关键词比较弱，使用映射
                    if len(keyword) < 15 or keyword == 'technology abstract background':
                        keyword = en_keyword
                        break

            seg['keyword'] = keyword
            optimized.append(seg)

        return optimized

    def _simple_segmentation(self, script: str) -> List[Dict[str, Any]]:
        """Simple fallback segmentation"""
        self.logger.info("Using simple segmentation as fallback")

        # 默认关键词池 - 这些在 Pexels 上一定有很多结果
        default_keywords = [
            'cryptocurrency bitcoin gold',
            'stock market trading chart',
            'digital technology network',
            'business finance graph',
            'computer data visualization',
            'city skyline modern',
            'office meeting business',
            'futuristic technology blue'
        ]

        # 清理 Markdown 格式
        clean_script = re.sub(r'#{1,6}\s*', '', script)  # 移除标题
        clean_script = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_script)  # 移除粗体
        clean_script = re.sub(r'[📊🏛️💰🔧💼✨✓⚠️❌✅]', '', clean_script)  # 移除emoji

        # 按段落分割
        paragraphs = clean_script.split('\n\n')
        segments = []
        keyword_index = 0

        for para in paragraphs:
            para = para.strip()
            # 跳过空段落和太短的段落
            if not para or len(para) < 20:
                continue

            # 估算时长（250字/分钟）
            char_count = len(para)
            duration = max(5, min(15, int(char_count / 250 * 60)))

            # 尝试从映射表获取关键词
            keyword = None
            for cn_term, en_keyword in self.keyword_mapping.items():
                if cn_term in para:
                    keyword = en_keyword
                    break

            # 如果没有匹配到，使用默认关键词池（循环使用）
            if not keyword:
                keyword = default_keywords[keyword_index % len(default_keywords)]
                keyword_index += 1

            segments.append({
                'text': para[:200],  # 限制文本长度
                'keyword': keyword,
                'duration': duration,
                'mood': 'neutral'
            })

        # 确保至少有一个段落
        if not segments:
            self.logger.warning("No segments generated, using default")
            segments = [{
                'text': '区块链每日观察',
                'keyword': 'cryptocurrency bitcoin blockchain',
                'duration': 10,
                'mood': 'neutral'
            }]

        self.logger.info(f"Simple segmentation generated {len(segments)} segments")
        return segments

    def estimate_audio_duration(self, text: str) -> float:
        """
        Estimate audio duration for text

        Args:
            text: Chinese text

        Returns:
            Estimated duration in seconds
        """
        # 中文语速约250字/分钟
        char_count = len(text)
        return char_count / 250 * 60

    def sync_with_audio(
        self,
        segments: List[Dict[str, Any]],
        audio_duration: float
    ) -> List[Dict[str, Any]]:
        """
        Adjust segment durations to match audio duration

        Args:
            segments: Storyboard segments
            audio_duration: Total audio duration in seconds

        Returns:
            Adjusted segments
        """
        if not segments:
            return segments

        # 计算当前总时长
        total_duration = sum(seg.get('duration', 8) for seg in segments)

        if total_duration <= 0:
            return segments

        # 按比例调整
        ratio = audio_duration / total_duration

        for seg in segments:
            seg['duration'] = max(3, seg['duration'] * ratio)

        return segments
