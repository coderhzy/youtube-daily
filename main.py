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

from src.config import (
    TIMEZONE, ENABLE_AI_SUMMARY, NEWS_SOURCES, FETCH_HOURS,
    ENABLE_IMAGE_GENERATION, ENABLE_PDF_GENERATION, ENABLE_EMAIL_SEND,
    ENABLE_VIDEO_GENERATION
)
from src.scrapers import (
    JinSeScraper,
    OdailyScraper,
    CointelegraphScraper,
    CoinDeskScraper,
    TheBlockScraper
)
from src.processors import AIProcessor, ContentFilter
from src.processors.image_generator import ImageGenerator
from src.processors.pdf_generator import PDFGenerator
from src.database import SupabaseClient
from src.utils.logger import setup_logger
from src.utils.email_sender import EmailSender
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

        # Step 5: Generate images (if enabled)
        generated_images = []
        if ENABLE_IMAGE_GENERATION:
            logger.info("\n[Step 5/8] Generating images with AI...")
            try:
                image_generator = ImageGenerator()

                # Get cover prompt and attractive title from processed data
                cover_prompt = processed_data.get('cover_prompt')
                attractive_title = processed_data.get('attractive_title')

                if attractive_title:
                    logger.info(f"✨ Attractive title: {attractive_title}")

                generated_images = image_generator.generate_images_for_article(
                    article_content=processed_data['content'],
                    date_str=date_str,
                    cover_prompt=cover_prompt,
                    attractive_title=attractive_title
                )
                logger.info(f"✓ Generated {len(generated_images)} images total")

                # Log cover image if generated
                cover_images = [img for img in generated_images if img.get('is_cover')]
                if cover_images:
                    logger.info(f"  - 1 cover image (YouTube thumbnail)")
                    logger.info(f"  - {len(generated_images) - 1} content images")
            except Exception as e:
                logger.error(f"Image generation failed: {e}")
                logger.info("Continuing without images...")
        else:
            logger.info("\n[Step 5/8] Image generation disabled (skipping)")

        # Step 6: Generate PDF (if enabled)
        pdf_path = None
        if ENABLE_PDF_GENERATION:
            logger.info("\n[Step 6/8] Generating PDF report...")
            try:
                pdf_generator = PDFGenerator()
                pdf_filename = f"blockchain-daily-{date_str}.pdf"
                pdf_path = pdf_generator.generate_pdf(
                    article_data={
                        'title': processed_data['title'],
                        'content': processed_data['content'],
                        'description': processed_data['description'],
                        'tags': processed_data['tags'],
                        'date': date_str
                    },
                    images=generated_images,
                    output_path=str(output_dir / pdf_filename)
                )
                logger.info(f"✓ PDF generated: {pdf_path}")
            except Exception as e:
                logger.error(f"PDF generation failed: {e}")
                logger.info("Continuing without PDF...")
        else:
            logger.info("\n[Step 6/8] PDF generation disabled (skipping)")

        # Step 7: Send email (if enabled and PDF exists)
        if ENABLE_EMAIL_SEND and pdf_path:
            logger.info("\n[Step 7/8] Sending email with PDF and images zip...")
            try:
                email_sender = EmailSender()
                success = email_sender.send_daily_report(
                    pdf_path=pdf_path,
                    date_str=date_str,
                    article_title=processed_data['title'],
                    article_description=processed_data['description'],
                    num_news=len(all_news),
                    num_images=len(generated_images),
                    images_dir='output/images'  # Pass images directory
                )
                if success:
                    logger.info("✓ Email sent successfully (PDF + Images ZIP)")
                else:
                    logger.warning("Email sending failed")
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                logger.info("Report generated but email not sent")
        else:
            logger.info("\n[Step 7/8] Email sending disabled or PDF not available (skipping)")

        # Step 8: Generate video (if enabled)
        video_result = None
        if ENABLE_VIDEO_GENERATION:
            logger.info("\n[Step 8/8] Generating video with TTS and stock footage...")
            try:
                from src.video import VideoGenerator
                video_generator = VideoGenerator()

                # 找封面图
                cover_image = None
                cover_images = [img for img in generated_images if img.get('is_cover')]
                if cover_images:
                    cover_image = cover_images[0].get('path')

                video_result = video_generator.generate_video(
                    script=processed_data['content'],
                    date_str=date_str,
                    title=processed_data.get('attractive_title', processed_data['title']),
                    cover_image=cover_image
                )

                if video_result.get('success'):
                    logger.info(f"✓ Video generated: {video_result['video_path']}")
                    logger.info(f"  Duration: {video_result['duration']:.1f}s")
                    logger.info(f"  Size: {video_result['file_size_mb']:.1f}MB")
                else:
                    logger.warning(f"Video generation failed: {video_result.get('error', 'Unknown error')}")

            except Exception as e:
                logger.error(f"Video generation failed: {e}")
                logger.info("Continuing without video...")
        else:
            logger.info("\n[Step 8/8] Video generation disabled (skipping)")

        logger.info("\n" + "=" * 80)
        logger.info("Blockchain Daily News Bot - Completed Successfully!")
        logger.info("=" * 80)
        logger.info(f"  News items: {len(all_news)}")
        logger.info(f"  Images generated: {len(generated_images)}")
        if pdf_path:
            logger.info(f"  PDF report: {pdf_path}")
        if video_result and video_result.get('success'):
            logger.info(f"  Video: {video_result['video_path']}")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error in main process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
