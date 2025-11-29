#!/usr/bin/env python3
"""
Instagram智能营销 - 完整流程
1. 搜索关键词 → 找到帖子
2. 抓取评论 → AI识别潜在客户
3. 批量发DM
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright
from smart_user_finder import SmartUserFinder
from instagram_dm_sender import InstagramDMSender

print("=" * 70)
print("🤖 Instagram Smart Campaign Test")
print("=" * 70)

# 产品描述
PRODUCT_DESCRIPTION = """
HireMeAI (https://interviewasssistant.com) - AI-powered interview preparation platform.
Helps job seekers prepare for interviews with AI-generated mock interviews and real-time feedback.
"""

# 测试关键词
TEST_KEYWORD = "job interview tips"

print(f"\n📝 Configuration:")
print(f"   Product: HireMeAI")
print(f"   Keyword: {TEST_KEYWORD}")
print(f"   AI Analysis: ✅ Enabled")
print()

# 初始化
finder = SmartUserFinder()
qualified_users = []

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        # 加载Instagram cookies
        with open('platforms_auth.json', 'r') as f:
            auth = json.load(f)
            sessionid = auth['instagram']['sessionid']

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

        # 步骤1: 搜索关键词
        print(f"🔍 Step 1: Searching Instagram for '{TEST_KEYWORD}'...")

        page.goto('https://www.instagram.com/', timeout=60000)
        time.sleep(3)

        # 点击搜索
        search_icon = page.wait_for_selector('svg[aria-label="搜索"], svg[aria-label="Search"]', timeout=10000)
        search_icon.click()
        time.sleep(2)

        # 输入关键词
        search_input = page.wait_for_selector('input[placeholder*="Search"], input[type="text"]', timeout=5000)
        search_input.fill(TEST_KEYWORD)
        time.sleep(3)

        # 步骤2: 找到帖子 (不是用户！)
        print("\n📸 Step 2: Finding posts (not users)...")

        # Instagram搜索结果有多个标签: Top, Accounts, Tags, Places
        # 我们需要点击 "Tags" 或直接搜索 hashtag
        post_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')

        if not post_links:
            print("   ⚠️  No posts found in search results")
            print("   Trying hashtag search instead...")

            # 尝试hashtag搜索
            hashtag_keyword = TEST_KEYWORD.replace(' ', '')
            page.goto(f'https://www.instagram.com/explore/tags/{hashtag_keyword}/', timeout=60000)
            time.sleep(3)

            post_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')

        print(f"   ✅ Found {len(post_links)} posts")

        # 步骤3: 点击第一个帖子，抓取评论
        if post_links and len(post_links) > 0:
            print("\n💬 Step 3: Scraping comments from first post...")

            first_post = post_links[0]
            post_url = first_post.get_attribute('href')
            if not post_url.startswith('http'):
                post_url = f'https://www.instagram.com{post_url}'

            print(f"   Post URL: {post_url}")

            # 使用SmartUserFinder抓取评论并分析
            qualified_users = finder.find_qualified_users_from_post(
                page=page,
                post_url=post_url,
                product_description=PRODUCT_DESCRIPTION,
                platform='instagram',
                max_comments=30
            )

            print(f"\n✅ Step 4: AI Analysis Complete")
            print(f"   Total qualified users: {len(qualified_users)}")

            if qualified_users:
                print("\n📋 Top qualified users:")
                for i, user in enumerate(qualified_users[:5], 1):
                    print(f"   {i}. @{user['username']}")
                    print(f"      Score: {user['intent_score']:.2f}")
                    print(f"      Priority: {user['priority']}")
                    print(f"      Reasons: {', '.join(user['reasons'][:2])}")
                    print()

                # 保存结果
                with open('instagram_qualified_users.json', 'w') as f:
                    json.dump(qualified_users, f, indent=2, ensure_ascii=False)
                print("💾 Saved to instagram_qualified_users.json")

                print("\n" + "=" * 70)
                print("✅ SUCCESS - Found qualified users from Instagram!")
                print("=" * 70)
                print("\nNext steps:")
                print("1. Review instagram_qualified_users.json")
                print("2. Run DM campaign: python3 run_dm_outreach.py")
            else:
                print("\n⚠️  No qualified users found in this post")
                print("   Try different keywords or posts")
        else:
            print("\n❌ No posts found for this keyword")

        browser.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed")
