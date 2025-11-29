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

# Article Generation Settings
ARTICLE_TARGET_WORDS = int(os.getenv('ARTICLE_TARGET_WORDS', '500'))  # 目标字数
ARTICLE_MAX_TOKENS = int(os.getenv('ARTICLE_MAX_TOKENS', '1500'))  # API返回上限

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
        'limit': 2,  # 测试模式：抓取2条新闻
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

# ==================== Video Generation ====================

# Feature Flag
ENABLE_VIDEO_GENERATION = os.getenv('ENABLE_VIDEO_GENERATION', 'false').lower() == 'true'

# Fish.audio TTS Configuration
FISH_AUDIO_API_KEY = os.getenv('FISH_AUDIO_API_KEY')
FISH_AUDIO_VOICE_ID = os.getenv('FISH_AUDIO_VOICE_ID', '')  # 你的声音克隆ID

# Pexels API Configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

# Video Settings
VIDEO_OUTPUT_DIR = os.getenv('VIDEO_OUTPUT_DIR', 'output/videos')
VIDEO_RESOLUTION = (1920, 1080)  # 1080p
VIDEO_FPS = 24
VIDEO_ORIENTATION = 'landscape'  # landscape / portrait

# 兜底素材目录
FALLBACK_ASSETS_DIR = 'assets/fallback'

# 关键词映射表（币圈术语 -> Pexels可搜索的通用词）
KEYWORD_MAPPING = {
    # 加密货币
    'BTC': 'Bitcoin cryptocurrency gold coin',
    'ETH': 'Ethereum blockchain technology',
    '比特币': 'Bitcoin cryptocurrency gold coin',
    '以太坊': 'Ethereum blockchain network',
    '加密货币': 'Cryptocurrency digital coins',
    '山寨币': 'Altcoin cryptocurrency trading',

    # DeFi
    'DeFi': 'Digital finance technology network',
    '去中心化': 'Decentralized network blockchain',
    '质押': 'Staking cryptocurrency investment',
    '流动性': 'Financial liquidity trading',

    # NFT
    'NFT': 'Digital art NFT technology',
    '数字藏品': 'Digital art collectibles',
    '铭文': 'Digital inscription art',

    # 市场
    '牛市': 'Stock market bull green arrow up',
    '熊市': 'Stock market bear red arrow down',
    '暴涨': 'Stock chart green spike up excitement',
    '暴跌': 'Stock market crash red numbers panic',
    '抄底': 'Investor buying opportunity trading',
    '套现': 'Cash money withdrawal finance',

    # 监管
    '监管': 'Government regulation official meeting',
    'SEC': 'Government regulatory agency official',
    '政策': 'Policy government decision making',
    '合规': 'Legal compliance business meeting',

    # 机构
    '机构': 'Corporate business office meeting',
    '华尔街': 'Wall Street New York finance',
    '银行': 'Bank finance building professional',
    '投资': 'Investment finance business professional',
    '融资': 'Funding investment business meeting',

    # 技术
    '升级': 'Technology upgrade innovation',
    '主网': 'Network technology infrastructure',
    '黑客': 'Hacker cybersecurity computer dark',
    '安全': 'Cybersecurity protection shield',

    # 通用
    '交易所': 'Stock exchange trading floor',
    '钱包': 'Digital wallet mobile phone app',
    '矿工': 'Cryptocurrency mining hardware',
}
