"""
Configuration management
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')

# Feature Flags
ENABLE_AI_SUMMARY = os.getenv('ENABLE_AI_SUMMARY', 'true').lower() == 'true'

# Timezone Settings
TIMEZONE = 'Asia/Shanghai'

# News Sources Configuration
NEWS_SOURCES = {
    'jinse': {
        'enabled': True,
        'api_url': 'https://api.jinse.cn/noah/v2/lives',
        'language': 'zh',
        'limit': 60,  # 抓取60条新闻（日更，24小时内）
    },
    'odaily': {
        'enabled': False,  # 禁用（RSSHub不稳定）
        'api_url': 'https://rsshub.app/odaily/newsflash',
        'language': 'zh',
    },
    'cointelegraph': {
        'enabled': False,  # 禁用（RSSHub不稳定）
        'rss_url': 'https://rsshub.app/cointelegraph',
        'language': 'en',
    },
    'coindesk': {
        'enabled': False,  # 禁用（RSSHub不稳定）
        'rss_url': 'https://rsshub.app/coindesk',
        'language': 'en',
    },
    'theblock': {
        'enabled': False,  # 禁用（RSSHub不稳定）
        'rss_url': 'https://rsshub.app/theblock',
        'language': 'en',
    },
}

# Content Settings
FETCH_HOURS = 24  # 抓取过去24小时的新闻（日更）
MIN_CONTENT_LENGTH = 50  # 最小内容长度
TARGET_ARTICLE_LENGTH = 8000  # 目标文章长度（字符数）约5k-10k字

# News Categories
NEWS_CATEGORIES = {
    'policy': '政策监管',
    'defi': 'DeFi',
    'nft': 'NFT',
    'market': '市场动态',
    'tech': '技术前沿',
    'investment': '投融资',
    'other': '其他'
}

# Request Headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}
