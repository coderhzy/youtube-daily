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

# Gemini Image Generation Model (Nano Banana Pro)
# google/gemini-3-pro-image-preview - 高级图片生成，支持多语言文字渲染
GEMINI_IMAGE_MODEL = os.getenv('GEMINI_IMAGE_MODEL', 'google/gemini-3-pro-image-preview')

# Feature Flags
ENABLE_AI_SUMMARY = os.getenv('ENABLE_AI_SUMMARY', 'true').lower() == 'true'
ENABLE_IMAGE_GENERATION = os.getenv('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true'
ENABLE_PDF_GENERATION = os.getenv('ENABLE_PDF_GENERATION', 'true').lower() == 'true'
ENABLE_EMAIL_SEND = os.getenv('ENABLE_EMAIL_SEND', 'true').lower() == 'true'

# Email Configuration
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', EMAIL_USERNAME)
EMAIL_TO = os.getenv('EMAIL_TO')  # 可以用逗号分隔多个邮箱

# Timezone Settings
TIMEZONE = 'Asia/Shanghai'

# News Sources Configuration
NEWS_SOURCES = {
    'jinse': {
        'enabled': True,
        'api_url': 'https://api.jinse.cn/noah/v2/lives',
        'language': 'zh',
        'limit': 40,  # 生产模式：抓取40条新闻
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
TARGET_ARTICLE_LENGTH = 8000  # 生产模式：目标文章长度8000字

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
