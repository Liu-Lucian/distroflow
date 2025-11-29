#!/usr/bin/env python3
"""
快速测试Reddit DM发送 - 使用更新后的代码
"""

import sys
sys.path.append('src')

from reddit_dm_sender import RedditDMSender

print("=" * 60)
print("🧪 Quick Reddit DM Test")
print("=" * 60)

# 测试用户
test_user = {
    'username': 'Gari_305',
    'name': 'Gari',
    'company': 'their company',
    'project': 'their project'
}

# 消息（带网址）
message = """Hey {{name}}, I came across your posts — really insightful stuff.

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

print(f"\n📋 Target: u/{test_user['username']}")

sender = RedditDMSender()
formatted = sender.format_message(message, test_user)

print(f"\n📝 Message:\n{formatted}\n")
print("=" * 60)
print("🚀 Sending DM...")
print("=" * 60)

try:
    success = sender.send_dm(test_user, formatted)

    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS - Message sent!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED - Could not send message")
        print("=" * 60)
finally:
    sender.cleanup()
