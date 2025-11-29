#!/usr/bin/env python3
"""
Twitter DM自动测试 - 查找用户并发送
"""

import sys
sys.path.append('src')

from twitter_dm_sender import TwitterDMSender

print("=" * 60)
print("🚀 Twitter DM Auto Test")
print("=" * 60)

# 使用一个公开的测试账号
test_user = {
    'username': 'paulg',  # Y Combinator创始人，公开账号
    'name': 'Paul Graham',
    'bio': 'Founder of Y Combinator'
}

print(f"\n📋 Target: @{test_user['username']}")
print(f"   Name: {test_user.get('name', 'N/A')}")

# 消息模板（带网址）
message_template = """Hey {{name}}, I came across your posts about startups — really insightful stuff.

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually in the startup world."""

sender = TwitterDMSender()
formatted = sender.format_message(message_template, test_user)

print(f"\n📝 Message:")
print("-" * 60)
print(formatted)
print("-" * 60)

print("\n" + "=" * 60)
print("🚀 Sending DM...")
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
        print("   - User has DMs disabled")
        print("   - You need to follow them first")
        print("   - Rate limit reached")
        print("   - Twitter detected automation")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    sender.cleanup()
