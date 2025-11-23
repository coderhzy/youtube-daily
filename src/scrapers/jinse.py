"""
Jin Se (金色财经) scraper
"""

from datetime import datetime
from typing import List, Dict, Any

from .base import BaseScraper
from src.config import NEWS_SOURCES

class JinSeScraper(BaseScraper):
    """Scraper for Jin Se (金色财经)"""

    def __init__(self):
        super().__init__('金色财经')
        self.api_url = NEWS_SOURCES['jinse']['api_url']
        self.limit = NEWS_SOURCES['jinse'].get('limit', 100)
        self.headers['Referer'] = 'https://www.jinse.cn/'

    def fetch_news(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch news from Jin Se with pagination

        Args:
            hours: Fetch news from past N hours

        Returns:
            List of news items
        """
        try:
            self.logger.info(f"Fetching Jin Se news from past {hours} hours...")

            all_lives = []
            current_id = 0
            page = 1
            max_pages = (self.limit + 19) // 20  # 计算需要的页数 (每页20条)

            # 用于提前终止的时间检查
            cutoff_time = self._get_cutoff_time(hours)

            while page <= max_pages:
                params = {
                    'limit': 20,  # 每页20条
                    'reading': 'false',
                    'source': 'web',
                    'flag': 'down',
                    'id': current_id,
                    'category': 0
                }

                try:
                    response = self._make_request(self.api_url, params=params)
                    data = response.json()

                    items = data.get('list', [])
                    if not items:
                        self.logger.info(f"No more data at page {page}")
                        break

                    page_lives = []
                    oldest_time = None

                    for item in items:
                        lives = item.get('lives', [])
                        for live in lives:
                            created_at = live.get('created_at')
                            if created_at:
                                news_time = datetime.fromtimestamp(created_at, tz=self.tz)
                                if oldest_time is None or news_time < oldest_time:
                                    oldest_time = news_time
                            page_lives.append(live)

                    if not page_lives:
                        break

                    # 如果本页最旧的新闻已经超出时间范围，可以提前终止
                    if oldest_time and oldest_time < cutoff_time:
                        self.logger.info(f"Reached time limit at page {page}")
                        all_lives.extend(page_lives)
                        break

                    # 更新current_id为最后一条的ID，用于下一页
                    last_id = page_lives[-1].get('id')
                    if last_id:
                        current_id = last_id

                    all_lives.extend(page_lives)
                    self.logger.debug(f"Page {page}: fetched {len(page_lives)} items (total: {len(all_lives)})")
                    page += 1

                except Exception as e:
                    self.logger.warning(f"Error fetching page {page}: {e}")
                    break

            self.logger.info(f"Fetched {len(all_lives)} total items from {page-1} pages")

            # 处理和过滤新闻
            filtered_news = []
            for live in all_lives:
                try:
                    created_at = live.get('created_at')
                    if not created_at:
                        continue

                    news_time = datetime.fromtimestamp(created_at, tz=self.tz)

                    if not self._is_within_timeframe(news_time, hours):
                        continue

                    content = live.get('content', '').strip()
                    if not content:
                        continue

                    # Use content_prefix as title if available
                    title = live.get('content_prefix', '').strip()
                    if not title:
                        from src.utils.helpers import extract_title
                        title = extract_title(content)

                    news_item = self._format_news_item(
                        title=title,
                        content=content,
                        link=f"https://www.jinse.cn/lives/{live.get('id')}",
                        published_at=news_time,
                        grade=live.get('grade', 0)
                    )

                    filtered_news.append(news_item)

                except Exception as e:
                    self.logger.warning(f"Error parsing Jin Se news item: {e}")
                    continue

            self.logger.info(f"Successfully fetched {len(filtered_news)} Jin Se news items within {hours} hours")
            return filtered_news

        except Exception as e:
            self.logger.error(f"Unexpected error in Jin Se scraper: {e}")
            return []
