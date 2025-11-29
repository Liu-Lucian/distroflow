#!/usr/bin/env python3
"""
测试任意Facebook URL
可以测试群组、帖子、或主页
"""

import sys
sys.path.append('src')

from facebook_scraper import FacebookScraper
import re

print("=" * 70)
print("🧪 Testing Facebook URL")
print("=" * 70)

# 输入URL
print("\n📝 Enter a Facebook URL to test:")
print("   Examples:")
print("   - Group: https://www.facebook.com/groups/123456/")
print("   - Post: https://www.facebook.com/groups/123/posts/456/")
print("   - Any post: https://www.facebook.com/username/posts/123/")

url = input("\nURL: ").strip()

if not url:
    print("❌ No URL provided!")
    sys.exit(1)

print(f"\n🔍 Testing URL: {url}")

# 判断URL类型
if '/groups/' in url and '/posts/' in url:
    url_type = "Group Post"
elif '/groups/' in url:
    url_type = "Group"
elif '/posts/' in url or '/permalink/' in url:
    url_type = "Post"
else:
    url_type = "Unknown"

print(f"   Type: {url_type}")

# 初始化scraper
scraper = FacebookScraper()

try:
    if url_type == "Group":
        # 测试群组
        print("\n[Test] Fetching posts from group...")

        # 提取群组ID
        match = re.search(r'/groups/([^/]+)', url)
        if match:
            group_id = match.group(1)
            print(f"   Group ID: {group_id}")

            posts = scraper.search_posts_from_groups([group_id], max_posts_per_group=3)

            print(f"\n✅ Found {len(posts)} posts")

            if posts:
                print("\n📋 Sample posts:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n[{i}] {post.get('url', 'N/A')[:80]}...")
            else:
                print("\n⚠️  No posts found!")
                print("💡 Reasons:")
                print("   1. Not a member of this group")
                print("   2. Group is private")
                print("   3. Invalid group ID")
        else:
            print("❌ Could not extract group ID from URL")

    elif url_type in ["Post", "Group Post"]:
        # 测试帖子评论
        print("\n[Test] Fetching comments from post...")

        comments = scraper.get_post_comments(url, max_comments=10)

        print(f"\n✅ Found {len(comments)} comments")

        if comments:
            print("\n📋 Sample comments:")
            for i, comment in enumerate(comments[:5], 1):
                print(f"\n[{i}] {comment.get('username')}")
                print(f"    Text: {comment.get('text', '')[:100]}...")
                print(f"    Profile: {comment.get('profile_url', 'N/A')}")
        else:
            print("\n⚠️  No comments found!")
            print("💡 Reasons:")
            print("   1. Post has no comments")
            print("   2. Can't access this post (privacy)")
            print("   3. Invalid post URL")

    else:
        print("\n⚠️  Unknown URL type")
        print("Please provide a group or post URL")

finally:
    # 关闭浏览器
    print("\n[Cleanup] Closing browser...")
    scraper._close_browser()

print("\n" + "=" * 70)
print("✅ Test completed!")
print("=" * 70)

print("\n💡 Tips:")
print("   - Use group URLs if you're a member")
print("   - Use public post URLs for testing")
print("   - Make sure you're logged in (run: python3 facebook_login_and_save_auth.py)")
