# PDF 报告和邮件发送功能

## 📋 功能概述

系统现在支持以下高级功能：

1. **AI 图片生成** - 使用 Nano Banana Pro (Gemini 3 Pro Image Preview) 为文章生成专业信息图表
2. **PDF 报告生成** - 将文章和图片整合成精美的 PDF 报告
3. **邮件自动发送** - 将 PDF 报告自动发送到指定邮箱

## 🎯 使用场景

- **每日讲解** - 收到带配图的 PDF 报告，方便直接打开讲解
- **团队分享** - 自动发送专业报告给团队成员
- **客户服务** - 为客户提供定制化的行业报告
- **存档备份** - PDF 格式便于长期存档和打印

## 🚀 快速开始

### 1. 配置环境变量

编辑 `.env` 文件，添加以下配置：

```bash
# 功能开关（全部设为 true 启用完整功能）
ENABLE_IMAGE_GENERATION=true
ENABLE_PDF_GENERATION=true
ENABLE_EMAIL_SEND=true

# Gemini 图片生成模型
GEMINI_IMAGE_MODEL=google/gemini-3-pro-image-preview

# 邮件配置
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

### 2. Gmail 配置（推荐）

如果使用 Gmail 发送邮件：

1. **启用两步验证**：
   - 访问 [Google Account Security](https://myaccount.google.com/security)
   - 启用"两步验证"

2. **生成应用专用密码**：
   - 访问 [App Passwords](https://myaccount.google.com/apppasswords)
   - 选择"邮件"和"其他（自定义名称）"
   - 输入"Blockchain Daily Bot"
   - 复制生成的 16 位密码到 `EMAIL_PASSWORD`

3. **配置 SMTP**：
   ```bash
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=abcd efgh ijkl mnop  # 16位应用专用密码
   ```

### 3. 其他邮箱服务配置

#### Outlook / Hotmail
```bash
EMAIL_SMTP_SERVER=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587
```

#### Yahoo Mail
```bash
EMAIL_SMTP_SERVER=smtp.mail.yahoo.com
EMAIL_SMTP_PORT=587
```

#### QQ Mail
```bash
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=587
# 需要在QQ邮箱设置中开启SMTP服务并获取授权码
```

#### 163 Mail
```bash
EMAIL_SMTP_SERVER=smtp.163.com
EMAIL_SMTP_PORT=465
```

### 4. 测试邮件发送

```bash
# 进入 Python 环境
python

# 测试邮件配置
from src.utils.email_sender import EmailSender
sender = EmailSender()
sender.send_test_email("测试邮件配置成功！")
```

## 📊 工作流程

完整的系统流程变为 7 步：

```
Step 1: 抓取新闻
  ↓
Step 2: 内容过滤
  ↓
Step 3: AI 生成文章 (5k-10k字)
  ↓
Step 4: 保存到 Supabase
  ↓
Step 5: AI 生成信息图表 (Nano Banana Pro)
  ↓
Step 6: 生成 PDF 报告 (文章 + 图片)
  ↓
Step 7: 发送邮件 (PDF 附件)
```

## 🎨 图片生成特性

### Nano Banana Pro 优势

- ✅ **高质量文字渲染** - 支持中文标题和数据标签
- ✅ **专业信息图表** - 数据可视化、趋势图、图表
- ✅ **2K/4K 输出** - 高分辨率，适合打印
- ✅ **实时信息整合** - 基于 Gemini 3 Pro 的搜索能力
- ✅ **多元素组合** - 图标、数据、文字完美融合

### 生成的图片类型

每个文章板块会生成对应的信息图表：

1. **市场动态** - 价格走势图、交易量对比
2. **政策监管** - 监管时间线、影响分析
3. **DeFi 生态** - TVL 变化、协议对比
4. **技术创新** - 技术架构图、流程图
5. **投融资** - 融资数据、估值对比
6. **行业动态** - 生态发展图、合作关系

### 图片存储

```
output/
  └── images/
      └── 2025-11-23/
          ├── 01_市场动态.png
          ├── 02_政策监管.png
          ├── 03_DeFi生态.png
          └── ...
```

## 📄 PDF 报告特性

### 报告结构

1. **封面页**
   - 渐变背景设计
   - 文章标题和日期
   - 简短描述和标签

2. **目录页**
   - 自动生成章节列表
   - 清晰的导航结构

3. **正文内容**
   - Markdown 格式化
   - 图片嵌入到相应章节
   - 专业排版和配色

4. **图片索引**
   - 所有图片的汇总展示
   - 网格布局，便于快速浏览

### PDF 样式

- **字体**: 支持中文（SimSun, STSong）
- **配色**: 专业蓝紫渐变 (#667eea ~ #764ba2)
- **布局**: A4 纸张，2cm 边距
- **分页**: 智能分页，避免章节断裂
- **页码**: 自动添加在页脚

### PDF 存储

```
output/
  └── blockchain-daily-2025-11-23.pdf
```

## 📧 邮件内容

### 邮件模板

HTML 格式，包含：
- 精美的报告封面设计
- 统计数据展示（新闻条数、图片张数）
- 报告内容预览
- PDF 附件说明

### 邮件主题

```
区块链每日观察 - 2025-11-23
```

### 附件信息

- **文件名**: `blockchain-daily-2025-11-23.pdf`
- **大小**: 通常 2-5 MB（取决于图片数量）
- **格式**: PDF (可直接打开、打印、分享)

## ⚙️ 功能开关

可以单独控制每个功能：

```bash
# 只生成文章，不生成图片和PDF
ENABLE_AI_SUMMARY=true
ENABLE_IMAGE_GENERATION=false
ENABLE_PDF_GENERATION=false
ENABLE_EMAIL_SEND=false

