#!/usr/bin/env python3
"""
Reddit DM自动测试 - 不需要交互式输入
"""

import sys
sys.path.append('src')

from reddit_dm_sender import RedditDMSender
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_reddit_dm():
    """测试Reddit DM发送"""

    print("=" * 60)
    print("🧪 Testing Reddit DM Sender")
    print("=" * 60)

    # 初始化sender
    print("\n1️⃣ Initializing Reddit DM sender...")
    try:
        sender = RedditDMSender()
        print("   ✅ Sender initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False

    # 测试用户（你可以改成真实用户）
    test_user = {
        'username': 'spez',  # Reddit CEO，只是测试
        'name': 'Steve',
        'company': 'Reddit',
        'project': 'Reddit Platform'
    }

    # 消息模板
    message_template = """Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

    # 格式化消息
    print("\n2️⃣ Formatting message...")
    formatted_message = sender.format_message(message_template, test_user)
    print(f"\n📝 Message to send:")
    print("-" * 60)
    print(formatted_message)
    print("-" * 60)

    # 询问是否真的发送
    print("\n" + "=" * 60)
    print("⚠️  READY TO SEND REAL MESSAGE")
    print("=" * 60)
    print(f"To: u/{test_user['username']}")
    print("\nThis is just a DRY RUN - we won't actually send")
    print("If you want to actually send, change DRY_RUN to False in the script")

    DRY_RUN = True

    if DRY_RUN:
        print("\n✅ Dry run successful - all components working!")
        print("\nTo actually send messages:")
        print("1. Change DRY_RUN = False in this script")
        print("2. Change test_user to a real target user")
        print("3. Run again")
        sender.cleanup()
        return True

    # 实际发送（如果不是dry run）
    print("\n3️⃣ Sending message...")
    try:
        success = sender.send_dm(test_user, formatted_message)
        if success:
            print("   ✅ Message sent successfully!")
        else:
            print("   ❌ Failed to send message")
        return success
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sender.cleanup()


if __name__ == "__main__":
    try:
        success = test_reddit_dm()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
