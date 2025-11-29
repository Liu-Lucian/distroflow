#!/usr/bin/env python3
"""
测试TikTok DM发送
"""

import sys
sys.path.append('src')

from tiktok_dm_sender import TikTokDMSender

print("=" * 60)
print("🚀 TikTok DM Test")
print("=" * 60)

# 测试用户 - 使用一个startup相关的账号
test_user = {
    'username': 'garyvee',  # Gary Vaynerchuk也有TikTok
    'name': 'Gary Vaynerchuk',
}

# 消息模板（带网址）
message = """Hey, I came across your content — really inspiring!

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

Would love to hear your thoughts!"""

print(f"\n📋 Target: @{test_user['username']}")

sender = TikTokDMSender()
formatted = sender.format_message(message, test_user)

print(f"\n📝 Message:")
print("-" * 60)
print(formatted)
print("-" * 60)

print("\n" + "=" * 60)
print("🚀 Testing TikTok DM...")
print("=" * 60)

try:
    success = sender.send_dm(test_user, formatted)

    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS - DM SENT!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED - Could not send DM")
        print("=" * 60)
        print("\n⚠️  Possible reasons:")
        print("   - Not logged in (cookies expired)")
        print("   - User has DMs restricted")
        print("   - Need to follow them first")
        print("   - TikTok detected automation")
        print("   - Rate limit reached")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    sender.cleanup()
