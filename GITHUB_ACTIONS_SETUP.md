# 🤖 GitHub Actions 自动化部署配置

## ✅ 已完成配置

系统已配置GitHub Actions每日自动运行，包含以下功能：
- ✅ 每天早上5点自动抓取新闻
- ✅ 生成8000字深度文章
- ✅ 生成20张专业图片（封面 + 内容图）
- ✅ 创建纯图片PDF
- ✅ 打包所有图片为ZIP
- ✅ 发送邮件（PDF + 图片ZIP）

---

## 📋 GitHub Secrets 配置

在GitHub仓库中配置以下Secrets（Settings → Secrets and variables → Actions → New repository secret）：

### 必需的Secrets

```bash
# 1. Supabase 数据库
SUPABASE_URL=https://ioxmmykvsvftysbjrusu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlveG1teWt2c3ZmdHlzYmpydXN1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzA3MTY4NCwiZXhwIjoyMDc4NjQ3Njg0fQ.z46T3oqEA2Q0WfDzXdQktr_9PUpq_7N3vaOrgcT3NKc

# 2. OpenRouter API（AI生成）
OPENROUTER_API_KEY=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

# 3. 邮箱配置（QQ邮箱）
EMAIL_USERNAME=441324066@qq.com
EMAIL_PASSWORD=xqtgmevcruqhbjid
EMAIL_FROM=441324066@qq.com
EMAIL_TO=hzy1257664828@gmail.com
```

---

## 🚀 配置步骤

### 1. 创建GitHub仓库

```bash
# 如果还没有创建仓库
cd /Users/he/Downloads/youtube-daily
git init
git add .
git commit -m "Initial commit: YouTube blockchain daily news automation"

# 在GitHub创建新仓库后
git remote add origin https://github.com/YOUR_USERNAME/youtube-daily.git
git branch -M main
git push -u origin main
```

### 2. 配置GitHub Secrets

1. 打开仓库页面
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 依次添加上述6个Secrets

**截图示例**：
```
Name: SUPABASE_URL
Secret: https://ioxmmykvsvftysbjrusu.supabase.co
```

### 3. 启用GitHub Actions

1. 点击仓库顶部的 **Actions** 标签
2. 如果看到提示，点击 **I understand my workflows, go ahead and enable them**
3. 查看工作流：**区块链每日观察 - 自动更新**

---

## ⏰ 运行时间配置

### 当前配置

```yaml
schedule:
  - cron: '0 21 * * *'  # 每天 UTC 21:00 = 北京时间早上5:00
```

### 修改运行时间

如果想改变运行时间，编辑 `.github/workflows/daily-update.yml`：

```yaml
# 北京时间 早上6点  = UTC 22:00 (前一天)
- cron: '0 22 * * *'

# 北京时间 早上7点  = UTC 23:00 (前一天)
- cron: '0 23 * * *'

# 北京时间 早上8点  = UTC 0:00 (当天)
- cron: '0 0 * * *'

# 北京时间 中午12点 = UTC 4:00
- cron: '0 4 * * *'
```

**Cron表达式格式**：
```
分钟(0-59) 小时(0-23) 日(1-31) 月(1-12) 星期(0-6)
```

---

## 🔧 手动运行

除了每日自动运行，你也可以手动触发：

1. 打开仓库的 **Actions** 标签
2. 点击左侧的 **区块链每日观察 - 自动更新**
3. 点击右上角的 **Run workflow** 按钮
4. 点击绿色的 **Run workflow** 确认

---

## 📊 运行结果查看

### 1. GitHub Actions日志

- 打开 **Actions** 标签
- 点击最近的运行记录
- 查看详细日志：
  ```
  检出代码
  设置 Python 环境
  安装系统依赖
  安装 Python 依赖
  运行每日新闻抓取与生成
  上传生成的文件为 Artifacts
  显示运行摘要
  ```

### 2. 下载生成文件

