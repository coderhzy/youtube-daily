# 项目总览

## 已完成功能 ✅

你的区块链每日新闻自动化系统已经完全搭建好了！系统具备以下功能:

### 核心功能

1. **新闻爬虫模块**
   - ✅ Odaily 快讯爬虫
   - ✅ 金色财经快讯爬虫
   - ✅ 时间过滤(可配置抓取过去N小时的新闻)
   - ✅ 内容清洗和格式化

2. **AI 智能处理**
   - ✅ OpenRouter API 集成
   - ✅ 支持多种 AI 模型(Claude/GPT/Gemini等)
   - ✅ 自动分类:市场动态、政策监管、DeFi、NFT、技术前沿等
   - ✅ 智能摘要生成
   - ✅ 自动提取标签
   - ✅ Markdown 格式输出

3. **数据处理**
   - ✅ 新闻去重
   - ✅ 低质量内容过滤
   - ✅ 时间排序

4. **数据库集成**
   - ✅ Supabase 客户端
   - ✅ 自动创建/更新文章
   - ✅ Slug 自动生成
   - ✅ 完整的 CRUD 操作

5. **自动化**
   - ✅ GitHub Actions 工作流
   - ✅ 定时任务(每天北京时间 8:00)
   - ✅ 手动触发支持
   - ✅ 日志上传

6. **开发工具**
   - ✅ 本地测试脚本
   - ✅ 完整的日志记录
   - ✅ 错误处理和降级方案
   - ✅ 环境变量配置

## 文件结构

```
youtube-daily/
├── .github/
│   └── workflows/
│       └── daily-news.yml          # GitHub Actions 自动化工作流
│
├── scrapers/                       # 爬虫模块
│   ├── __init__.py
│   ├── odaily.py                   # Odaily 爬虫
│   └── jinse.py                    # 金色财经爬虫
│
├── ai_processor.py                 # AI 处理器(OpenRouter)
├── database.py                     # Supabase 数据库操作
├── config.py                       # 配置管理
├── main.py                         # 主程序入口
├── test_local.py                   # 本地测试脚本
│
├── requirements.txt                # Python 依赖
├── .env.example                    # 环境变量模板
├── .gitignore                      # Git 忽略配置
│
├── README.md                       # 项目说明
├── SETUP.md                        # 详细部署指南
└── PROJECT_SUMMARY.md              # 本文件
```

## 快速开始

### 方式一: 本地测试

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 3. 运行测试脚本(不需要 Supabase)
python test_local.py

# 4. 运行完整程序
python main.py
```

### 方式二: GitHub Actions 自动化

1. 将代码推送到 GitHub
2. 在 Settings > Secrets 中配置:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENROUTER_API_KEY`
3. 进入 Actions 手动运行或等待定时触发

详见 [SETUP.md](SETUP.md)

## 环境变量配置

复制 `.env.example` 为 `.env` 并填入以下信息:

```env
# Supabase 配置
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# OpenRouter 配置
OPENROUTER_API_KEY=sk-or-v1-xxx...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# 功能开关
ENABLE_AI_SUMMARY=true
```

## 工作流程

```
1. 定时触发(每天早上8点)
   │
   ▼
2. 运行爬虫
   ├─ Odaily API
   └─ 金色财经 API
   │
   ▼
3. 数据处理
   ├─ 去重
   ├─ 过滤低质量
   └─ 排序
   │
   ▼
4. AI 处理
   ├─ 智能分类
   ├─ 生成摘要
   └─ 提取标签
   │
   ▼
5. 存入 Supabase
   └─ posts 表
   │
   ▼
6. IPFS 博客自动展示
```

## 数据库表结构

```sql
posts (
  id          UUID PRIMARY KEY,
  slug        TEXT UNIQUE NOT NULL,      -- 如: blockchain-daily-2025-11-23
  title       TEXT NOT NULL,             -- 如: 区块链每日观察 - 2025-11-23
  date        DATE NOT NULL,             -- 2025-11-23
  description TEXT,                      -- AI 生成的摘要
  tags        TEXT[],                    -- ['区块链', 'DeFi', 'NFT']
  content     TEXT NOT NULL,             -- Markdown 格式的文章内容
  created_at  TIMESTAMPTZ,
  updated_at  TIMESTAMPTZ
)
```

## 测试清单

### 本地测试

- [ ] 运行 `python test_local.py` 测试爬虫
- [ ] 检查 `test_output.md` 查看 AI 生成的内容
- [ ] 运行 `python main.py` 完整测试
- [ ] 查看 `blockchain_daily.log` 日志

### GitHub Actions 测试

- [ ] 推送代码到 GitHub
- [ ] 配置所有必需的 Secrets
- [ ] 手动触发工作流
- [ ] 检查 Actions 运行日志
- [ ] 验证 Supabase 中有新数据

### 博客展示测试

- [ ] 在 IPFS 博客中查询 posts 表
- [ ] 确认文章正确显示
- [ ] 检查标签和分类

## 成本估算

### 免费服务
- GitHub Actions: ✅ 免费
- Supabase: ✅ 免费套餐足够

### 付费服务 (OpenRouter)
- Claude 3.5 Sonnet: ~$0.02/天 = **$0.60/月**
- GPT-4 Turbo: ~$0.05/天 = $1.50/月
- Gemini Pro: ~$0.002/天 = $0.06/月

**推荐**: Claude 3.5 Sonnet (性价比最高)

## 下一步

### 立即可做

1. ✅ **配置环境变量**: 填写 `.env` 文件
2. ✅ **本地测试**: 运行 `python test_local.py`
3. ✅ **部署到 GitHub**: 参考 [SETUP.md](SETUP.md)

### 可选优化

- [ ] 添加图片抓取和 CDN 上传
- [ ] 集成更多新闻源(如 CoinDesk, The Block)
- [ ] 添加邮件/Telegram 通知
- [ ] 数据分析和可视化
- [ ] 多语言支持
- [ ] 自定义 AI 提示词模板

## 常见问题

### 1. 如何测试爬虫是否正常?

```bash
python test_local.py
```

查看输出,应该能看到抓取的新闻数量。

### 2. 如何修改定时任务时间?

编辑 `.github/workflows/daily-news.yml`:

```yaml
cron: '0 0 * * *'  # UTC 00:00 = 北京时间 08:00
```

### 3. 如何禁用 AI 处理?

在 `.env` 中设置:

```env
ENABLE_AI_SUMMARY=false
```

系统会使用基础格式化,直接保存原始新闻。

### 4. API 被限流怎么办?

- 确保 GitHub Actions 只每天运行一次
- 添加请求延迟: `time.sleep(1)`
- 联系新闻源网站获取官方 API Key

### 5. OpenRouter 余额不足?

- 登录 OpenRouter 充值
- 或切换到更便宜的模型(如 Gemini Pro)
- 或禁用 AI 处理

## 技术栈

- **Python 3.11+**: 主要编程语言
- **Requests**: HTTP 请求
- **Supabase**: PostgreSQL 数据库
- **OpenRouter**: AI API 聚合服务
- **GitHub Actions**: CI/CD 自动化
- **IPFS**: 博客托管

## 贡献

欢迎提交 Issue 和 Pull Request!

## 许可证

MIT License

---

**准备好了吗? 开始使用吧!** 🚀

1. `cp .env.example .env` - 配置环境变量
2. `python test_local.py` - 本地测试
3. `python main.py` - 发布到数据库
4. 推送到 GitHub 启用自动化

Have fun! 🎉
