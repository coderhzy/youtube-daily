# GitHub Actions 部署指南

本文档详细说明如何在 GitHub 上配置自动化部署。

## 📋 前置条件

1. ✅ 本地系统已经测试成功（`python main.py` 运行正常）
2. ✅ Supabase 数据库已配置（执行了 `docs/SUPABASE_SETUP.sql`）
3. ✅ 拥有以下 API Keys：
   - Supabase URL 和 Service Role Key
   - OpenRouter API Key

## 🚀 部署步骤

### 1. 创建 GitHub 仓库

在 GitHub 上创建新仓库：
- 仓库名称：`blockchain-daily-observer`（或任意名称）
- 可见性：Public 或 Private（推荐 Private，因为涉及 API keys）
- **不要**初始化 README、.gitignore 或 LICENSE（已经在本地创建）

### 2. 推送代码到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/blockchain-daily-observer.git

# 推送代码
git push -u origin master
```

### 3. 配置 GitHub Secrets

这是**最关键**的一步！在 GitHub 仓库中配置环境变量。

#### 3.1 进入 Secrets 设置

1. 打开你的 GitHub 仓库
2. 点击 **Settings** (设置)
3. 左侧菜单选择 **Secrets and variables** > **Actions**
4. 点击 **New repository secret** (新建仓库密钥)

#### 3.2 添加以下 Secrets

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase 项目 URL |
| `SUPABASE_KEY` | `eyJhbGci...` | Supabase **service_role** key（不是 anon key！） |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | OpenRouter API Key |
| `OPENROUTER_MODEL` | `google/gemini-2.0-flash-exp:free` | 使用的模型（可选，有默认值） |

**获取 Supabase Credentials：**
1. 登录 [Supabase](https://supabase.com)
2. 选择你的项目
3. 点击 **Settings** (齿轮图标)
4. 选择 **API**
5. 复制：
   - `URL` → `SUPABASE_URL`
   - `service_role` key → `SUPABASE_KEY` ⚠️ **重要：使用 service_role，不是 anon key！**

**获取 OpenRouter API Key：**
1. 访问 [OpenRouter](https://openrouter.ai)
2. 登录后进入 [Keys 页面](https://openrouter.ai/keys)
3. 创建新的 API Key
4. 复制 `sk-or-v1-...` → `OPENROUTER_API_KEY`

#### 3.3 验证 Secrets 配置

配置完成后，Secrets 页面应该显示：

```
✓ SUPABASE_URL
✓ SUPABASE_KEY
✓ OPENROUTER_API_KEY
✓ OPENROUTER_MODEL (可选)
```

### 4. 启用 GitHub Actions

GitHub Actions 应该自动启用。如果没有：

1. 进入仓库的 **Actions** 标签页
2. 如果显示"Workflows disabled"，点击 **Enable workflows**

### 5. 手动触发测试运行

在正式等待定时任务前，建议先手动测试：

1. 进入 **Actions** 标签页
2. 左侧选择 **Blockchain Daily News Bot**
3. 点击右侧 **Run workflow** 按钮
4. 点击绿色的 **Run workflow** 确认

### 6. 查看运行结果

#### 6.1 实时监控

点击正在运行的 workflow，可以看到实时日志：
- **Checkout repository** - 拉取代码
- **Set up Python** - 安装 Python
- **Install dependencies** - 安装依赖包
- **Run Daily News Bot** - 运行主程序
- **Upload logs** - 上传日志文件

#### 6.2 检查输出

展开 **Run Daily News Bot** 步骤，应该看到：

```
[Step 1/4] Fetching news from sources...
  金色财经: 60 items
Total fetched: 60 news items

[Step 2/4] Processing and filtering news...
After processing: 60 news items

[Step 3/4] Generating article with AI...
Generated article: 区块链每日观察 - 2025-11-23
Tags: DeFi, 区块链, 政策监管...
Content length: 15000+ characters

[Step 4/4] Saving to Supabase database...
Successfully saved post to database
  Post ID: xxx
  Post Slug: blockchain-daily-2025-11-23

================================================================================
Blockchain Daily News Bot - Completed Successfully!
================================================================================
```

#### 6.3 下载日志

如果需要详细日志：
1. Workflow 运行完成后
2. 滚动到底部 **Artifacts** 部分
3. 下载 **bot-logs** 文件
4. 解压后可以查看完整日志

### 7. 验证数据库

在 Supabase 中验证数据是否成功保存：

```sql
SELECT id, slug, title, date, created_at
FROM posts
ORDER BY date DESC
LIMIT 5;
```

应该能看到新生成的文章记录。

## ⏰ 定时运行

GitHub Actions 已配置为**每天北京时间早上 5:00** 自动运行（UTC 21:00）。

### 定时任务说明

```yaml
schedule:
  - cron: '0 21 * * *'  # UTC 21:00 = 北京时间 05:00
