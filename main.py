#!/usr/bin/env python3
"""
Blockchain Daily News Automation System
Main entry point
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import TIMEZONE, ENABLE_AI_SUMMARY, NEWS_SOURCES, FETCH_HOURS
from src.scrapers import (
    JinSeScraper,
    OdailyScraper,
    CointelegraphScraper,
    CoinDeskScraper,
    TheBlockScraper
)
from src.processors import AIProcessor, ContentFilter
from src.database import SupabaseClient
from src.utils.logger import setup_logger
import pytz

# Setup logger
logger = setup_logger('blockchain_daily', log_dir='logs')

def main():
    """Main function"""
    try:
        logger.info("=" * 80)
        logger.info("Blockchain Daily News Bot - Starting")
        logger.info("=" * 80)

        # Get current time
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        date_str = now.strftime('%Y-%m-%d')

        logger.info(f"Date: {date_str}")
        logger.info(f"AI Summary Enabled: {ENABLE_AI_SUMMARY}")

        # Step 1: Fetch news from all sources
        logger.info("\n[Step 1/4] Fetching news from sources...")

        all_news = []
        scrapers = []

        # Initialize enabled scrapers
        if NEWS_SOURCES['jinse']['enabled']:
            scrapers.append(('金色财经', JinSeScraper()))
        if NEWS_SOURCES['odaily']['enabled']:
            scrapers.append(('Odaily', OdailyScraper()))
        if NEWS_SOURCES['cointelegraph']['enabled']:
            scrapers.append(('Cointelegraph', CointelegraphScraper()))
        if NEWS_SOURCES['coindesk']['enabled']:
            scrapers.append(('CoinDesk', CoinDeskScraper()))
        if NEWS_SOURCES['theblock']['enabled']:
            scrapers.append(('The Block', TheBlockScraper()))

        # Fetch from all sources
        for source_name, scraper in scrapers:
            news = scraper.fetch_news(hours=FETCH_HOURS)
            logger.info(f"  {source_name}: {len(news)} items")
            all_news.extend(news)

        logger.info(f"Total fetched: {len(all_news)} news items")

        if not all_news:
            logger.warning("No news fetched from any source, exiting...")
            return

        # Step 2: Filter and process
        logger.info("\n[Step 2/4] Processing and filtering news...")

        content_filter = ContentFilter()
        all_news = content_filter.process(all_news)

        logger.info(f"After processing: {len(all_news)} news items")

        if not all_news:
            logger.warning("No news remaining after filtering, exiting...")
            return

        # Step 3: AI processing
        logger.info("\n[Step 3/4] Generating article with AI...")

        ai_processor = AIProcessor()
        processed_data = ai_processor.process_daily_news(all_news, date_str)

        logger.info(f"Generated article: {processed_data['title']}")
        logger.info(f"Tags: {', '.join(processed_data['tags'])}")
        logger.info(f"Content length: {len(processed_data['content'])} characters")

        # Step 4: Save to database
        logger.info("\n[Step 4/4] Saving to Supabase database...")

        db = SupabaseClient()
        result = db.create_daily_post(
            title=processed_data['title'],
            content=processed_data['content'],
            date=now,
            description=processed_data['description'],
            tags=processed_data['tags']
        )

        logger.info(f"Successfully saved post to database")
        logger.info(f"  Post ID: {result.get('id')}")
        logger.info(f"  Post Slug: {result.get('slug')}")

        # Also save to output directory for backup
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"blockchain-daily-{date_str}.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {processed_data['title']}\n\n")
            f.write(f"> {processed_data['description']}\n\n")
            f.write(f"**Tags**: {', '.join(processed_data['tags'])}\n\n")
            f.write("---\n\n")
            f.write(processed_data['content'])

        logger.info(f"Backup saved to: {output_file}")

        logger.info("\n" + "=" * 80)
        logger.info("Blockchain Daily News Bot - Completed Successfully!")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error in main process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
