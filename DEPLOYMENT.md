# 🚀 快速部署清单

按照以下步骤部署到 GitHub Actions，实现每日自动化。

## ✅ 部署前检查

- [ ] 本地测试成功（`python main.py` 运行正常）
- [ ] Supabase 数据库已配置
- [ ] 拥有所有必需的 API Keys

## 📝 部署步骤（5分钟）

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 上创建新仓库（建议 Private）
# 不要初始化任何文件
```

### 2. 推送代码

```bash
# 添加远程仓库（替换 YOUR_USERNAME 和仓库名）
git remote add origin https://github.com/YOUR_USERNAME/blockchain-daily-observer.git

# 推送代码
git push -u origin master
```

### 3. 配置 GitHub Secrets ⭐ **最重要**

进入仓库 **Settings** > **Secrets and variables** > **Actions**，添加：

| Secret 名称 | 如何获取 |
|------------|---------|
| `SUPABASE_URL` | Supabase > Settings > API > URL |
| `SUPABASE_KEY` | Supabase > Settings > API > **service_role** key |
| `OPENROUTER_API_KEY` | OpenRouter > Keys > 创建新 Key |

### 4. 测试运行

```bash
# 在 GitHub 仓库页面
Actions 标签 > Blockchain Daily News Bot > Run workflow
```

### 5. 验证结果

- [ ] Workflow 运行成功（绿色 ✓）
- [ ] Supabase 中有新数据
- [ ] 日志已上传

## ⏰ 自动运行时间

**每天北京时间早上 5:00** 自动运行

## 📚 详细文档

遇到问题？查看完整指南：[GitHub Actions 部署指南](docs/GITHUB_ACTIONS_SETUP.md)

## 🆘 常见问题

**Q: Workflow 失败怎么办？**
A: 查看 Actions 日志，检查 Secrets 配置是否正确

**Q: 如何修改运行时间？**
A: 编辑 `.github/workflows/daily-news.yml` 中的 cron 表达式

**Q: 如何手动触发？**
A: Actions > Blockchain Daily News Bot > Run workflow

---

**部署完成后，系统将完全自动化！** 🎉
