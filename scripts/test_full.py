#!/usr/bin/env python3
"""
完整测试脚本 - 测试新的配置（100条/48小时）
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers import JinSeScraper
from src.processors import AIProcessor, ContentFilter
from src.utils.logger import setup_logger
from src.config import FETCH_HOURS
from datetime import datetime
import pytz

logger = setup_logger('test_full')

def main():
    """完整测试流程"""
    logger.info("="*80)
    logger.info("完整系统测试 - 新配置（100条/48小时）")
    logger.info("="*80)

    # 获取当前时间
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    date_str = now.strftime('%Y-%m-%d')

    # Step 1: 测试爬虫
    logger.info(f"\n[Step 1/3] 测试爬虫 (抓取过去 {FETCH_HOURS} 小时)")
    logger.info("-"*80)

    scraper = JinSeScraper()
    news_list = scraper.fetch_news(hours=FETCH_HOURS)

    logger.info(f"✓ 抓取结果: {len(news_list)} 条新闻")

    if not news_list:
        logger.warning("未抓取到新闻，测试终止")
        return

    # 显示样本
    logger.info(f"\n样本新闻 (前3条):")
    for i, news in enumerate(news_list[:3], 1):
        logger.info(f"{i}. {news['title'][:60]}...")
        logger.info(f"   发布时间: {news['published_at']}")
        logger.info(f"   内容长度: {len(news['content'])} 字符")

    # Step 2: 内容过滤
    logger.info(f"\n[Step 2/3] 内容过滤")
    logger.info("-"*80)

    content_filter = ContentFilter()
    filtered_news = content_filter.process(news_list)

    logger.info(f"✓ 过滤后: {len(filtered_news)} 条新闻")

    # Step 3: AI 处理（不需要API key也能测试基础格式）
    logger.info(f"\n[Step 3/3] 测试文章生成")
    logger.info("-"*80)

    try:
        ai_processor = AIProcessor()
        result = ai_processor.process_daily_news(filtered_news, date_str)

        logger.info(f"✓ 生成成功")
        logger.info(f"  标题: {result['title']}")
        logger.info(f"  描述长度: {len(result['description'])} 字符")
        logger.info(f"  内容长度: {len(result['content'])} 字符")
        logger.info(f"  标签: {', '.join(result['tags'])}")

        # 保存测试输出
        output_file = Path('output') / 'test_output.md'
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {result['title']}\n\n")
            f.write(f"> {result['description']}\n\n")
            f.write(f"**标签**: {', '.join(result['tags'])}\n\n")
            f.write("---\n\n")
            f.write(result['content'])

        logger.info(f"✓ 测试文章已保存到: {output_file}")

        # 统计字数
        content_length = len(result['content'])
        word_count = len(result['content'].replace(' ', ''))  # 粗略估计中文字数

        logger.info(f"\n📊 文章统计:")
        logger.info(f"  字符数: {content_length}")
        logger.info(f"  约{word_count}字")
        logger.info(f"  目标: 5000-10000字")

        if word_count < 5000:
            logger.warning(f"⚠️  文章偏短，建议:")
            logger.warning(f"  1. 检查是否启用了AI处理")
            logger.warning(f"  2. 增加 FETCH_HOURS 到 72")
            logger.warning(f"  3. 增加 NEWS_SOURCES['jinse']['limit'] 到 150")
        elif word_count > 12000:
            logger.warning(f"⚠️  文章偏长，建议:")
            logger.warning(f"  1. 减少 FETCH_HOURS 到 36")
            logger.warning(f"  2. 减少 NEWS_SOURCES['jinse']['limit'] 到 80")
        else:
            logger.info(f"✅ 文章长度合适！")

    except ValueError as e:
        logger.warning(f"AI处理器初始化失败: {e}")
        logger.info("提示: 需要配置 OPENROUTER_API_KEY 才能使用AI处理")

    # 总结
    logger.info(f"\n{'='*80}")
    logger.info("测试完成！")
    logger.info("="*80)
    logger.info(f"✓ 数据源: 金色财经")
    logger.info(f"✓ 抓取: {len(news_list)} 条原始新闻")
    logger.info(f"✓ 过滤后: {len(filtered_news)} 条")
    logger.info(f"✓ 时间范围: 过去 {FETCH_HOURS} 小时")
    logger.info(f"\n下一步:")
    logger.info(f"  1. 配置 .env 文件（添加 OPENROUTER_API_KEY）")
    logger.info(f"  2. 运行 python main.py 生成正式文章")

if __name__ == "__main__":
    main()
