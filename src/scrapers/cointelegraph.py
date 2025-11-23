"""
Cointelegraph scraper (via RSSHub)
"""

from datetime import datetime
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from .base import BaseScraper
from src.config import NEWS_SOURCES

class CointelegraphScraper(BaseScraper):
    """Scraper for Cointelegraph (via RSSHub)"""

    def __init__(self):
        super().__init__('Cointelegraph')
        self.rss_url = NEWS_SOURCES['cointelegraph']['rss_url']

    def fetch_news(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch news from Cointelegraph via RSSHub

        Args:
            hours: Fetch news from past N hours

        Returns:
            List of news items
        """
        try:
            self.logger.info(f"Fetching Cointelegraph news (past {hours} hours)...")

            response = self._make_request(self.rss_url)
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
                            published_at=news_time,
                            language='en'
                        )
                        filtered_news.append(news_item)

                except Exception as e:
                    self.logger.warning(f"Error parsing Cointelegraph RSS item: {e}")
                    continue

            self.logger.info(f"Successfully fetched {len(filtered_news)} Cointelegraph news items")
            return filtered_news

        except Exception as e:
            self.logger.error(f"Error in Cointelegraph scraper: {e}")
            self.logger.info("Cointelegraph scraper will skip, continuing with other sources...")
            return []
