# 项目结构说明

## 📂 完整目录结构

```
youtube-daily/
│
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── config.py                 # 配置管理 (数据源、API密钥等)
│   │
│   ├── scrapers/                 # 新闻爬虫模块
│   │   ├── __init__.py
│   │   ├── base.py              # 爬虫基类 (统一接口)
│   │   ├── jinse.py             # 金色财经爬虫 ✅
│   │   ├── odaily.py            # Odaily爬虫 (RSSHub)
│   │   ├── cointelegraph.py     # Cointelegraph爬虫
│   │   ├── coindesk.py          # CoinDesk爬虫
│   │   └── theblock.py          # The Block爬虫
│   │
│   ├── processors/               # 数据处理模块
│   │   ├── __init__.py
│   │   ├── ai_processor.py      # AI处理器 (OpenRouter)
│   │   └── content_filter.py    # 内容过滤和去重
│   │
│   ├── database/                 # 数据库模块
│   │   ├── __init__.py
│   │   └── supabase_client.py   # Supabase客户端
│   │
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── logger.py            # 日志配置
│       └── helpers.py           # 辅助函数
│
├── scripts/                      # 脚本和工具
│   └── test_scrapers.py         # 测试所有爬虫
│
├── tests/                        # 单元测试 (待实现)
│   └── __init__.py
│
├── docs/                         # 文档目录
│   ├── README.md                # 项目说明 (已移动)
│   ├── SETUP.md                 # 详细部署指南
│   ├── QUICK_START.md           # 快速开始
│   ├── PROJECT_SUMMARY.md       # 项目总览
│   └── PROJECT_STRUCTURE.md     # 本文件
│
├── .github/                      # GitHub配置
│   └── workflows/
│       └── daily-news.yml       # GitHub Actions工作流
│
├── logs/                         # 日志目录 (自动生成)
│   └── blockchain_daily_YYYYMMDD.log
│
├── output/                       # 输出目录 (备份)
│   └── blockchain-daily-YYYY-MM-DD.md
│
├── main.py                       # 主程序入口 ⭐️
├── requirements.txt              # Python依赖列表
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git忽略配置
└── README.md                     # 项目首页README
```

## 🏗️ 模块说明

### 1. src/scrapers/ - 爬虫模块

**基类** (`base.py`):
- 定义统一的爬虫接口
- 提供通用的HTTP请求、时间过滤等功能
- 所有具体爬虫继承此基类

**具体爬虫**:
- `jinse.py` - 金色财经 (API直接调用) ✅ 工作正常
- `odaily.py` - Odaily (通过RSSHub RSS源)
- `cointelegraph.py` - Cointelegraph (通过RSSHub)
- `coindesk.py` - CoinDesk (通过RSSHub)
- `theblock.py` - The Block (通过RSSHub)

### 2. src/processors/ - 数据处理模块

**AI处理器** (`ai_processor.py`):
- 使用OpenRouter调用LLM
- 支持多种模型 (Gemini/Claude/GPT)
- 智能分类和摘要生成
- 标签提取

**内容过滤器** (`content_filter.py`):
- 新闻去重
- 低质量内容过滤
- 按时间排序

### 3. src/database/ - 数据库模块

**Supabase客户端** (`supabase_client.py`):
- CRUD操作
- 自动生成slug
- 支持更新和创建

### 4. src/utils/ - 工具模块

**日志工具** (`logger.py`):
- 统一日志配置
- 文件和控制台双输出
- 按日期归档

**辅助函数** (`helpers.py`):
- 文本清理
- 标题提取
- 去重和过滤

## 📊 数据流

```
1. 主程序 (main.py)
   ↓
2. 多个爬虫并行抓取
   ├─ 金色财经
   ├─ Odaily
   ├─ Cointelegraph
   ├─ CoinDesk
   └─ The Block
   ↓
3. 内容过滤器
   ├─ 去重
   ├─ 质量过滤
   └─ 排序
   ↓
4. AI处理器
   ├─ 分类
   ├─ 摘要
   └─ 标签提取
   ↓
5. Supabase数据库
   └─ posts表
   ↓
6. 备份到output/目录
```

## 🔧 配置文件

### `src/config.py`

```python
# 数据源配置
NEWS_SOURCES = {
    'jinse': {
        'enabled': True,      # 是否启用
        'api_url': '...',    # API地址
        'language': 'zh',    # 语言
    },
    # ...
}

# AI配置
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
```

## 🧪 测试

### 测试爬虫

```bash
python scripts/test_scrapers.py
```

输出示例:
```
✓ 金色财经: 20 items
✗ Odaily: 0 items
✗ Cointelegraph: 0 items
...
```

### 测试完整流程

```bash
python main.py
```

## 📝 日志

日志保存在 `logs/blockchain_daily_YYYYMMDD.log`:

```
2025-11-23 13:00:00 - blockchain_daily - INFO - Starting...
2025-11-23 13:00:01 - scraper.金色财经 - INFO - Fetching news...
2025-11-23 13:00:03 - scraper.金色财经 - INFO - Successfully fetched 20 items
...
```

## 📦 依赖管理

### 核心依赖

- `requests` - HTTP请求
- `supabase` - 数据库客户端
- `openai` - OpenRouter API调用
- `pytz` - 时区处理
- `python-dotenv` - 环境变量管理

### 安装

```bash
pip install -r requirements.txt
```

## 🚀 扩展指南

### 添加新的数据源

1. 在 `src/scrapers/` 创建新文件 `newsource.py`
2. 继承 `BaseScraper` 类
3. 实现 `fetch_news()` 方法
4. 在 `src/scrapers/__init__.py` 中导出
5. 在 `src/config.py` 中添加配置
6. 在 `main.py` 中添加初始化代码

示例:
```python
from src.scrapers.base import BaseScraper

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__('NewSource')
        self.api_url = NEWS_SOURCES['newsource']['api_url']

    def fetch_news(self, hours=24):
        # 实现抓取逻辑
        ...
```

### 修改AI提示词

编辑 `src/processors/ai_processor.py` 中的 `_create_prompt()` 方法。

### 更改数据库表

修改 `src/database/supabase_client.py` 中的方法。

## 🎯 最佳实践

1. **日志**: 所有模块都使用 `get_logger()` 获取logger
2. **错误处理**: 爬虫失败不影响其他爬虫
3. **配置**: 所有配置集中在 `src/config.py`
4. **备份**: 数据库+文件双备份
5. **测试**: 使用 `scripts/test_scrapers.py` 测试新功能

## 📈 项目统计

- **Python文件**: 19个
- **数据源**: 5个 (1个工作正常)
- **代码行数**: ~1500行
- **依赖包**: 40+个

---

**架构设计目标**: 清晰、模块化、易扩展、易维护 ✅
