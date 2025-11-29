#!/usr/bin/env python3
"""
测试Twitter DM发送
"""

import sys
sys.path.append('src')

from twitter_dm_sender import TwitterDMSender

print("=" * 60)
print("🧪 Twitter DM Test")
print("=" * 60)

# 测试用户 - 使用一个公开账号
test_user = {
    'username': 'elonmusk',  # 测试用，实际不会发送
    'name': 'Elon',
    'company': 'Tesla/SpaceX',
    'project': 'AI initiatives'
}

# 消息
message = """Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

print(f"\n📋 Target: @{test_user['username']}")

sender = TwitterDMSender()
formatted = sender.format_message(message, test_user)

print(f"\n📝 Message:\n{formatted}\n")
print("=" * 60)
print("⚠️  This is a test - we'll check if login works")
print("=" * 60)

try:
    # 只测试登录，不实际发送
    sender._setup_browser()

    # 访问Twitter首页检查登录
    sender.page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=30000)
    sender._random_delay(2, 3)

    current_url = sender.page.url
    print(f"\nCurrent URL: {current_url}")

    if 'login' in current_url or 'i/flow' in current_url:
        print("\n" + "=" * 60)
        print("❌ NOT LOGGED IN")
        print("=" * 60)
        print("Twitter cookies may be expired. Need to save new ones.")
    else:
        print("\n" + "=" * 60)
        print("✅ LOGGED IN SUCCESSFULLY!")
        print("=" * 60)
        print(f"Ready to send DMs")

        # 可以选择测试发送
        response = input("\nDo you want to try sending a DM? (yes/no): ")
        if response.lower() == 'yes':
            success = sender.send_dm(test_user, formatted)
            if success:
                print("\n✅ DM SENT!")
            else:
                print("\n❌ DM FAILED")

    sender.cleanup()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
