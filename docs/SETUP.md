# 部署指南

完整的部署和配置说明。

## 第一步: 获取 Supabase 凭证

1. 访问 [Supabase](https://supabase.com/) 并登录
2. 选择你的项目或创建新项目
3. 进入 **Settings** > **API**
4. 复制以下信息:
   - **Project URL** (SUPABASE_URL)
   - **Anon/Public Key** (SUPABASE_KEY)

### 创建数据表

在 Supabase 的 SQL Editor 中执行:

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

ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON posts
  FOR SELECT
  USING (true);
```

## 第二步: 获取 OpenRouter API Key

1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册/登录账号
3. 进入 **Keys** 页面创建新的 API Key
4. 充值一些余额(建议 $5-10,可以用很久)
5. 复制 API Key

### 可选模型

- `anthropic/claude-3.5-sonnet` (推荐) - 高质量输出
- `openai/gpt-4-turbo` - 稳定可靠
- `google/gemini-pro-1.5` - 性价比高
- `anthropic/claude-3-haiku` - 最便宜

## 第三步: 配置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** > **Secrets and variables** > **Actions**
3. 点击 **New repository secret** 添加以下密钥:

| Secret Name | Value | 说明 |
|------------|-------|------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | 你的 Supabase 项目 URL |
| `SUPABASE_KEY` | `eyJxxx...` | 你的 Supabase Anon Key |
| `OPENROUTER_API_KEY` | `sk-or-v1-xxx...` | 你的 OpenRouter API Key |
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-sonnet` | (可选) AI 模型 |

## 第四步: 启用 GitHub Actions

1. 在仓库中,进入 **Actions** 标签页
2. 如果 Actions 被禁用,点击 **I understand my workflows, go ahead and enable them**
3. 找到 **Blockchain Daily News Bot** 工作流
4. 点击 **Run workflow** 手动测试运行

## 第五步: 验证

### 检查 GitHub Actions 运行日志

1. 进入 **Actions** 页面
2. 点击最近的运行记录
3. 查看每个步骤的输出
4. 如果失败,查看错误信息

### 检查 Supabase 数据

1. 进入 Supabase 项目
2. 打开 **Table Editor**
3. 选择 `posts` 表
4. 确认有新记录插入

### 本地测试

```bash
# 1. 克隆仓库
git clone <your-repo>
cd youtube-daily

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 .env
cp .env.example .env
# 编辑 .env 填入你的配置

# 5. 运行测试
python main.py
```

## 定时任务说明

当前配置为每天北京时间早上 8:00 运行:

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00 = 北京时间 08:00
```

### 修改运行时间

| 北京时间 | Cron 表达式 | 说明 |
|---------|------------|------|
| 08:00 | `0 0 * * *` | 当前配置 |
| 09:00 | `0 1 * * *` | 每天早上9点 |
| 12:00 | `0 4 * * *` | 每天中午12点 |
| 18:00 | `0 10 * * *` | 每天下午6点 |
| 20:00 | `0 12 * * *` | 每天晚上8点 |

### 手动触发

除了定时运行,你也可以随时手动触发:

1. 进入 **Actions** 页面
2. 选择 **Blockchain Daily News Bot**
3. 点击 **Run workflow** 按钮
4. 选择分支后点击运行

## 常见问题排查

### 1. GitHub Actions 失败

**错误**: `Error: Process completed with exit code 1`

**解决**:
- 检查 Secrets 是否正确配置
- 查看详细日志定位具体错误
- 确保 Supabase URL 和 Key 有效

### 2. Supabase 连接失败

**错误**: `ValueError: SUPABASE_URL and SUPABASE_KEY must be set`

**解决**:
- 确认已在 GitHub Secrets 中添加 `SUPABASE_URL` 和 `SUPABASE_KEY`
- 检查 Secret 名称是否完全匹配(区分大小写)

### 3. OpenRouter API 调用失败

**错误**: `API key not found` 或 `Insufficient credits`

**解决**:
- 检查 `OPENROUTER_API_KEY` 是否正确
- 确认 OpenRouter 账户有足够余额
- 可以临时设置 `ENABLE_AI_SUMMARY=false` 跳过 AI 处理

### 4. 没有抓取到新闻

**可能原因**:
- API 接口变更(Odaily/金色财经 可能会更新接口)
- 网络问题或被限流
- 过去 24 小时内确实没有新闻

**解决**:
- 检查日志中的具体错误信息
- 可以尝试增加抓取时间范围到 48 小时
- 检查 API URL 是否仍然有效

### 5. 数据重复

**问题**: 每次运行都创建新文章而不是更新

**解决**:
- 检查 `slug` 字段是否设置为 UNIQUE
- 确认 `database.py` 中的 `create_daily_post` 方法有更新逻辑

## 高级配置

### 添加其他新闻源

1. 在 `scrapers/` 目录创建新的爬虫文件
2. 继承基础爬虫类或实现 `fetch_news()` 方法
3. 在 `main.py` 中导入并调用

### 自定义 AI 提示词

编辑 `ai_processor.py` 中的 `_create_prompt()` 方法,修改提示词以改变输出风格。

### 添加通知

可以在 GitHub Actions 中添加通知步骤:

```yaml
- name: Send notification
  if: success()
  run: |
    curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
      -d "chat_id=<YOUR_CHAT_ID>" \
      -d "text=今日区块链新闻已更新!"
```

## 成本估算

### OpenRouter 费用

假设每天生成 1 篇博客,平均使用:
- 输入: ~2000 tokens (新闻内容)
- 输出: ~1500 tokens (生成文章)

**Claude 3.5 Sonnet**:
- 输入: $3/M tokens
- 输出: $15/M tokens
- 每篇成本: ~$0.02
- 月成本: ~$0.60

**GPT-4 Turbo**:
- 输入: $10/M tokens
- 输出: $30/M tokens
- 每篇成本: ~$0.05
- 月成本: ~$1.50

**Gemini Pro 1.5**:
- 输入: $0.35/M tokens
- 输出: $1.05/M tokens
- 每篇成本: ~$0.002
- 月成本: ~$0.06

### 其他服务

- GitHub Actions: 免费(公开仓库)
- Supabase: 免费套餐足够使用

**总成本**: 每月 $0.06 - $1.50,取决于模型选择

## 后续优化

- [ ] 添加图片抓取和上传
- [ ] 支持多语言输出
- [ ] 添加邮件通知
- [ ] 集成更多新闻源
- [ ] 添加数据分析和统计
- [ ] 支持自定义模板

## 技术支持

如遇问题,请:

1. 查看 [README.md](README.md) 了解基础用法
2. 检查 GitHub Actions 运行日志
3. 查看 `blockchain_daily.log` 本地日志
4. 在 GitHub Issues 中提问

祝使用愉快! 🚀
