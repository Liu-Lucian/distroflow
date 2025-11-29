#!/usr/bin/env python3
"""
测试Facebook评论抓取功能
只抓取评论，不发送DM
"""

import sys
sys.path.append('src')

from facebook_scraper import FacebookScraper

print("=" * 70)
print("🧪 Testing Facebook Comment Scraping")
print("=" * 70)

# 测试帖子URL（请替换为真实的帖子URL）
test_post_url = input("\n📝 Enter a Facebook post URL to test: ").strip()

if not test_post_url:
    print("❌ No URL provided!")
    sys.exit(1)

print(f"\n🔍 Testing with URL: {test_post_url}")

# 初始化scraper
scraper = FacebookScraper()

try:
    # 抓取评论
    print("\n[1/2] Scraping comments...")
    comments = scraper.get_post_comments(test_post_url, max_comments=10)

    print(f"\n✅ Found {len(comments)} comments")

    # 显示前几条评论
    if comments:
        print("\n📋 Sample comments:")
        for i, comment in enumerate(comments[:5], 1):
            print(f"\n[{i}] {comment.get('username')}")
            print(f"    Text: {comment.get('text', '')[:100]}...")
            print(f"    Profile: {comment.get('profile_url', 'N/A')}")
    else:
        print("\n⚠️  No comments found!")
        print("💡 Possible reasons:")
        print("   1. Post has no comments")
        print("   2. Not logged in (run: python3 facebook_login_and_save_auth.py)")
        print("   3. Post URL is incorrect")
        print("   4. Page didn't load properly")

finally:
    # 关闭浏览器
    print("\n[2/2] Closing browser...")
    scraper._close_browser()

print("\n" + "=" * 70)
print("✅ Test completed!")
print("=" * 70)

if comments:
    print(f"\n✨ Success! Found {len(comments)} comments")
    print("\n💡 Next step: Edit run_facebook_campaign_simple.py")
    print("   Add this URL to POST_URLS list and run the full campaign")
else:
    print("\n⚠️  No comments found - please check the issues above")
