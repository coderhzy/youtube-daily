# 区块链每日新闻自动化系统

自动抓取 Odaily 和金色财经的区块链新闻,使用 AI 处理后存入 Supabase 数据库,为你的博客提供每日更新的高质量内容。

## 功能特性

- 每天自动抓取 Odaily 和金色财经过去 24 小时的区块链新闻
- 使用 OpenRouter 调用 AI (Claude/GPT) 进行智能分类和摘要
- 自动去重和质量过滤
- 将处理后的内容存入 Supabase 数据库
- 支持 GitHub Actions 定时自动化运行
- 完整的日志记录和错误处理

## 系统架构

```
┌─────────────────┐
│  GitHub Actions │  每天早上8点触发
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   新闻爬虫模块   │  Odaily + 金色财经
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI处理器      │  OpenRouter (Claude/GPT)
│   - 智能分类    │
│   - 内容摘要    │
│   - 标签提取    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Supabase 数据库│  存储博客文章
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   IPFS 博客     │  自动展示最新内容
└─────────────────┘
```

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd youtube-daily
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`:

```bash
cp .env.example .env
```

编辑 `.env` 文件,填入你的配置:

```env
# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# OpenRouter配置
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# 启用AI摘要
ENABLE_AI_SUMMARY=true
```

### 4. 本地测试

```bash
python main.py
```

### 5. 配置 GitHub Actions

在 GitHub 仓库设置中添加以下 Secrets:

- `SUPABASE_URL`: 你的 Supabase 项目 URL
- `SUPABASE_KEY`: 你的 Supabase Anon Key
- `OPENROUTER_API_KEY`: 你的 OpenRouter API Key
- `OPENROUTER_MODEL`: (可选) AI 模型,默认为 `anthropic/claude-3.5-sonnet`

配置完成后,GitHub Actions 将每天北京时间早上 8:00 自动运行。

## 数据库表结构

系统使用以下 Supabase 表结构:

```sql
CREATE TABLE IF NOT EXISTS posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  date DATE NOT NULL,
  description TEXT,
  tags TEXT[] DEFAULT '{}',
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(date DESC);
CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
```

## 文件结构

```
.
├── .github/
│   └── workflows/
│       └── daily-news.yml      # GitHub Actions 工作流
├── scrapers/
│   ├── __init__.py
│   ├── odaily.py               # Odaily 爬虫
│   └── jinse.py                # 金色财经爬虫
├── ai_processor.py             # AI 处理器
├── database.py                 # Supabase 数据库操作
├── config.py                   # 配置文件
├── main.py                     # 主程序
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量示例
├── .gitignore
└── README.md
```

## 工作流程

1. **抓取新闻** (Step 1/4)
   - 从 Odaily 和金色财经抓取过去 24 小时的新闻
   - 解析 API 响应,提取标题、内容、发布时间等信息

2. **去重和过滤** (Step 2/4)
   - 基于内容相似度去除重复新闻
   - 过滤低质量内容(内容过短、缺少关键信息等)
   - 按时间排序

3. **AI 处理** (Step 3/4)
   - 调用 OpenRouter API 使用 Claude/GPT 处理新闻
   - 智能分类:市场动态、政策监管、DeFi、NFT、技术前沿等
   - 生成文章摘要和标签
   - 输出 Markdown 格式的博客内容

4. **存入数据库** (Step 4/4)
   - 将处理后的文章存入 Supabase
   - 自动生成 slug (格式: `blockchain-daily-2025-11-23`)
   - 如果当天已有文章则更新,否则创建新文章

## OpenRouter 模型选择

系统默认使用 `anthropic/claude-3.5-sonnet`,你也可以选择其他模型:

- `anthropic/claude-3.5-sonnet` - 高质量,推荐
- `openai/gpt-4-turbo` - 稳定可靠
- `google/gemini-pro-1.5` - 性价比高
- `meta-llama/llama-3.1-70b-instruct` - 开源选项

在 `.env` 文件中修改 `OPENROUTER_MODEL` 即可。

## 自定义配置

### 修改抓取时间范围

编辑 `main.py` 中的 `hours` 参数:

```python
odaily_news = odaily_scraper.fetch_news(hours=24)  # 改为其他小时数
```

### 修改定时任务时间

编辑 `.github/workflows/daily-news.yml`:

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00 = 北京时间 08:00
```

### 禁用 AI 处理

如果不想使用 AI,可以在 `.env` 中设置:

```env
ENABLE_AI_SUMMARY=false
```

系统将使用基础格式化,直接按来源分组展示新闻。

## 常见问题

### 1. API 限流怎么办?

- Odaily 和金色财经的 API 通常有访问频率限制
- 建议在 GitHub Actions 中设置合理的运行频率(每天一次)
- 如遇到 403/429 错误,可适当增加请求间隔

### 2. OpenRouter 费用问题

- OpenRouter 按使用量计费,每天一篇博客成本很低
- Claude 3.5 Sonnet: ~$0.01-0.03/篇
- GPT-4 Turbo: ~$0.02-0.05/篇
- 可以选择更便宜的模型降低成本

### 3. 如何测试单个模块?

```python
# 测试爬虫
from scrapers import OdailyScraper
scraper = OdailyScraper()
news = scraper.fetch_news(hours=24)
print(f"Fetched {len(news)} news items")

# 测试数据库
from database import SupabaseDB
db = SupabaseDB()
posts = db.get_recent_posts(limit=5)
print(posts)
```

## 日志和调试

- 日志文件: `blockchain_daily.log`
- GitHub Actions 日志: 在 Actions 页面查看运行记录
- 可通过 `logging.basicConfig(level=logging.DEBUG)` 启用详细日志

## 部署到 IPFS

由于你的博客已经部署在 IPFS 上,系统会自动将新文章写入 Supabase,你的博客前端从数据库读取数据即可展示最新内容,无需重新部署。

## 贡献

欢迎提交 Issue 和 Pull Request!

## 许可证

MIT License

## 致谢

- [Odaily](https://www.odaily.news/) - 区块链新闻源
- [金色财经](https://www.jinse.cn/) - 区块链新闻源
- [OpenRouter](https://openrouter.ai/) - AI API 聚合服务
- [Supabase](https://supabase.com/) - 开源数据库服务
