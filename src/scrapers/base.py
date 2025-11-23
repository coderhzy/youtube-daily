"""
Base scraper class for all news sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz
import requests

from src.utils.logger import get_logger

class BaseScraper(ABC):
    """
    Abstract base class for news scrapers
    """

    def __init__(self, source_name: str, timezone: str = 'Asia/Shanghai'):
        """
        Initialize scraper

        Args:
            source_name: Name of the news source
            timezone: Timezone for timestamp conversion
        """
        self.source_name = source_name
        self.tz = pytz.timezone(timezone)
        self.logger = get_logger(f'scraper.{source_name.lower()}')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

    @abstractmethod
    def fetch_news(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch news from the source

        Args:
            hours: Fetch news from past N hours

        Returns:
            List of news items, each containing:
                - source: str
                - title: str
                - content: str
                - link: str
                - published_at: str (ISO format)
                - timestamp: int
                - image_url: str (optional)
        """
        pass

    def _make_request(self, url: str, params: dict = None, timeout: int = 30) -> requests.Response:
        """
        Make HTTP request with error handling

        Args:
            url: Request URL
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            raise

    def _get_cutoff_time(self, hours: int) -> datetime:
        """
        Get cutoff time for news filtering

        Args:
            hours: Timeframe in hours

        Returns:
            Cutoff datetime
        """
        now = datetime.now(self.tz)
        return now - timedelta(hours=hours)

    def _is_within_timeframe(self, news_time: datetime, hours: int) -> bool:
        """
        Check if news is within specified timeframe

        Args:
            news_time: News publication time
            hours: Timeframe in hours

        Returns:
            True if within timeframe, False otherwise
        """
        cutoff_time = self._get_cutoff_time(hours)
        return news_time >= cutoff_time

    def _format_news_item(
        self,
        title: str,
        content: str,
        link: str,
        published_at: datetime,
        image_url: str = '',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Format news item to standard structure

        Args:
            title: News title
            content: News content
            link: News URL
            published_at: Publication datetime
            image_url: Image URL
            **kwargs: Additional fields

        Returns:
            Formatted news dict
        """
        news_item = {
            'source': self.source_name,
            'title': title.strip(),
            'content': content.strip(),
            'link': link.strip(),
            'published_at': published_at.isoformat(),
            'timestamp': int(published_at.timestamp()),
            'image_url': image_url
        }

        # Add any additional fields
        news_item.update(kwargs)

        return news_item

    def _clean_text(self, text: str) -> str:
        """
        Clean text content

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        from src.utils.helpers import clean_text
        return clean_text(text)
