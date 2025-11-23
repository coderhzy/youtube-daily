#!/usr/bin/env python3
"""
Test all news scrapers
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers import (
    JinSeScraper,
    OdailyScraper,
    CointelegraphScraper,
    CoinDeskScraper,
    TheBlockScraper
)
from src.utils.logger import setup_logger

logger = setup_logger('test_scrapers')

def test_scraper(name: str, scraper, hours: int = 24):
    """Test a single scraper"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing {name} Scraper")
    logger.info('='*60)

    try:
        news = scraper.fetch_news(hours=hours)
        logger.info(f"✓ Fetched {len(news)} news items")

        if news:
            logger.info(f"Sample news: {news[0]['title'][:60]}...")
            logger.info(f"Source: {news[0]['source']}")
            logger.info(f"Link: {news[0]['link']}")

        return news
    except Exception as e:
        logger.error(f"✗ Failed: {e}")
        return []

def main():
    """Test all scrapers"""
    logger.info("="*60)
    logger.info("Testing All News Scrapers")
    logger.info("="*60)

    scrapers = [
        ('金色财经', JinSeScraper()),
        ('Odaily', OdailyScraper()),
        ('Cointelegraph', CointelegraphScraper()),
        ('CoinDesk', CoinDeskScraper()),
        ('The Block', TheBlockScraper()),
    ]

    results = {}

    for name, scraper in scrapers:
        news = test_scraper(name, scraper)
        results[name] = len(news)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("Summary")
    logger.info('='*60)

    total = sum(results.values())
    for name, count in results.items():
        status = '✓' if count > 0 else '✗'
        logger.info(f"{status} {name}: {count} items")

    logger.info(f"\nTotal: {total} news items")

if __name__ == "__main__":
    main()
