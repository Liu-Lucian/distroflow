#!/usr/bin/env python3
"""
测试Instagram DM with AI Healer Integration
"""

import sys
sys.path.append('src')

from instagram_dm_sender import InstagramDMSender

print("=" * 70)
print("🤖 Testing Instagram DM with AI Healer")
print("=" * 70)

# 初始化sender（AI Healer默认启用）
sender = InstagramDMSender(use_ai_healer=True)

# 测试用户（选择一个非网红账号）
test_user = {
    'username': 'startupgrind',  # 可以换成其他用户
    'name': 'Startup Grind'
}

# 测试消息
test_message = """Hey, I saw your content about startups — really insightful!

I'm building HireMeAI (https://interviewasssistant.com), an AI-powered interview prep platform.

Would love to get your thoughts if you're open to it!"""

print("\n📝 Test Configuration:")
print(f"   Target: @{test_user['username']}")
print(f"   AI Healer: ✅ Enabled")
print(f"   Message: {test_message[:80]}...")

print("\n🚀 Starting test...")
print("   Note: Browser will open in visible mode")
print("   AI will automatically diagnose and fix any issues")
print()

try:
    success = sender.send_dm(test_user, test_message)

    print("\n" + "=" * 70)
    if success:
        print("✅ TEST PASSED - Message sent successfully!")
    else:
        print("❌ TEST FAILED - Could not send message")
    print("=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print(f"❌ TEST ERROR: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()

finally:
    # 清理
    try:
        sender.cleanup()
    except:
        pass

print("\n✅ Test completed")