在运行完成后：
1. 滚动到页面底部的 **Artifacts** 部分
2. 点击 `daily-report-XXX` 下载
3. 解压查看生成的PDF和图片

### 3. 检查邮件

- 打开 `hzy1257664828@gmail.com`
- 查找标题：**区块链每日观察 - YYYY-MM-DD**
- 附件包含：
  - PDF报告（约3-4MB）
  - 图片压缩包（约5-8MB）

---

## 📧 邮件内容

每天早上5点，你会收到包含以下内容的邮件：

### 邮件主题
```
区块链每日观察 - 2025-11-23
```

### 邮件正文
```
📊 区块链每日观察
2025-11-23

今日报告已生成

[文章摘要]

统计数据:
- 新闻条数: 40
- 配图张数: 21 (1封面 + 20内容图)

📄 报告内容
• 封面页 - 报告标题和概述
• 目录 - 快速导航
• 深度分析 - 详细的行业观察和数据分析
• 信息图表 - AI生成的专业可视化图片
• 图片索引 - 所有配图汇总

📎 附件
• PDF 报告已作为附件发送
• 图片压缩包已作为附件发送
```

### 附件
1. **blockchain-daily-2025-11-23.pdf** (~3-4MB)
   - 21页纯图片PDF
   - 每页一张图片，全屏显示

2. **blockchain-images-2025-11-23.zip** (~5-8MB)
   - 包含所有21张原图
   - 文件名清晰标注内容
   ```
   00_COVER_吸引人的标题.png
   01_第一个板块.png
   02_第二个板块.png
   ...
   20_第二十个板块.png
   ```

---

## 🔍 故障排查

### 问题1: Actions运行失败

**症状**：GitHub Actions显示红色❌

**解决**：
1. 点击失败的运行记录
2. 查看具体错误日志
3. 常见原因：
   - Secrets配置错误
   - API限流（429错误）
   - 网络问题

**修复**：
```bash
# 检查Secrets是否正确配置
# Settings → Secrets → 逐个验证

# 如果是API限流，等待几小时后重试
```

### 问题2: 邮件未收到

**症状**：Actions显示成功✅，但没收到邮件

**解决**：
1. 检查垃圾邮件文件夹
2. 验证 `EMAIL_TO` Secret是否正确
3. 查看Actions日志中的邮件发送部分
4. QQ邮箱可能显示错误 `(-1, b'\x00\x00\x00')`，但邮件实际已发送

### 问题3: 图片生成失败

**症状**：PDF只有几张图或没有图片

**解决**：
1. 检查API额度：https://openrouter.ai/activity
2. 查看是否遇到429限流
3. 系统有fallback机制，应该至少有几张图片

### 问题4: PDF为空或损坏

**症状**：PDF文件很小或无法打开

**解决**：
1. 检查WeasyPrint依赖是否正确安装
2. 查看Actions日志中的PDF生成步骤
3. 下载Artifacts手动检查

---

## 💰 成本监控

### OpenRouter使用情况

访问：https://openrouter.ai/activity

**每日成本预估**：
```
新闻抓取: 免费
文章生成: 免费 (Gemini Flash)
标题生成: 免费 (Gemini Flash)
封面图: $0.00012
内容图(20张): $0.0024
总计: ~$0.00252 (约0.25分钱/天)

月度成本: ~$0.076 (约7.6分钱/月)
年度成本: ~$0.92 (约9毛钱/年)
```

### GitHub Actions配额

**Free Plan限额**：
- 每月2000分钟
- 当前workflow约5-10分钟/天
- 每月使用约150-300分钟
- **完全够用！**

---

## 📝 工作流文件说明

位置：`.github/workflows/daily-update.yml`

### 关键配置

```yaml
# 运行时间
schedule:
  - cron: '0 21 * * *'  # UTC 21:00 = 北京时间早上5:00

# 环境变量
env:
  OPENROUTER_MODEL: google/gemini-2.5-flash
  GEMINI_IMAGE_MODEL: google/gemini-3-pro-image-preview
  ENABLE_IMAGE_GENERATION: true
  ENABLE_PDF_GENERATION: true
  ENABLE_EMAIL_SEND: true

# Artifacts保留天数
retention-days: 30  # 保留30天
```

