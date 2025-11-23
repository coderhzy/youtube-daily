"""
Odaily scraper (via RSSHub)
"""

from datetime import datetime
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from .base import BaseScraper
from src.config import NEWS_SOURCES

class OdailyScraper(BaseScraper):
    """Scraper for Odaily (via RSSHub)"""

    def __init__(self):
        super().__init__('Odaily')
        self.api_url = NEWS_SOURCES['odaily']['api_url']

    def fetch_news(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch news from Odaily via RSSHub

        Args:
            hours: Fetch news from past N hours

        Returns:
            List of news items
        """
        try:
            self.logger.info(f"Fetching Odaily news from RSSHub (past {hours} hours)...")

            response = self._make_request(self.api_url)
            root = ET.fromstring(response.content)

            filtered_news = []

            for item in root.findall('.//item'):
                try:
                    title_elem = item.find('title')
                    desc_elem = item.find('description')
                    link_elem = item.find('link')
                    pubDate_elem = item.find('pubDate')

                    if title_elem is None or desc_elem is None:
                        continue

                    title = title_elem.text.strip() if title_elem.text else ''
                    content = desc_elem.text.strip() if desc_elem.text else ''
                    link = link_elem.text.strip() if link_elem and link_elem.text else ''

                    if pubDate_elem is not None and pubDate_elem.text:
                        news_time = parsedate_to_datetime(pubDate_elem.text)
                        news_time = news_time.astimezone(self.tz)
                    else:
                        continue

                    if not self._is_within_timeframe(news_time, hours):
                        continue

                    content = self._clean_text(content)

                    if title and content:
                        news_item = self._format_news_item(
                            title=title,
                            content=content,
                            link=link,
                            published_at=news_time
                        )
                        filtered_news.append(news_item)

                except Exception as e:
                    self.logger.warning(f"Error parsing Odaily RSS item: {e}")
                    continue

            self.logger.info(f"Successfully fetched {len(filtered_news)} Odaily news items")
            return filtered_news

        except Exception as e:
            self.logger.error(f"Error in Odaily scraper: {e}")
            self.logger.info("Odaily scraper will skip, continuing with other sources...")
            return []
