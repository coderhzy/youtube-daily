# 区块链每日观察 - 自动化新闻系统

🤖 自动抓取区块链行业新闻，使用 AI 生成深度分析文章（5k-10k字），并自动更新到 Supabase 数据库。

## ✨ 特性

- 📰 **数据源**: 金色财经（支持API分页，60条/24小时）
- 🤖 **AI 深度分析**: 使用 OpenRouter 生成 5k-10k 字的专业深度文章
- 🗄️ **数据库集成**: 自动写入 Supabase，支持 IPFS 博客展示
- ⚙️ **自动化运行**: GitHub Actions 每天早上 5:00 (北京时间) 自动执行
- 📊 **清晰架构**: 模块化设计，易于扩展和维护

## 📂 项目结构

```
youtube-daily/
├── src/                          # 源代码
│   ├── scrapers/                 # 新闻爬虫
│   │   ├── base.py              # 爬虫基类
│   │   ├── jinse.py             # 金色财经
│   │   ├── odaily.py            # Odaily
│   │   ├── cointelegraph.py     # Cointelegraph
│   │   ├── coindesk.py          # CoinDesk
│   │   └── theblock.py          # The Block
│   ├── processors/               # 数据处理
│   │   ├── ai_processor.py      # AI 处理器
│   │   └── content_filter.py    # 内容过滤
│   ├── database/                 # 数据库
│   │   └── supabase_client.py   # Supabase 客户端
│   ├── utils/                    # 工具函数
│   │   ├── logger.py            # 日志配置
│   │   └── helpers.py           # 辅助函数
│   └── config.py                 # 配置管理
│
├── scripts/                      # 测试脚本
│   └── test_scrapers.py         # 测试所有爬虫
│
├── docs/                         # 文档
│   ├── SETUP.md                 # 详细部署指南
│   └── QUICK_START.md           # 快速开始
│
├── .github/workflows/            # GitHub Actions
│   └── daily-news.yml           # 自动化工作流
│
├── main.py                       # 主程序入口
├── requirements.txt              # Python 依赖
└── .env.example                  # 环境变量模板
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入配置
```

需要配置:
- `SUPABASE_URL` - Supabase 项目 URL
- `SUPABASE_KEY` - Supabase Anon Key
- `OPENROUTER_API_KEY` - OpenRouter API Key

### 3. 测试爬虫

```bash
python scripts/test_scrapers.py
```

### 4. 运行主程序

```bash
python main.py
```

生成的文章会保存到:
- Supabase `posts` 表
- `output/` 目录 (备份)

## 📖 文档

- [快速开始](docs/QUICK_START.md) - 30秒快速部署指南
- [详细部署](docs/SETUP.md) - 完整的部署和配置说明
- [项目总览](docs/PROJECT_SUMMARY.md) - 系统架构和设计

## 💰 成本

- GitHub Actions: **免费**
- Supabase: **免费**
- OpenRouter (Gemini 2.0 Flash Exp): **免费** (推荐)
- OpenRouter (Gemini 2.0 Flash): **~$0.003/天 ≈ $0.1/月**

总计: **完全免费！** (使用免费模型)

## 🔧 配置说明

### 核心配置 (`src/config.py`)

```python
# 抓取时间范围
FETCH_HOURS = 24  # 24小时（日更）

# 新闻数量
NEWS_SOURCES = {
    'jinse': {
        'enabled': True,
        'limit': 60,  # 抓取60条新闻（支持API分页）
    }
}

# 目标文章长度
TARGET_ARTICLE_LENGTH = 8000  # 约5k-10k字
```

### 调整文章长度

```python
# 文章太短 (<5k字)
NEWS_SOURCES['jinse']['limit'] = 80

# 文章太长 (>12k字)
NEWS_SOURCES['jinse']['limit'] = 40
```

## 📊 Supabase 数据库设置

### 快速设置

在 Supabase SQL Editor 中执行 [`docs/SUPABASE_SETUP.sql`](docs/SUPABASE_SETUP.sql) 文件即可完成所有设置。

或者手动执行以下步骤：

### 1. 创建表

```sql
CREATE TABLE IF NOT EXISTS posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  date DATE NOT NULL,
  description TEXT,
  tags TEXT[],
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. 配置 Row Level Security (RLS)

```sql
-- 启用 RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 允许所有人读取
CREATE POLICY "Enable read access for all users"
ON posts FOR SELECT
USING (true);

-- 允许插入（使用 anon key）
CREATE POLICY "Enable insert for authenticated users"
ON posts FOR INSERT
WITH CHECK (true);

-- 允许更新
CREATE POLICY "Enable update for authenticated users"
ON posts FOR UPDATE
USING (true);
```

### 3. 创建索引

```sql
CREATE INDEX idx_posts_date ON posts(date DESC);
CREATE INDEX idx_posts_slug ON posts(slug);
```

### 故障排查

如果遇到 `row-level security policy` 错误：

1. **检查 RLS 策略**：确保已执行上面的 RLS 配置
2. **使用 Service Role Key**（仅用于服务器端）：
   ```bash
   # .env 中使用 service_role key（注意安全！）
   SUPABASE_KEY=your_service_role_key
   ```
3. **完全禁用 RLS**（仅开发环境）：
   ```sql
   ALTER TABLE posts DISABLE ROW LEVEL SECURITY;
   ```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

---

**准备好了吗?** 查看 [快速开始指南](docs/QUICK_START.md) 开始使用 🚀
