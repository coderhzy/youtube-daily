"""
Content filtering and deduplication
"""

from typing import List, Dict, Any
from src.utils.helpers import deduplicate_news, filter_quality_news
from src.utils.logger import get_logger

class ContentFilter:
    """Filter and process news content"""

    def __init__(self):
        self.logger = get_logger('content_filter')

    def process(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process news list: deduplicate, filter, and sort

        Args:
            news_list: Raw news list

        Returns:
            Processed news list
        """
        if not news_list:
            return []

        self.logger.info(f"Processing {len(news_list)} news items...")

        # Deduplicate
        news_list = deduplicate_news(news_list)
        self.logger.info(f"After deduplication: {len(news_list)} items")

        # Filter quality
        news_list = filter_quality_news(news_list, min_length=30)
        self.logger.info(f"After quality filter: {len(news_list)} items")

        # Sort by timestamp (newest first)
        news_list.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

        return news_list
