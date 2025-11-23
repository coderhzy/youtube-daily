# 🚀 快速开始 - 手动触发测试

## 📋 当前状态

✅ 代码已推送到GitHub
✅ Workflow已配置为**仅手动触发**
⏸️ 定时任务已暂时禁用（测试完成后再启用）

---

## 🎯 立即手动触发

### 步骤1: 打开GitHub仓库
访问: https://github.com/coderhzy/youtube-daily

### 步骤2: 进入Actions
点击顶部的 **Actions** 标签

### 步骤3: 选择工作流
点击左侧的 **区块链每日观察 - 自动更新**

### 步骤4: 手动运行
1. 点击右上角的 **Run workflow** 按钮
2. 确认分支为 `master`
3. 点击绿色的 **Run workflow** 按钮

### 步骤5: 查看运行进度
- 等待几秒后刷新页面
- 看到黄色圆圈🟡表示正在运行
- 点击进入查看详细日志
- 绿色✅表示成功，红色❌表示失败

---

## ⏱️ 预计运行时间

```
抓取新闻:     ~5秒
生成文章:     ~15秒
生成封面图:   ~20秒 (使用Nano Banana Pro，仅1张)
生成PDF:      ~5秒
创建ZIP:      ~2秒
发送邮件:     ~10秒

总计: 约1分钟
```

---

## 📧 检查邮件

运行完成后（约1分钟）：

1. 打开 `hzy1257664828@gmail.com`
2. 查找主题: **区块链每日观察 - 2025-11-23**
3. 附件包含：
   - `blockchain-daily-2025-11-23.pdf` (~200-500KB, 1张封面图)
   - `blockchain-images-2025-11-23.zip` (~300-600KB, 1张封面图)

---

## 🔍 查看生成的文件

在GitHub Actions中：

1. 运行完成后，滚动到页面底部
2. 找到 **Artifacts** 部分
3. 点击 `daily-report-XXX` 下载
4. 解压查看：
   ```
   output/
   ├── blockchain-daily-2025-11-23.md
   ├── blockchain-daily-2025-11-23.pdf
   ├── blockchain-images-2025-11-23.zip
   └── images/
       └── 2025-11-23/
           └── 00_COVER_xxx.png (仅1张封面图，Nano Banana Pro生成)
   ```

---

## ✅ 测试完成后启用定时任务

如果测试成功，编辑 `.github/workflows/daily-update.yml`：

```yaml
on:
  schedule:
    # 每天东八区(北京时间)早上5点运行
    - cron: '0 21 * * *'  # UTC 21:00 = 北京时间次日 05:00
  workflow_dispatch:  # 保留手动触发
```

**注意**:
- GitHub使用UTC时间
- 北京时间(东八区) = UTC+8
- 北京时间早上5:00 = UTC前一天21:00
- 所以cron表达式为: `0 21 * * *`

### 修改后提交

```bash
git add .github/workflows/daily-update.yml
git commit -m "feat: 启用每日定时任务 - 北京时间早上5点"
git push origin master
```

---

## 🛠️ 故障排查

### 问题1: Secrets未配置

**症状**: 运行失败，日志显示环境变量为空

**解决**:
1. 进入仓库 Settings → Secrets and variables → Actions
2. 添加所需的6个Secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENROUTER_API_KEY`
   - `EMAIL_USERNAME`
   - `EMAIL_PASSWORD`
   - `EMAIL_FROM`
   - `EMAIL_TO`

### 问题2: 图片生成失败

**症状**: 日志显示429错误或图片数量少于20张

**解决**:
- 429错误是API限流，等待几分钟后重试
- 系统有fallback机制，会生成基础版本的图片

### 问题3: 邮件未收到

**症状**: Actions显示成功但没收到邮件

**解决**:
1. 检查垃圾邮件箱
2. 验证 `EMAIL_TO` Secret是否正确
3. 查看Actions日志中的邮件发送部分
4. QQ邮箱可能显示错误，但邮件实际已发送

---

## 📊 查看运行日志

在Actions运行详情页面：

```
✓ 检出代码
✓ 设置 Python 环境
✓ 安装系统依赖
✓ 安装 Python 依赖
✓ 运行每日新闻抓取与生成  ← 点击查看详细日志
  ├─ [Step 1/7] 抓取新闻...
  ├─ [Step 2/7] 过滤处理...
  ├─ [Step 3/7] AI生成文章...
  ├─ [Step 4/7] 保存数据库...
  ├─ [Step 5/7] 生成图片...
  ├─ [Step 6/7] 生成PDF...
  └─ [Step 7/7] 发送邮件...
✓ 上传生成的文件为 Artifacts
✓ 显示运行摘要
```

---

## 💰 成本监控

每次运行后，检查OpenRouter使用情况：
https://openrouter.ai/activity

**预期成本**: ~$0.0025/次 (约0.25分钱)

---

## 🎉 成功标志

运行成功后，你应该看到：

✅ GitHub Actions显示绿色✅
✅ 收到邮件，包含PDF和ZIP
✅ Artifacts包含完整文件
✅ 日志显示生成了1张封面图
✅ PDF大小约200-500KB
✅ ZIP大小约300-600KB
✅ 文章描述干净简洁，无AI回复性文字

---

## 📝 下一步

测试成功后：

1. ✅ 解压ZIP查看封面图质量（高质量YouTube缩略图）
2. ✅ 打开PDF确认封面图显示正常（无底部空白）
3. ✅ 使用封面图作为YouTube视频缩略图
4. ✅ 如果满意，启用定时任务
5. ✅ 每天早上5点自动收到新报告

**图片生成策略**：
- 仅生成1张封面图：使用 Nano Banana Pro（高质量，适合YouTube缩略图）
- 不生成内容图：节省成本和时间
- 文章描述自动过滤AI回复性文字（"好的"、"这是"等）

---

**创建时间**: 2025-11-23
**当前状态**: 🟡 等待手动触发测试
**仓库地址**: https://github.com/coderhzy/youtube-daily
**运行方式**: 手动触发 (Actions → Run workflow)
