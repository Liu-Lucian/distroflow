#!/usr/bin/env python3
"""
测试完整DM营销流程：搜索关键词 → 找到用户 → 发送私信
"""

import sys
sys.path.append('src')

from reddit_dm_sender import RedditDMSender
from twitter_dm_sender import TwitterDMSender
from reddit_scraper import RedditScraper
from twitter_scraper_playwright import TwitterPlaywrightScraper

print("=" * 60)
print("🚀 DM Campaign Test - Keyword → Users → DM")
print("=" * 60)

# 配置
KEYWORD = "interview preparation"  # 搜索关键词
PLATFORM = "reddit"  # 测试平台：reddit 或 twitter
MAX_USERS = 1  # 测试发送数量（先发1条测试）
DRY_RUN = False  # True=只打印不发送，False=真实发送

# 消息模板
MESSAGE_TEMPLATE = """Hey {{name}}, I saw your post about {{keyword}} — really helpful insights!

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

Would love to get your thoughts if you're open to it!"""

print(f"\n📋 Campaign Config:")
print(f"   Platform: {PLATFORM}")
print(f"   Keyword: {KEYWORD}")
print(f"   Max Users: {MAX_USERS}")
print(f"   Dry Run: {DRY_RUN}")

# 步骤1: 搜索用户
print("\n" + "=" * 60)
print("🔍 Step 1: Searching for users...")
print("=" * 60)

if PLATFORM == "reddit":
    scraper = RedditScraper()
    users = scraper.search_users(KEYWORD, limit=MAX_USERS)
elif PLATFORM == "twitter":
    scraper = TwitterPlaywrightScraper()
    users = scraper.search_users(KEYWORD, limit=MAX_USERS)
else:
    print(f"❌ Unsupported platform: {PLATFORM}")
    sys.exit(1)

if not users:
    print("❌ No users found")
    sys.exit(1)

print(f"\n✅ Found {len(users)} users:")
for i, user in enumerate(users, 1):
    username = user.get('username', 'N/A')
    name = user.get('name', 'N/A')
    print(f"   {i}. @{username} ({name})")

# 步骤2: 发送DM
print("\n" + "=" * 60)
print("💬 Step 2: Sending DMs...")
print("=" * 60)

if PLATFORM == "reddit":
    sender = RedditDMSender()
elif PLATFORM == "twitter":
    sender = TwitterDMSender()

success_count = 0
fail_count = 0

for i, user in enumerate(users, 1):
    username = user.get('username', 'N/A')
    name = user.get('name', username)  # 如果没有名字就用username

    print(f"\n[{i}/{len(users)}] Target: @{username}")

    # 格式化消息
    message = MESSAGE_TEMPLATE.replace('{{name}}', name)
    message = message.replace('{{keyword}}', KEYWORD)

    print(f"📝 Message preview:")
    print("-" * 40)
    print(message[:150] + "..." if len(message) > 150 else message)
    print("-" * 40)

    if DRY_RUN:
        print("🔵 DRY RUN - Message not sent")
        success_count += 1
    else:
        try:
            success = sender.send_dm(user, message)
            if success:
                print("✅ Sent successfully")
                success_count += 1
            else:
                print("❌ Failed to send")
                fail_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            fail_count += 1

# 清理
if not DRY_RUN:
    sender.cleanup()

# 总结
print("\n" + "=" * 60)
print("📊 Campaign Summary")
print("=" * 60)
print(f"Total Users: {len(users)}")
print(f"✅ Successful: {success_count}")
print(f"❌ Failed: {fail_count}")

if DRY_RUN:
    print("\n💡 This was a DRY RUN. Set DRY_RUN=False to send real messages.")
else:
    print("\n✅ Campaign complete!")
