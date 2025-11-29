#!/usr/bin/env python3
"""
测试Twitter DM - 真实发送
"""

import sys
sys.path.append('src')

from twitter_dm_sender import TwitterDMSender
from twitter_scraper_playwright import TwitterScraperPlaywright

print("=" * 60)
print("🚀 Twitter DM Real Send Test")
print("=" * 60)

# 查找一个真实的startup相关用户
print("\n🔍 Finding Twitter users...")
scraper = TwitterScraperPlaywright()
users = scraper.search_users('startup founder', limit=1)

if not users:
    print("❌ No users found")
    sys.exit(1)

test_user = users[0]
print(f"\n📋 Target: @{test_user['username']}")
print(f"   Name: {test_user.get('name', 'N/A')}")
print(f"   Bio: {test_user.get('bio', 'N/A')[:100]}...")

# 消息模板（带网址）
message_template = """Hey {{name}}, I came across your posts about {{project}} — really insightful stuff.

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

sender = TwitterDMSender()
formatted = sender.format_message(message_template, test_user)

print(f"\n📝 Message to send:")
print("-" * 60)
print(formatted)
print("-" * 60)

print("\n" + "=" * 60)
print("⚠️  READY TO SEND REAL DM")
print("=" * 60)
print(f"To: @{test_user['username']}")
print("\nThis will send a REAL message!")

response = input("\nSend this message? (yes/no): ")

if response.lower() != 'yes':
    print("\n❌ Cancelled")
    sys.exit(0)

print("\n🚀 Sending DM...")

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
        print("\nPossible reasons:")
        print("- User has DMs disabled")
        print("- You need to follow them first")
        print("- Rate limit reached")

finally:
    sender.cleanup()