```

- 📅 频率：每天一次
- ⏰ 时间：北京时间 05:00（UTC 21:00）
- 🔄 自动执行：无需手动触发

### 修改运行时间

如果想更改运行时间，编辑 `.github/workflows/daily-news.yml`：

```yaml
schedule:
  # 北京时间 08:00 (UTC 00:00)
  - cron: '0 0 * * *'

  # 北京时间 12:00 (UTC 04:00)
  - cron: '0 4 * * *'

  # 北京时间 20:00 (UTC 12:00)
  - cron: '0 12 * * *'
```

**提交更改后**，新的定时任务会在下次触发时生效。

## 🔍 故障排查

### 问题 1：Workflow 运行失败

**检查步骤：**
1. 查看 Actions 日志，找到具体错误信息
2. 常见错误：
   - `Invalid URL` → 检查 `SUPABASE_URL` 格式
   - `No auth credentials found` → 检查 `OPENROUTER_API_KEY`
   - `row-level security policy` → 使用 `service_role` key

### 问题 2：Secrets 配置错误

**解决方法：**
1. 进入 Settings > Secrets and variables > Actions
2. 点击 Secret 名称旁的 **Update**
3. 重新粘贴正确的值
4. 保存后重新运行 workflow

### 问题 3：依赖安装失败

**可能原因：**
- `requirements.txt` 中的包版本冲突
- GitHub Actions 环境缺少系统依赖

**解决方法：**
1. 本地测试 `pip install -r requirements.txt`
2. 确保 `requirements.txt` 是最新的
3. 如果需要系统依赖，在 workflow 中添加：
   ```yaml
   - name: Install system dependencies
     run: |
       sudo apt-get update
       sudo apt-get install -y libssl-dev
   ```

### 问题 4：定时任务未触发

**可能原因：**
- GitHub Actions 在低活跃度仓库中可能延迟
- 免费账户有使用限制

**解决方法：**
1. 确保仓库有提交活动
2. 手动触发几次 workflow
3. 检查 Actions 标签页是否启用

### 问题 5：日志文件未上传

**检查：**
- 确保 `logs/` 目录在 workflow 运行时被创建
- 查看 "Upload logs" 步骤的输出

## 📊 监控运行状态

### 1. 添加 Status Badge

在 `README.md` 顶部添加徽章：

```markdown
[![Daily News Bot](https://github.com/YOUR_USERNAME/blockchain-daily-observer/actions/workflows/daily-news.yml/badge.svg)](https://github.com/YOUR_USERNAME/blockchain-daily-observer/actions/workflows/daily-news.yml)
```

### 2. 查看历史记录

在 Actions 标签页可以看到：
- ✅ 成功运行的次数
- ❌ 失败的记录
- ⏱️ 每次运行的时长
- 📊 趋势图表

### 3. 邮件通知

GitHub 默认会在 workflow 失败时发送邮件通知到你的注册邮箱。

## 🎯 最佳实践

1. **定期检查**：
   - 每周查看一次 Actions 运行记录
   - 确保文章正常生成并保存到数据库

2. **日志审查**：
   - 下载日志文件检查是否有警告
   - 关注抓取的新闻数量是否稳定

3. **API 配额监控**：
   - OpenRouter：查看 [Dashboard](https://openrouter.ai/activity)
   - Supabase：查看 [Usage](https://supabase.com/dashboard/project/_/settings/billing)

4. **定期更新**：
   - 每月运行 `pip list --outdated` 检查依赖更新
   - 关注 GitHub Actions 的版本更新

## ✅ 部署完成检查清单

- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 GitHub
- [ ] Secrets 已正确配置（4个）
- [ ] 手动触发测试成功
- [ ] Supabase 中有新数据
- [ ] 日志文件已上传
- [ ] 定时任务已启用
- [ ] Status Badge 已添加到 README

全部完成后，系统将**每天早上 5 点自动运行**，无需任何手动操作！🎉

## 🆘 获取帮助

如果遇到问题：
1. 查看 [GitHub Actions 文档](https://docs.github.com/en/actions)
2. 查看项目的 [Issues](https://github.com/YOUR_USERNAME/blockchain-daily-observer/issues)
3. 检查本项目的其他文档：
   - [`README.md`](../README.md) - 项目总览
   - [`docs/SUPABASE_SETUP.sql`](SUPABASE_SETUP.sql) - 数据库设置
   - [`docs/OPTIMIZATION.md`](OPTIMIZATION.md) - 优化配置

---

**部署成功后，系统将完全自动化运行，每天为你生成高质量的区块链行业观察文章！** 🚀
