#!/usr/bin/env python3
"""
TikTok智能营销测试 - 关键词搜索 + AI分析
不发送DM，仅测试搜索和AI识别功能
"""

import sys
sys.path.append('src')

import json
from playwright.sync_api import sync_playwright
from smart_user_finder import SmartUserFinder
import time

print("=" * 70)
print("🎵 TikTok Smart Campaign Test")
print("=" * 70)

PRODUCT_DESCRIPTION = """
HireMeAI (https://interviewasssistant.com) - AI-powered interview preparation platform.
Helps job seekers with mock interviews and real-time feedback.
"""

TEST_KEYWORD = "job interview tips"

print(f"\n🔍 Test Keyword: '{TEST_KEYWORD}'")
print("\n📊 This test will:")
print("   1. Search TikTok for videos matching the keyword")
print("   2. Scrape comments from top videos")
print("   3. Use AI to identify qualified users")
print("   4. Show results (NO DMs will be sent)")
print()

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
    sessionid = auth['tiktok']['sessionid']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context()
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.tiktok.com',
        'path': '/'
    }])

    page = context.new_page()

    # 步骤1: 搜索视频
    print("\n" + "=" * 70)
    print("Step 1: Searching TikTok videos...")
    print("=" * 70)

    search_url = f'https://www.tiktok.com/search?q={TEST_KEYWORD.replace(" ", "%20")}'
    page.goto(search_url, timeout=30000)
    time.sleep(3)

    # 收集视频链接
    video_links = page.query_selector_all('a[href*="/video/"]')
    videos = []
    for link in video_links[:3]:
        href = link.get_attribute('href')
        if href and '/video/' in href:
            if not href.startswith('http'):
                href = f'https://www.tiktok.com{href}'
            videos.append(href)

    print(f"✅ Found {len(videos)} videos")
    for i, url in enumerate(videos, 1):
        print(f"   {i}. {url}")

    # 步骤2: 抓取评论
    print("\n" + "=" * 70)
    print("Step 2: Scraping comments from first video...")
    print("=" * 70)

    if videos:
        page.goto(videos[0], timeout=30000)
        time.sleep(3)

        # 滚动加载评论
        for i in range(3):
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(1)

        # 抓取评论
        comments = []
        comment_elements = page.query_selector_all('div[data-e2e="comment-item"]')

        for elem in comment_elements[:30]:
            try:
                username_elem = elem.query_selector('a[href*="/@"]')
                username = username_elem.inner_text() if username_elem else "unknown"

                text_elem = elem.query_selector('span[data-e2e="comment-text"], p')
                text = text_elem.inner_text() if text_elem else ""

                if username and text and len(text) > 10:
                    comments.append({
                        'username': username.lstrip('@'),
                        'text': text,
                        'platform': 'tiktok'
                    })
            except:
                continue

        # 去重
        seen = set()
        unique_comments = []
        for c in comments:
            key = f"{c['username']}:{c['text'][:30]}"
            if key not in seen:
                seen.add(key)
                unique_comments.append(c)

        print(f"✅ Scraped {len(unique_comments)} unique comments")

        # 显示前5条
        print("\nSample comments:")
        for i, c in enumerate(unique_comments[:5], 1):
            print(f"   {i}. @{c['username']}: {c['text'][:80]}...")

        # 步骤3: AI分析
        print("\n" + "=" * 70)
        print("Step 3: AI Analysis of comments...")
        print("=" * 70)

        finder = SmartUserFinder()

        print(f"🧠 Analyzing {len(unique_comments)} comments with GPT-4o-mini...")
        print("   (Batch processing - one API call)")

        qualified_users = finder.analyze_comments_for_intent(
            comments=unique_comments,
            product_description=PRODUCT_DESCRIPTION
        )

        # 过滤高分用户
        high_score_users = [
            u for u in qualified_users
            if u.get('intent_score', 0) >= 0.6
        ]

        print(f"\n✅ AI identified {len(high_score_users)} qualified users (score >= 0.6)")

        # 显示结果
        if high_score_users:
            print("\n" + "=" * 70)
            print("📊 Qualified Users:")
            print("=" * 70)

            for i, user in enumerate(high_score_users, 1):
                print(f"\n{i}. @{user['username']}")
                print(f"   Intent Score: {user.get('intent_score', 0):.2f}")
                print(f"   Priority: {user.get('priority', 'N/A')}")
                print(f"   Reasons:")
                for reason in user.get('reasons', []):
                    print(f"      - {reason}")
                if user.get('pain_points'):
                    print(f"   Pain Points: {', '.join(user['pain_points'])}")

            print("\n" + "=" * 70)
            print("✅ Test completed successfully!")
            print("=" * 70)
            print(f"\n💰 Estimated cost for this test: ~$0.001")
            print(f"📊 Found {len(high_score_users)} qualified users")
            print("\n💡 These users would be contacted in a real campaign")
            print("   (NO DMs were sent in this test)")
        else:
            print("\n⚠️  No qualified users found with score >= 0.6")
            print("   Try different keywords or lower the threshold")

    else:
        print("❌ No videos found")

    browser.close()

print("\n✅ Test completed!")
