#!/usr/bin/env python3
"""
测试Facebook群组抓取功能
"""

import sys
sys.path.append('src')

from facebook_scraper import FacebookScraper

print("=" * 70)
print("🧪 Testing Facebook Group Scraping")
print("=" * 70)

# 输入群组ID
print("\n📝 Enter Facebook group IDs (one per line, empty line to finish):")
print("   Example: jobsearch")
print("   Example: 123456789")
print("   (Find group ID in URL: facebook.com/groups/{ID}/)")

group_ids = []
while True:
    group_id = input(f"Group #{len(group_ids)+1}: ").strip()
    if not group_id:
        break
    group_ids.append(group_id)

if not group_ids:
    print("❌ No group IDs provided!")
    sys.exit(1)

print(f"\n🔍 Testing with {len(group_ids)} groups: {', '.join(group_ids)}")

# 初始化scraper
scraper = FacebookScraper()

try:
    # Step 1: 从群组获取帖子
    print("\n[1/3] Fetching posts from groups...")
    posts = scraper.search_posts_from_groups(group_ids, max_posts_per_group=3)

    print(f"\n✅ Found {len(posts)} posts")

    if not posts:
        print("\n⚠️  No posts found!")
        print("💡 Possible reasons:")
        print("   1. Group IDs are incorrect")
        print("   2. Not logged in (run: python3 facebook_login_and_save_auth.py)")
        print("   3. Not a member of these groups")
        print("   4. Groups are private or restricted")
        sys.exit(1)

    # 显示帖子
    print("\n📋 Sample posts:")
    for i, post in enumerate(posts[:5], 1):
        print(f"\n[{i}] {post.get('url', 'N/A')[:80]}...")
        print(f"    Group: {post.get('group_id', 'N/A')}")

    # Step 2: 从第一个帖子抓取评论
    print("\n[2/3] Testing comment extraction from first post...")
    test_post = posts[0]
    comments = scraper.get_post_comments(test_post['url'], max_comments=5)

    print(f"\n✅ Found {len(comments)} comments")

    if comments:
        print("\n📋 Sample comments:")
        for i, comment in enumerate(comments[:3], 1):
            print(f"\n[{i}] {comment.get('username')}")
            print(f"    Text: {comment.get('text', '')[:100]}...")
            print(f"    Profile: {comment.get('profile_url', 'N/A')}")
    else:
        print("\n⚠️  No comments found!")
        print("💡 Post might not have comments yet")

    # Step 3: 测试完整流程
    print("\n[3/3] Testing complete user search...")
    users = scraper.search_users(group_ids, limit=10)

    print(f"\n✅ Found {len(users)} users")

    if users:
        print("\n📋 Sample users:")
        for i, user in enumerate(users[:5], 1):
            print(f"\n[{i}] {user.get('username')}")
            print(f"    Comment: {user.get('comment_text', '')[:100]}...")
            print(f"    Profile: {user.get('profile_url', 'N/A')}")
    else:
        print("\n⚠️  No users found!")

finally:
    # 关闭浏览器
    print("\n[Cleanup] Closing browser...")
    scraper._close_browser()

print("\n" + "=" * 70)
print("✅ Test completed!")
print("=" * 70)

if posts and comments:
    print(f"\n✨ Success! Found {len(posts)} posts and {len(comments)} comments")
    print("\n💡 Next step: Edit run_facebook_campaign.py")
    print(f"   Add these group IDs to GROUP_IDS:")
    for gid in group_ids:
        print(f'   "{gid}",')
    print("\n   Then run: python3 run_facebook_campaign.py")
else:
    print("\n⚠️  Issues found - please check the errors above")
