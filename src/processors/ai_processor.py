"""
AI Processor for news content using OpenRouter
"""

from typing import List, Dict, Any
from openai import OpenAI

from src.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    ENABLE_AI_SUMMARY,
    ARTICLE_TARGET_WORDS,
    ARTICLE_MAX_TOKENS
)
from src.utils.logger import get_logger

class AIProcessor:
    """AI processor using OpenRouter for content generation"""

    def __init__(self):
        self.logger = get_logger('ai_processor')

        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY must be set in environment variables")

        # 创建不带代理的 httpx client
        import httpx
        http_client = httpx.Client(
            base_url=OPENROUTER_BASE_URL,
            timeout=120.0
        )

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            http_client=http_client
        )
        self.model = OPENROUTER_MODEL
        self.logger.info(f"AI Processor initialized with model: {self.model}")

    def process_daily_news(
        self,
        news_list: List[Dict[str, Any]],
        date_str: str
    ) -> Dict[str, Any]:
        """
        Process daily news and generate blog article

        Args:
            news_list: List of news items
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Dict containing title, content, description, tags, attractive_title, cover_prompt
        """
        if not ENABLE_AI_SUMMARY:
            self.logger.info("AI summary is disabled, using basic formatting")
            return self._basic_format(news_list, date_str)

        try:
            self.logger.info(f"Processing {len(news_list)} news items with AI...")

            # Prepare news text
            news_text = self._prepare_news_text(news_list)

            # Call AI to generate article
            prompt = self._create_prompt(news_text, date_str)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位区块链YouTube博主，擅长用口语化、接地气的方式讲解行业新闻。你的风格是：简洁直接、不用书面语、像和朋友聊天。避免使用'值得注意'、'总而言之'、'不可否认'等AI腔调词汇。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=ARTICLE_MAX_TOKENS
            )

            result = response.choices[0].message.content

            # Parse AI response
            parsed_result = self._parse_ai_response(result, date_str)

            # Generate attractive title and cover image prompt
            self.logger.info("Generating attractive title and cover image prompt...")
            title_and_cover = self._generate_attractive_title_and_cover(news_text, parsed_result['content'])

            parsed_result['attractive_title'] = title_and_cover['title']
            parsed_result['cover_prompt'] = title_and_cover['cover_prompt']

            self.logger.info("AI processing completed successfully")
            return parsed_result

        except Exception as e:
            self.logger.error(f"Error in AI processing: {e}")
            self.logger.info("Falling back to basic formatting")
            return self._basic_format(news_list, date_str)

    def _prepare_news_text(self, news_list: List[Dict[str, Any]]) -> str:
        """Prepare news text for AI processing"""
        news_items = []
        for i, news in enumerate(news_list, 1):
            source = news.get('source', '未知来源')
            title = news.get('title', '')
            content = news.get('content', '')

            news_items.append(
                f"{i}. [{source}] {title}\n   {content}"
            )

        return "\n\n".join(news_items)

    def _create_prompt(self, news_text: str, date_str: str) -> str:
        """Create AI prompt"""
        return f"""请将以下区块链新闻整理成一篇适合TTS语音合成的视频脚本。

日期: {date_str}

新闻内容:
{news_text}

请按以下要求处理:

1. **文章长度**: 目标{ARTICLE_TARGET_WORDS}字左右

2. **写作技巧 - 现象→问题→解答**:
   在今天最重要的1-2个话题上，可以用这个结构来增加深度：
   - 现象: 客观陈述发生了什么
   - 问题: 提出观众关心的问题（"那我们不禁要问..."）
   - 解答: 引用专家观点或分析

   示例:
   "英伟达昨夜大涨百分之五，纳指突破两万点，引爆了投资者对AI的热情。
   那我们不禁要问，AI行情还能持续多久。
   著名投资人木头姐认为，AI仍处于早期阶段。"

   注意：不要每个话题都用这个结构，其他次要新闻简单陈述即可，保持自然

3. **语言风格**:
   - 平稳叙述，像新闻播报
   - 禁止感叹号和夸张词
   - 禁止"值得注意的是"、"总而言之"等套话
   - 用短句，直接陈述

4. **数字格式** (TTS朗读):
   - 所有数字转中文: "20%" → "百分之二十"
   - 金额: "$95000" → "九万五千美元"
   - 日期: "11月28日" → "十一月二十八日"

5. **文章结构**:
   a) **开场**: "大家好，欢迎来到区块链每日观察" + 今天最重要的一两件事

   b) **互动提示**: "如果觉得有帮助，欢迎点赞订阅，开启小铃铛"

   c) **主体内容** (2-3个话题)

   d) **结尾**: 用自然的过渡语，如"好了，让我们快速回顾一下今天的重点"，不要直接说"总结"两个字

6. **格式要求**:
   - 使用Markdown，板块用二级标题
   - 不用emoji，不用粗体星号

请直接输出脚本内容。"""

    def _parse_ai_response(self, ai_response: str, date_str: str) -> Dict[str, Any]:
        """Parse AI response"""
        lines = ai_response.strip().split('\n')
        description_lines = []
        content_start = 0

        # 过滤掉AI的礼貌性回复开头
        skip_phrases = [
            '好的', '这是', '根据', '您提供', '整理而成',
            '以下是', '为您', '我将', '让我', '---', '**日期：'
        ]

        for i, line in enumerate(lines):
            if line.startswith('##'):
                content_start = i
                break

            # 跳过空行和以#开头的行
            if not line.strip() or line.startswith('#'):
                continue

            # 跳过包含礼貌性回复的行
            if any(phrase in line for phrase in skip_phrases):
                continue

            # 只添加有实际内容的行
            if line.strip():
                description_lines.append(line.strip())

        # 如果没有找到合适的描述，使用默认描述
        if description_lines:
            description = ' '.join(description_lines[:2])  # 只取前2行，避免太长
        else:
            description = f"区块链每日观察 - {date_str}"

        content = '\n'.join(lines[content_start:]) if content_start > 0 else ai_response

        # 强制插入互动提示（如果AI没有生成）
        cta_text = "如果你觉得内容有帮助，欢迎点赞、订阅，开启小铃铛，不错过每天的行业动态"

        # 检查内容中是否包含互动提示
        if "点赞" not in content or "订阅" not in content:
            self.logger.info("AI未生成互动提示，强制插入...")

            # 在第一个二级标题前插入互动提示
            lines_list = content.split('\n')
            insert_index = 0

            for i, line in enumerate(lines_list):
                if line.startswith('## '):
                    insert_index = i
                    break

            if insert_index > 0:
                # 在第一个板块前插入
                lines_list.insert(insert_index, f"\n{cta_text}\n")
                content = '\n'.join(lines_list)
                self.logger.info("互动提示已插入到第一个板块前")
            else:
                # 如果没有找到板块标题，插入到开头后
                lines_list.insert(min(10, len(lines_list)), f"\n{cta_text}\n")
                content = '\n'.join(lines_list)
                self.logger.info("互动提示已插入到开头位置")

        tags = self._extract_tags(content)

        return {
            'title': f"区块链每日观察 - {date_str}",
            'content': content,
            'description': description[:200],  # 限制200字符
            'tags': tags
        }

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        tags = ['区块链', '每日观察']

        content_lower = content.lower()

        if 'defi' in content_lower or '去中心化金融' in content:
            tags.append('DeFi')
        if 'nft' in content_lower or '数字藏品' in content:
            tags.append('NFT')
        if '比特币' in content or 'bitcoin' in content_lower or 'btc' in content_lower:
            tags.append('比特币')
        if '以太坊' in content or 'ethereum' in content_lower or 'eth' in content_lower:
            tags.append('以太坊')
        if '监管' in content or '政策' in content:
            tags.append('政策监管')
        if '融资' in content or '投资' in content:
            tags.append('投融资')

        return list(set(tags))

    def _generate_attractive_title_and_cover(self, news_text: str, article_content: str) -> Dict[str, str]:
        """
        Generate attractive title and cover image prompt based on article content

        Args:
            news_text: Raw news text
            article_content: Processed article content

        Returns:
            Dict with 'title' and 'cover_prompt'
        """
        try:
            prompt = f"""基于以下区块链新闻文章，生成一个吸引人的YouTube视频标题和封面图描述。

文章摘要:
{article_content[:1000]}...

要求:

1. **YouTube视频标题**（10-25个字）:
   - 抓住今日最核心、最吸引眼球的话题
   - 使用数字、情感词、悬念等技巧
   - 适合YouTube算法推荐
   - 示例: "比特币暴跌20%！巨鲸却在疯狂抄底？"
   - 示例: "以太坊重大升级！Gas费用降低90%"
   - 示例: "美国SEC突发新政！加密市场将迎来巨变？"

2. **封面图提示词**（英文，用于Nano Banana Pro图片生成）:
   - 必须包含吸引人的人物场景
   - 突出今日最重要的主题
   - 适合YouTube缩略图（16:9横屏）
   - 包含清晰的中文标题文字
   - 视觉冲击力强，让人想点击
   - 符合Nano Banana Pro的文字渲染优势

请以JSON格式返回:
{{
  "title": "吸引人的YouTube标题",
  "cover_prompt": "Detailed English prompt for cover image generation"
}}

封面图提示词示例格式:
"Create a dramatic YouTube thumbnail image for blockchain news.
Scene: Shocked/excited business analyst looking at large digital screen showing [KEY EVENT],
dramatic lighting, urgent atmosphere, close-up professional photography style.
Chinese title text: '[YouTube标题]' in large bold white characters (90pt+) at top,
highly visible and readable using Nano Banana Pro's superior text rendering.
Visual elements: Bitcoin/crypto symbols, price charts with dramatic arrows,
breaking news aesthetic, red/green color accents for market emotions.
Background: Gradient dark blue to black, cinematic lighting, high contrast.
Style: YouTube thumbnail optimized, attention-grabbing, professional yet dramatic,
perfect for video presentation, 16:9 horizontal format.
Text rendering: Ensure Chinese characters are crystal clear and prominent using
Nano Banana Pro's industry-leading multilingual text capabilities."

注意: 标题要能引起好奇心和点击欲望，封面图要视觉冲击力强！"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # 稍高的温度以获得更有创意的标题
                max_tokens=2000
            )

            result = response.choices[0].message.content

            # Parse JSON response
            import json
            import re

            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)

            parsed = json.loads(result)

            self.logger.info(f"Generated attractive title: {parsed['title']}")
            return parsed

        except Exception as e:
            self.logger.error(f"Error generating attractive title and cover: {e}")
            # Fallback
            return {
                'title': '今日区块链行业重大动态',
                'cover_prompt': 'Professional blockchain news presenter looking at dramatic market charts, urgent atmosphere, Chinese title text visible'
            }

    def _basic_format(self, news_list: List[Dict[str, Any]], date_str: str) -> Dict[str, Any]:
        """Basic formatting without AI"""
        content_parts = [
            f"# 区块链每日观察 - {date_str}\n",
            f"今日共收录 {len(news_list)} 条区块链行业动态\n",
            "---\n"
        ]

        # Group by source
        sources = {}
        for news in news_list:
            source = news.get('source', '其他')
            if source not in sources:
                sources[source] = []
            sources[source].append(news)

        for source, source_news in sources.items():
            content_parts.append(f"\n## 📰 {source}\n")
            for news in source_news:
                content_parts.append(f"- **{news['title']}**  \n  {news['content']}\n")

        content = '\n'.join(content_parts)

        return {
            'title': f"区块链每日观察 - {date_str}",
            'content': content,
            'description': f"区块链每日观察 - {date_str},收录{len(news_list)}条行业动态",
            'tags': ['区块链', '每日观察'],
            'attractive_title': f'今日区块链行业动态 - {date_str}',
            'cover_prompt': 'Professional blockchain news, modern office setting'
        }