### 修改图片数量

如果想调整生成的图片数量，修改 `src/processors/image_generator.py`：

```python
# 当前：20张图片
sections = sections[:20]

# 改为15张
sections = sections[:15]

# 改为30张
sections = sections[:30]
```

---

## 🎯 使用场景

### 场景1: 每日YouTube视频制作

```
早上5:00  GitHub Actions自动运行
早上5:10  收到邮件（PDF + 图片ZIP）
早上6:00  下载图片ZIP，导入视频编辑软件
早上8:00  录制完成，使用封面图作为缩略图
早上9:00  上传到YouTube
```

### 场景2: 每日演讲/直播

```
早上5:00  自动生成今日内容
早上6:00  下载PDF到iPad/笔记本
早上8:00  线上/线下演讲，PDF翻页讲解
```

### 场景3: 社交媒体分享

```
早上5:00  自动生成
早上6:00  解压图片ZIP
早上7:00  选择精彩图片发布到微博/公众号/Twitter
早上8:00  配合深度文章发布长文
```

---

## ⚙️ 高级配置

### 1. 多个邮箱收件

修改GitHub Secrets中的 `EMAIL_TO`：

```
# 单个邮箱
EMAIL_TO=hzy1257664828@gmail.com

# 多个邮箱（逗号分隔）
EMAIL_TO=email1@example.com,email2@example.com
```

### 2. 修改文章长度

修改 `src/config.py`：

```python
# 当前：8000字
TARGET_ARTICLE_LENGTH = 8000

# 改为6000字（视频约30分钟）
TARGET_ARTICLE_LENGTH = 6000

# 改为10000字（视频约50分钟）
TARGET_ARTICLE_LENGTH = 10000
```

### 3. 调整新闻数量

修改 `src/config.py`：

```python
# 当前：40条
'limit': 40

# 改为30条
'limit': 30

# 改为60条
'limit': 60
```

---

## 📊 监控和日志

### GitHub Actions日志

查看每次运行的详细日志：
```
Actions → 选择运行记录 → 展开每个步骤
```

### 本地测试

在推送到GitHub前，可以本地测试：

```bash
# 设置环境变量
export SUPABASE_URL="..."
export SUPABASE_KEY="..."
export OPENROUTER_API_KEY="..."
# ... 其他环境变量

# 运行
source venv/bin/activate
python main.py
```

---

## ✅ 部署清单

完成以下步骤即可启用自动化：

- [ ] 1. 创建GitHub仓库
- [ ] 2. 推送代码到GitHub
- [ ] 3. 配置6个GitHub Secrets
- [ ] 4. 启用GitHub Actions
- [ ] 5. 测试手动运行
- [ ] 6. 等待第二天早上5点自动运行
- [ ] 7. 检查邮件接收
- [ ] 8. 下载Artifacts验证

---

## 🎉 总结

配置完成后，系统将：

✅ **每天早上5点自动运行**
✅ **抓取40条最新区块链新闻**
✅ **生成8000-10000字深度分析**
✅ **生成21张专业图片**（1封面 + 20内容）
✅ **创建纯图片PDF**（21页）
✅ **打包所有图片为ZIP**
✅ **发送邮件**（PDF + ZIP）
✅ **保存到Supabase数据库**
✅ **上传Artifacts到GitHub**（保留30天）

**成本**：~$0.076/月（约7.6分钱/月）
**时长**：约5-10分钟/次
**完全自动化，无需人工干预！**

---

**配置时间**: 2025-11-23
**状态**: ✅ 已配置完成
**下次运行**: 明天早上5:00
**文档**: GITHUB_ACTIONS_SETUP.md

祝你的YouTube区块链频道越做越好！🚀
