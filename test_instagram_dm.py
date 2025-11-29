#!/usr/bin/env python3
"""
测试Instagram DM发送 - 使用搜索→帖子→头像→消息流程
"""

import sys
sys.path.append('src')

from instagram_dm_sender import InstagramDMSender

print("=" * 60)
print("🚀 Instagram DM Test (New Workflow)")
print("=" * 60)

# 测试用户 - 使用一个较小的账号（更容易有Message按钮）
test_user = {
    'username': 'garyvee',  # 改用startup相关的账号
    'name': 'Gary Vaynerchuk',
}

# 消息模板（带网址）
message = """Hey, I came across your content — really inspiring stuff.

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

Would love to hear your thoughts!"""

print(f"\n📋 Target: @{test_user['username']}")

sender = InstagramDMSender()
formatted = sender.format_message(message, test_user)

print(f"\n📝 Message:")
print("-" * 60)
print(formatted)
print("-" * 60)

print("\n" + "=" * 60)
print("🚀 Testing Instagram DM...")
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
        print("   - Not logged in (sessionid expired)")
        print("   - User has DMs restricted")
        print("   - Instagram detected automation")
        print("   - Rate limit reached")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    sender.cleanup()
