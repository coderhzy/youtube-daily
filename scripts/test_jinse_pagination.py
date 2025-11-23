#!/usr/bin/env python3
"""测试金色财经API分页机制"""

import requests
import json

url = "https://api.jinse.cn/noah/v2/lives"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.jinse.cn/"
}

print("="*80)
print("测试金色财经API分页机制")
print("="*80)

all_lives = []
current_id = 0
page = 1
max_pages = 5  # 测试5页

while page <= max_pages:
    print(f"\n--- Page {page} (id={current_id}) ---")

    params = {
        'limit': 20,
        'reading': 'false',
        'source': 'web',
        'flag': 'down',
        'id': current_id,
        'category': 0
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        items = data.get('list', [])
        print(f"List items: {len(items)}")

        page_lives = []
        for item in items:
            lives = item.get('lives', [])
            page_lives.extend(lives)

        print(f"Lives in this page: {len(page_lives)}")

        if not page_lives:
            print("没有更多数据，停止分页")
            break

        # 显示第一条和最后一条的ID
        if page_lives:
            first_id = page_lives[0].get('id')
            last_id = page_lives[-1].get('id')
            print(f"First live ID: {first_id}")
            print(f"Last live ID: {last_id}")

            # 显示第一条标题
            first_title = page_lives[0].get('content_prefix', '')[:50]
            print(f"First title: {first_title}")

            # 更新current_id为最后一条的ID，用于下一页
            current_id = last_id

        all_lives.extend(page_lives)
        page += 1

    except Exception as e:
        print(f"Error: {e}")
        break

print(f"\n{'='*80}")
print(f"总计抓取: {len(all_lives)} 条新闻")
print("="*80)

# 显示去重后的数量
unique_ids = set(live.get('id') for live in all_lives)
print(f"去重后: {len(unique_ids)} 条唯一新闻")

# 显示时间范围
if all_lives:
    from datetime import datetime

    timestamps = [live.get('created_at', 0) for live in all_lives]
    earliest = min(timestamps)
    latest = max(timestamps)

    earliest_dt = datetime.fromtimestamp(earliest)
    latest_dt = datetime.fromtimestamp(latest)

    print(f"时间范围: {earliest_dt} 到 {latest_dt}")

    time_diff = (latest - earliest) / 3600
    print(f"覆盖时长: {time_diff:.1f} 小时")
