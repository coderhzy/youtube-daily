# 快速开始指南

## ✅ 系统状态

你的区块链每日新闻自动化系统已经完成并测试通过！

### 当前工作状态:
- ✅ 金色财经新闻爬虫 (20条新闻/天)
- ✅ AI 智能处理 (Gemini 2.5 Flash)
- ✅ Supabase 数据库集成
- ⚠️ Odaily爬虫 (RSSHub超时,已配置为可选)

### 成本:
- **金色财经 API**: 免费
- **AI处理 (Gemini 2.5 Flash)**: ~$0.001/天 ≈ **$0.03/月**
- **GitHub Actions**: 免费
- **Supabase**: 免费
- **总计**: ~$0.03/月 (几乎免费!)

---

## 🚀 30秒快速部署

### 1. 配置环境变量

```bash
cd /Users/he/Downloads/youtube-daily
cp .env.example .env
```

编辑 `.env` 文件,填入你的配置:

```env
# Supabase配置 (必需)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# OpenRouter配置 (必需)
OPENROUTER_API_KEY=sk-or-v1-xxx...
OPENROUTER_MODEL=google/gemini-2.5-flash

# 是否启用AI摘要 (建议true)
ENABLE_AI_SUMMARY=true
```

### 2. 本地测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试爬虫和AI (不写数据库)
python test_local.py

# 查看生成的文章
cat test_output.md

# 完整运行 (写入数据库)
python main.py
```

### 3. 部署到 GitHub

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit: Blockchain daily news automation"

# 推送到GitHub
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 4. 配置 GitHub Secrets

在 GitHub 仓库的 **Settings** > **Secrets and variables** > **Actions** 中添加:

| Name | Value | 备注 |
|------|-------|------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | 你的Supabase项目URL |
| `SUPABASE_KEY` | `eyJxxx...` | Supabase Anon Key |
| `OPENROUTER_API_KEY` | `sk-or-v1-xxx...` | OpenRouter API Key |
| `OPENROUTER_MODEL` | `google/gemini-2.5-flash` | (可选) 默认已配置 |

### 5. 启用自动化

- 进入 GitHub 仓库的 **Actions** 页面
- 点击 **I understand my workflows, go ahead and enable them**
- 点击 **Run workflow** 手动测试
- 查看运行日志确认成功

✅ 完成！系统将每天早上 5:00 (北京时间) 自动运行

---

## 📋 预期效果

### 每天自动完成的任务:

1. **抓取新闻** (05:00 AM)
   - 金色财经: ~15-20条区块链新闻
   - Odaily: 备用(如果RSSHub可用)

2. **AI 处理**
   - 智能分类:市场动态、政策监管、DeFi、技术前沿等
   - 生成摘要和标签
   - 输出专业的 Markdown 文章

3. **存入数据库**
   - 写入 Supabase `posts` 表
   - Slug: `blockchain-daily-2025-11-23`
   - 包含完整的标题、内容、标签

4. **IPFS 博客展示**
   - 你的博客从 Supabase 读取数据
   - 自动展示最新文章
   - 无需重新部署

### 生成文章示例:

```markdown
# 区块链每日观察 - 2025-11-23

## 📊 市场动态
- 巨鲸循环贷做多WBTC，均价85376.5美元
- Bitwise CEO增持比特币，买入价约85,000美元
- 恐慌与贪婪指数过去一周均值仅为10，市场维持极度恐慌状态

## 🏛️ 政策监管
- 特立尼达与多巴哥通过加密监管法案，为FATF评估做准备
- 香港财政司司长陈茂波：香港成为资金避险安全港

