# 优化配置说明

## 📊 新配置概览

系统已优化为**仅使用金色财经**作为数据源，并生成**5k-10k字**的深度文章。

### 关键配置

#### 1. 数据源配置 (`src/config.py`)

```python
NEWS_SOURCES = {
    'jinse': {
        'enabled': True,
        'limit': 60,  # 抓取60条新闻（日更，24小时内）
    },
    # 其他数据源已禁用（RSSHub不稳定）
}

FETCH_HOURS = 24  # 抓取过去24小时的新闻（日更）
```

#### 2. 内容目标

```python
TARGET_ARTICLE_LENGTH = 8000  # 目标8000字符（约5k-10k字）
```

## 📰 数据量提升

### 之前
- 数据源: 1个（金色财经）
- 抓取量: 20条/24小时（无分页）
- 文章长度: 2k-3k字

### 现在
- 数据源: 1个（金色财经）
- 抓取量: **60条/24小时（支持分页）**
- 文章长度: **5k-10k字**

## 🤖 AI提示词优化

新的AI提示词要求:

### 1. 文章长度
- 目标: **8000-10000字**
- 开篇总结: 500-800字
- 深度分析: 1000-1500字

### 2. 内容深度
- **重要新闻**: 150-300字/条
  - 事件背景
  - 详细数据
  - 业内观点
  - 影响分析

- **次要新闻**: 80-150字/条

### 3. 文章结构

```markdown
# 区块链每日观察 - YYYY-MM-DD

## 开篇总结 (500-800字)
- 核心主题提炼
- 重要趋势分析
- 阅读导航

## 📊 市场动态
### [重要事件标题]
详细展开...

- 次要事件1
- 次要事件2

## 🏛️ 政策监管
...

## 💰 DeFi生态
...

## 🔧 技术创新
...

## 💼 投融资
...

## 🌐 行业动态
...

## 深度分析 (1000-1500字)
- 今日新闻关联性
- 行业趋势影响
- 机会与风险
```

## 📈 预期效果

### 新闻覆盖
- **24小时内**: 50-70条新闻（支持API分页）
- **去重后**: 45-65条高质量新闻
- **最终文章**: 包含30-50条新闻的深度分析

### 文章质量
- ✅ 信息量大 (5k-10k字)
- ✅ 分析深入 (背景+影响+预测)
- ✅ 结构清晰 (分类+层次)
- ✅ 专业可读 (数据+观点)

## 🔧 调优参数

### 如果文章太短 (<5k字)

**方法1**: 增加新闻量
```python
# src/config.py
NEWS_SOURCES['jinse']['limit'] = 150  # 增加到150条
FETCH_HOURS = 72  # 扩展到72小时
```

**方法2**: 强化AI提示
```python
# src/processors/ai_processor.py
# 在prompt中增加:
"每条重要新闻必须包含至少300字的详细分析"
```

### 如果文章太长 (>12k字)

**方法1**: 减少新闻量
```python
NEWS_SOURCES['jinse']['limit'] = 80
FETCH_HOURS = 36
```

**方法2**: 调整内容深度
```python
"重要新闻: 100-200字/条"
"次要新闻: 50-80字/条"
```

### 如果想要更多样化的内容

可以尝试启用其他数据源（需要先解决RSSHub问题）:

```python
# 方案A: 自建RSSHub
docker run -d -p 1200:1200 diygod/rsshub

# 方案B: 使用其他RSS服务
NEWS_SOURCES['odaily']['api_url'] = 'https://your-rsshub.com/odaily/newsflash'
```

## 💰 成本影响

### 之前
- Token输入: ~2k tokens
- Token输出: ~1.5k tokens
- 成本: ~$0.001/天 (Gemini 2.0 Flash)

### 现在
- Token输入: ~8k-10k tokens (更多新闻)
- Token输出: ~8k-10k tokens (长文章)
- 成本: **~$0.003-0.005/天** (仍然很便宜!)

### 年成本估算
- Gemini 2.0 Flash Exp (免费): **$0/年** ✅
- Gemini 2.0 Flash: **~$1.5/年**
- Claude 3.5 Sonnet: **~$15/年**

## 📊 测试结果

### 测试命令
```bash
# 测试爬虫（应该获取更多新闻）
python scripts/test_scrapers.py

# 测试完整流程
python main.py
```

### 预期输出
```
[Step 1/4] Fetching news...
  金色财经: 80-100 items

[Step 2/4] Processing...
  After processing: 60-80 items

[Step 3/4] AI processing...
  Generated article: 区块链每日观察 - 2025-11-23
  Content length: 8000-10000 characters ✅
```

## ⚙️ 配置文件位置

- **数据源配置**: `src/config.py`
- **AI提示词**: `src/processors/ai_processor.py` (line 103)
- **环境变量**: `.env`

## 🎯 最佳实践

1. **监控文章长度**: 检查 `output/` 目录中生成的文章
2. **调整参数**: 根据实际效果微调 `limit` 和 `FETCH_HOURS`
3. **控制成本**: 使用 Gemini 2.0 Flash Exp (免费版)
4. **定期检查**: 确保金色财经API稳定

## 🔍 故障排查

### 问题: 文章仍然很短

**检查点**:
1. ✅ `NEWS_SOURCES['jinse']['limit']` = 100
2. ✅ `FETCH_HOURS` = 48
3. ✅ `max_tokens` = 16000
4. ✅ 提示词要求 8000-10000字

**调试命令**:
```bash
# 查看抓取的新闻数量
python -c "
from src.scrapers import JinSeScraper
scraper = JinSeScraper()
news = scraper.fetch_news(hours=48)
print(f'Fetched: {len(news)} items')
"
```

### 问题: API超时

金色财经API比较稳定，如果超时:
- 检查网络连接
- 减少 `limit` 到 50-80
- 增加请求 timeout

---

**配置已优化完成！** 现在系统将生成更长、更深入的每日文章 🚀
