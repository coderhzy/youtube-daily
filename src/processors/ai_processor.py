"""
AI Processor for news content using OpenRouter
"""

from typing import List, Dict, Any
from openai import OpenAI

from src.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    ENABLE_AI_SUMMARY
)
from src.utils.logger import get_logger

class AIProcessor:
    """AI processor using OpenRouter for content generation"""

    def __init__(self):
        self.logger = get_logger('ai_processor')

        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY must be set in environment variables")

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
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
            Dict containing title, content, description, tags
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
                        "content": "你是一位资深的区块链行业分析师和深度内容创作者,擅长撰写详实、有洞察力的行业观察文章。你的文章信息量大、分析深入,深受专业读者喜爱。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=16000  # 支持更长的输出（约10k中文字）
            )

            result = response.choices[0].message.content

            # Parse AI response
            parsed_result = self._parse_ai_response(result, date_str)

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
        return f"""请将以下区块链新闻整理成一篇**深度、详细**的每日观察博客文章。

日期: {date_str}

新闻内容:
{news_text}

请按以下要求处理:

1. **文章长度**: 目标8000-10000字，需要详细展开每条新闻的背景、影响和分析

2. **文章结构**:

   a) **开篇总结** (500-800字):
      - 用3-5段话总结今日最重要的动态
      - 提炼核心主题和趋势
      - 设置阅读期待

   b) **分类深度报道**: 将新闻分为以下板块，每个板块详细展开:
      - 📊 **市场动态** (价格、交易量、市场情绪、技术分析)
      - 🏛️ **政策监管** (各国监管动向、合规要求、政策影响)
      - 💰 **DeFi生态** (协议更新、TVL变化、收益机会、风险分析)
      - 🎨 **NFT与链游** (新项目、交易数据、市场热点)
      - 🔧 **技术创新** (协议升级、Layer2进展、新技术落地)
      - 💼 **投融资** (融资事件、投资机构动向、估值分析)
      - 🌐 **行业动态** (机构入场、生态发展、行业合作)

   c) **深度分析** (1000-1500字):
      - 今日新闻的关联性分析
      - 对行业趋势的影响
      - 潜在机会和风险提示

3. **内容深度要求**:
   - **每条重要新闻**: 用150-300字展开，包括:
     * 事件背景介绍
     * 详细数据和事实
     * 业内观点引用
     * 潜在影响分析

   - **次要新闻**: 用80-150字概括

   - **添加专业洞察**:
     * 引用行业数据和指标
     * 对比历史事件
     * 分析因果关系
     * 预测未来走向

4. **语言风格**:
   - 专业但易懂，面向对区块链有一定了解的读者
   - 使用数据支撑观点
   - 保持客观中立，但可以提供独到见解
   - 适当使用行业术语，并简要解释

5. **格式要求**:
   - 使用Markdown格式
   - 每个板块用二级标题(##)
   - 重要新闻用三级标题(###)
   - 次要新闻用列表项(-)
   - 关键数据用**粗体**标注
   - 适当使用引用块(>)突出重要观点

请直接输出Markdown格式的文章内容，确保内容充实、分析深入、信息量大。"""

    def _parse_ai_response(self, ai_response: str, date_str: str) -> Dict[str, Any]:
        """Parse AI response"""
        lines = ai_response.strip().split('\n')
        description_lines = []
        content_start = 0

        for i, line in enumerate(lines):
            if line.startswith('##'):
                content_start = i
                break
            if line.strip() and not line.startswith('#'):
                description_lines.append(line.strip())

        description = ' '.join(description_lines[:3]) if description_lines else f"区块链每日观察 - {date_str}"

        content = '\n'.join(lines[content_start:]) if content_start > 0 else ai_response

        tags = self._extract_tags(content)

        return {
            'title': f"区块链每日观察 - {date_str}",
            'content': content,
            'description': description[:200],
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
            'tags': ['区块链', '每日观察']
        }
