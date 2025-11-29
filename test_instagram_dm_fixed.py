#!/usr/bin/env python3
"""
测试修复后的Instagram DM发送
"""

import sys
sys.path.append('src')

from instagram_dm_sender_optimized import InstagramDMSender
import json

print("=" * 70)
print("🧪 Testing Fixed Instagram DM Sender")
print("=" * 70)

# 加载测试用户
try:
    with open('instagram_qualified_users.json', 'r') as f:
        users = json.load(f)

    # 找一个未发送的用户
    test_user = None
    for user in users:
        if not user.get('sent_dm', False):
            test_user = user
            break

    if not test_user:
        print("❌ No unsent users found")
        print("   Using first user for testing...")
        test_user = users[0] if users else None

    if not test_user:
        print("❌ No users found!")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error loading users: {e}")
    sys.exit(1)

print(f"\n📱 Test user: @{test_user.get('username', 'unknown')}")
print(f"   Score: {test_user.get('intent_score', 0)}")
print()

# 测试消息
test_message = """Hi! I saw your post about career advice.

I'm building HireMeAI, an AI interview prep platform. Would love your thoughts!"""

# 创建sender并测试
sender = InstagramDMSender()

print("🚀 Attempting to send DM...")
print()

success = sender.send_dm(test_user, test_message)

if success:
    print("\n" + "=" * 70)
    print("✅ SUCCESS! DM sent successfully!")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("❌ FAILED! Check logs above")
    print("=" * 70)

print("\n💡 If it worked, run: python3 run_instagram_campaign_optimized.py")
