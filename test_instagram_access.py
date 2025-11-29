#!/usr/bin/env python3
"""
测试Instagram访问是否正常
"""

import json
import time
from playwright.sync_api import sync_playwright

print("=" * 70)
print("🧪 Testing Instagram Access")
print("=" * 70)

# 加载sessionid
try:
    with open('platforms_auth.json', 'r') as f:
        auth = json.load(f)
    sessionid = auth['instagram']['sessionid']
    print(f"✅ SessionID loaded (length: {len(sessionid)})")
except:
    print("❌ Failed to load sessionid")
    exit(1)

# 测试访问
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
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

    # 测试1: 访问首页
    print("\n📝 Test 1: Instagram homepage...")
    try:
        page.goto('https://www.instagram.com/', timeout=30000)
        time.sleep(5)
        title = page.title()
        print(f"   Page title: {title}")

        # 检查是否登录
        try:
            profile_btn = page.query_selector('a[href*="/accounts/"]')
            if profile_btn:
                print("   ✅ Logged in successfully")
            else:
                print("   ⚠️  May not be logged in")
        except:
            print("   ⚠️  Cannot check login status")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 测试2: 搜索hashtag
    print("\n📝 Test 2: Hashtag page...")
    try:
        hashtag = 'jobsearch'
        url = f'https://www.instagram.com/explore/tags/{hashtag}/'
        print(f"   URL: {url}")

        page.goto(url, timeout=30000)
        time.sleep(5)

        # 检查是否有帖子
        post_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
        print(f"   ✅ Found {len(post_links)} post links")

        if post_links:
            # 测试访问第一个帖子
            first_post = post_links[0].get_attribute('href')
            if not first_post.startswith('http'):
                first_post = f'https://www.instagram.com{first_post}'

            print(f"\n📝 Test 3: Accessing post...")
            print(f"   URL: {first_post}")

            try:
                page.goto(first_post, timeout=30000)
                time.sleep(5)
                title = page.title()
                print(f"   Page title: {title}")

                # 检查评论
                comment_elements = page.query_selector_all('span')
                print(f"   ✅ Page loaded, found {len(comment_elements)} span elements")

            except Exception as e:
                print(f"   ❌ Failed to access post: {e}")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print("\n" + "=" * 70)
    print("Press Enter to close browser...")
    input()

    browser.close()
