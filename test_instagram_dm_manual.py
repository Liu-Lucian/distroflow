#!/usr/bin/env python3
"""
手动指定用户测试Instagram DM
"""

import sys
sys.path.append('src')

from instagram_dm_sender_optimized import InstagramDMSender

print("=" * 70)
print("🧪 Manual Instagram DM Test")
print("=" * 70)

# 手动指定一个测试用户（换一个不同的账号）
test_username = input("\nEnter Instagram username to test (without @): ").strip()

if not test_username:
    print("❌ No username provided")
    sys.exit(1)

test_user = {
    'username': test_username,
    'intent_score': 0.8,
}

print(f"\n📱 Test user: @{test_username}")
print()

# 测试消息
test_message = """Hi! I saw your posts about career and entrepreneurship.

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

print("\n💡 Try another username if this one has issues")