## 🔧 技术前沿
- Monad主网将于下周一上线
- Cardano因旧代码漏洞发生短暂性链分裂
```

---

## 🛠️ 常见问题

### Q: Odaily 爬虫为什么超时?

A: RSSHub 服务器在国内可能不稳定。系统已配置为:
- 如果 Odaily 失败,自动跳过
- 金色财经仍然正常工作
- 不影响整体流程

**解决方案 (可选)**:
1. 自建 RSSHub 实例
2. 使用 Odaily 官方 API (如果有)
3. 只使用金色财经 (已足够)

### Q: 如何修改定时任务时间?

A: 编辑 `.github/workflows/daily-news.yml` 中的 cron 表达式:

```yaml
schedule:
  - cron: '0 21 * * *'  # UTC 21:00 = 北京时间 05:00
```

### Q: 如何更换 AI 模型?

A: 在 `.env` 中修改:

```env
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # 更高质量,稍贵 (~$0.02/天)
OPENROUTER_MODEL=google/gemini-2.5-flash      # 当前配置 (~$0.001/天)
OPENROUTER_MODEL=openai/gpt-4o-mini          # 中等质量 (~$0.005/天)
```

### Q: 如何禁用 AI 处理?

A: 在 `.env` 中设置:

```env
ENABLE_AI_SUMMARY=false
```

系统将使用基础格式化,直接保存原始新闻。

### Q: 数据库中看不到文章?

检查清单:
1. ✅ Supabase URL 和 Key 正确?
2. ✅ `posts` 表已创建?
3. ✅ RLS 策略允许插入?
4. ✅ GitHub Actions 运行成功?

查看 GitHub Actions 日志:
- 进入 **Actions** 页面
- 点击最近的运行记录
- 查看 "Run Daily News Bot" 步骤的输出

---

## 📊 监控和维护

### 查看运行状态

**方式1: GitHub Actions**
- 进入仓库的 **Actions** 页面
- 查看最近的运行记录
- 绿色 ✅ = 成功,红色 ❌ = 失败

**方式2: Supabase**
- 打开 Supabase 项目
- 进入 **Table Editor** > **posts**
- 确认每天有新记录

**方式3: IPFS 博客**
- 访问你的博客
- 检查是否显示最新文章

### 日志位置

- **本地日志**: `blockchain_daily.log`
- **GitHub 日志**: Actions 页面下载 artifacts
- **实时日志**: 查看 Actions 运行输出

---

## 🎯 下一步优化

### 可选改进:

1. **添加更多新闻源**
   - 创建 `scrapers/coindesk.py`
   - 创建 `scrapers/theblock.py`
   - 在 `main.py` 中导入调用

2. **添加通知**
   ```python
   # 在 main.py 最后添加
   import requests
   telegram_token = "YOUR_BOT_TOKEN"
   chat_id = "YOUR_CHAT_ID"
   message = f"✅ 今日区块链新闻已更新!\n\n{result.get('slug')}"
   requests.post(
       f"https://api.telegram.org/bot{telegram_token}/sendMessage",
       json={"chat_id": chat_id, "text": message}
   )
   ```

3. **自定义 AI 提示词**
   - 编辑 `ai_processor.py` 中的 `_create_prompt()` 方法
   - 调整输出风格和格式

4. **数据分析**
   - 统计高频关键词
   - 生成每周/每月总结
   - 可视化热点趋势

---

## 💡 提示

- **测试前先备份**: 在修改代码前 `git commit`
- **小步迭代**: 一次只改一个功能
- **查看日志**: 遇到问题先看日志输出
- **善用测试脚本**: `python test_local.py` 不写数据库,安全测试

---

## 🎉 恭喜!

你现在拥有一个:
- ✅ 全自动化的区块链新闻系统
- ✅ AI 驱动的内容生成
- ✅ 几乎零成本运行 (~$0.03/月)
- ✅ 每天 5:00 AM 自动更新

**祝你使用愉快!** 🚀

---

## 📞 获取帮助

- **文档**: 查看 `README.md` 和 `SETUP.md`
- **测试**: 运行 `python test_local.py`
- **调试**: 查看 `blockchain_daily.log`

Happy Automating! 🤖
