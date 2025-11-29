#!/usr/bin/env python3
"""快速诊断Instagram访问问题"""

import json
import sys
sys.path.append('src')

from playwright.sync_api import sync_playwright

print("🔍 Diagnosing Instagram access...")

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
sessionid = auth['instagram']['sessionid']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/'
    }])

    page = context.new_page()

    # 测试访问一个hashtag页面
    url = 'https://www.instagram.com/explore/tags/jobsearch/'
    print(f"\n访问: {url}")

    page.goto(url, timeout=30000)

    import time
    time.sleep(5)

    # 收集帖子链接
    links = page.query_selector_all('a[href*="/p/"]')
    print(f"\n找到 {len(links)} 个帖子链接")

    if links:
        # 尝试访问第一个帖子
        first_link = links[0].get_attribute('href')
        if not first_link.startswith('http'):
            first_link = f'https://www.instagram.com{first_link}'

        print(f"\n尝试访问帖子: {first_link}")

        try:
            page.goto(first_link, timeout=30000)
            time.sleep(3)
            print("✅ 帖子加载成功！")

            # 查找评论
            comments = page.query_selector_all('span')
            print(f"找到 {len(comments)} 个span元素")

        except Exception as e:
            print(f"❌ 帖子访问失败: {e}")

    print("\n按Enter关闭...")
    input()
    browser.close()
