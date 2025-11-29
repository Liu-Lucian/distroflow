#!/usr/bin/env python3
"""
简单测试LinkedIn DM功能
直接使用一个LinkedIn profile URL测试
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 测试消息模板
TEST_MESSAGE = """Hey there, I came across your profile on LinkedIn — really liked your background.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""


def test_linkedin_dm():
    """测试LinkedIn DM"""
    logger.info("="*60)
    logger.info("🧪 Testing LinkedIn DM")
    logger.info("="*60)

    from src.linkedin_dm_sender import LinkedInDMSender

    # 初始化发送器
    sender = LinkedInDMSender()

    # 测试用户 - 你需要提供一个真实的LinkedIn URL
    logger.info("\n请提供一个LinkedIn profile URL来测试")
    logger.info("例如: https://www.linkedin.com/in/johndoe/\n")

    profile_url = input("LinkedIn profile URL: ").strip()

    if not profile_url:
        logger.error("❌ No URL provided")
        return False

    # 从URL中提取名字（简单处理）
    try:
        username = profile_url.rstrip('/').split('/')[-1]
        name = username.replace('-', ' ').title()
    except:
        name = "there"

    test_user = {
        'name': name,
        'profile_url': profile_url,
        'company': 'your company',
        'project': 'your work'
    }

    logger.info(f"\n📋 Target user:")
    logger.info(f"   Name: {test_user['name']}")
    logger.info(f"   URL: {test_user['profile_url']}")

    formatted_message = sender.format_message(TEST_MESSAGE, test_user)
    logger.info(f"\n📝 Message to send:\n")
    logger.info("-" * 60)
    logger.info(formatted_message)
    logger.info("-" * 60)

    # 确认
    response = input("\n⚠️  Send this message? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("❌ Cancelled")
        return False

    # 发送
    logger.info("\n🚀 Sending message...")
    logger.info("(浏览器会弹出，你可以看到整个过程)\n")

    success = sender.send_dm(test_user, formatted_message)

    if success:
        logger.info("\n✅ Message sent successfully!")
        logger.info("\n💡 Tip: Check your LinkedIn messages to verify")
    else:
        logger.error("\n❌ Failed to send message")
        logger.info("\n可能的原因:")
        logger.info("  1. LinkedIn cookies过期 - 运行 python3 linkedin_login_and_save_auth.py")
        logger.info("  2. 对方未开启私信 - 尝试其他用户")
        logger.info("  3. 页面结构变化 - 告诉我具体错误信息")

    return success


if __name__ == "__main__":
    try:
        success = test_linkedin_dm()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⏸️  Test cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