# 生成文章和PDF，但不发送邮件
ENABLE_AI_SUMMARY=true
ENABLE_IMAGE_GENERATION=true
ENABLE_PDF_GENERATION=true
ENABLE_EMAIL_SEND=false

# 完整功能（推荐）
ENABLE_AI_SUMMARY=true
ENABLE_IMAGE_GENERATION=true
ENABLE_PDF_GENERATION=true
ENABLE_EMAIL_SEND=true
```

## 💰 成本估算

### OpenRouter API 调用

1. **文章生成**: Gemini 2.0 Flash Exp (免费) - $0
2. **图片提示词生成**: Gemini 2.0 Flash Exp (免费) - $0
3. **图片生成** (约 5-6 张):
   - Gemini 3 Pro Image Preview: 具体价格请查看 [OpenRouter Pricing](https://openrouter.ai/models/google/gemini-3-pro-image-preview)
   - 预估: ~$0.05-0.15/天

### 总成本

- **不含图片生成**: **$0/天** (完全免费)
- **包含图片生成**: **~$0.05-0.15/天** (~$1.5-4.5/月)

仍然非常经济！

## 🔍 故障排查

### 1. 图片生成失败

**问题**: `Error in single image generation`

**可能原因**:
- OpenRouter API key 无效
- Gemini 3 Pro Image Preview 配额不足
- API 响应格式不符合预期

**解决方法**:
```bash
# 检查 API key
echo $OPENROUTER_API_KEY

# 查看 OpenRouter 使用情况
# 访问: https://openrouter.ai/activity

# 临时禁用图片生成
ENABLE_IMAGE_GENERATION=false
```

### 2. PDF 生成失败

**问题**: `PDF generation failed: No module named 'weasyprint'`

**解决方法**:
```bash
pip install markdown weasyprint pillow
```

**问题**: `PDF 中文显示为方块`

**解决方法**:
- WeasyPrint 会自动查找系统字体
- macOS/Linux: 确保安装了中文字体
- Windows: 通常自带中文字体

### 3. 邮件发送失败

**问题**: `SMTPAuthenticationError: Username and Password not accepted`

**解决方法**:
- 检查 EMAIL_USERNAME 和 EMAIL_PASSWORD 是否正确
- Gmail 用户：确保使用的是"应用专用密码"，不是账户密码
- 检查是否启用了两步验证

**问题**: `SMTPServerDisconnected: Connection unexpectedly closed`

**解决方法**:
```bash
# 检查 SMTP 服务器和端口
# Gmail: smtp.gmail.com:587
# 确保端口 587 未被防火墙阻止
```

**问题**: `Email sending failed: timed out`

**解决方法**:
- 检查网络连接
- 尝试使用其他 SMTP 端口（如 465）
- 暂时禁用邮件发送功能继续测试其他部分

### 4. 图片未插入PDF

**检查**:
- 图片文件是否存在于 `output/images/` 目录
- 检查日志中的图片路径
- 确认图片生成步骤成功完成

## 📝 使用示例

### 完整流程示例

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入所有必需的配置

# 2. 测试邮件配置
python -c "from src.utils.email_sender import EmailSender; EmailSender().send_test_email()"

# 3. 运行完整流程
python main.py

# 4. 检查输出
ls -lh output/
ls -lh output/images/$(date +%Y-%m-%d)/

# 5. 查看 PDF
open output/blockchain-daily-$(date +%Y-%m-%d).pdf
```

### 预期输出

```
[Step 1/4] Fetching news from sources...
  金色财经: 60 items

[Step 2/4] Processing and filtering news...
  After processing: 60 news items

[Step 3/4] Generating article with AI...
  Generated article: 区块链每日观察 - 2025-11-23
  Content length: 15000+ characters

[Step 4/4] Saving to Supabase database...
  ✓ Successfully saved

[Step 5/7] Generating images with AI...
  Generating image 1/5: 市场动态
  ✓ Generated 5 images

[Step 6/7] Generating PDF report...
  ✓ PDF generated: output/blockchain-daily-2025-11-23.pdf

[Step 7/7] Sending email with PDF attachment...
  ✓ Email sent successfully

================================================================================
Blockchain Daily News Bot - Completed Successfully!
  News items: 60
  Images generated: 5
  PDF report: output/blockchain-daily-2025-11-23.pdf
================================================================================
```

## 🔐 安全建议

1. **保护邮箱密码**:
   - 使用应用专用密码，不要使用真实账户密码
   - 不要将 `.env` 文件提交到 Git

2. **限制邮件接收者**:
   - 仅发送给授权的邮箱地址
   - 避免将敏感信息包含在邮件中

3. **API Key 安全**:
   - 定期轮换 OpenRouter API Key
   - 监控 API 使用情况，避免滥用

## 🆘 获取帮助

如果遇到问题：

1. 查看详细日志：`logs/blockchain_daily_YYYYMMDD.log`
2. 检查 OpenRouter 使用情况：[Dashboard](https://openrouter.ai/activity)
3. 测试单个功能组件（见上文测试邮件示例）
4. 提交 Issue 到 GitHub 仓库

---

**功能已完成！享受自动化的专业报告生成！** 📊✉️
