#!/usr/bin/env python3
"""
测试所有平台的DM发送功能
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 测试消息模板
TEST_MESSAGE_TEMPLATE = """Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""


def test_linkedin():
    """测试LinkedIn DM"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing LinkedIn DM Sender")
    logger.info("="*60)

    try:
        from src.linkedin_dm_sender import LinkedInDMSender

        sender = LinkedInDMSender()

        # 测试用户（你需要提供一个真实的LinkedIn profile URL来测试）
        test_user = {
            'name': 'Test User',
            'profile_url': 'https://www.linkedin.com/in/test-user/',  # 替换为真实URL
            'company': 'Test Company',
            'project': 'Test Project'
        }

        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)
        logger.info(f"\n📝 Formatted message:\n{formatted_message}\n")

        # 如果你想真的发送，取消下面的注释
        # success = sender.send_dm(test_user, formatted_message)
        # logger.info(f"\n{'✅' if success else '❌'} LinkedIn DM test: {success}")

        logger.info("✅ LinkedIn DM sender initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ LinkedIn test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_twitter():
    """测试Twitter DM"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing Twitter DM Sender")
    logger.info("="*60)

    try:
        from src.twitter_dm_sender import TwitterDMSender

        sender = TwitterDMSender()

        test_user = {
            'username': 'test_user',  # 替换为真实username
            'name': 'Test User',
            'company': 'Test Corp',
            'project': 'AI Project'
        }

        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)
        logger.info(f"\n📝 Formatted message:\n{formatted_message}\n")

        logger.info("✅ Twitter DM sender initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Twitter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reddit():
    """测试Reddit DM"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing Reddit DM Sender")
    logger.info("="*60)

    try:
        from src.reddit_dm_sender import RedditDMSender

        sender = RedditDMSender()

        test_user = {
            'username': 'test_user',  # 替换为真实username
            'name': 'Test User'
        }

        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)
        logger.info(f"\n📝 Formatted message:\n{formatted_message}\n")

        logger.info("✅ Reddit DM sender initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Reddit test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_instagram():
    """测试Instagram DM"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing Instagram DM Sender")
    logger.info("="*60)

    try:
        from src.instagram_dm_sender import InstagramDMSender

        sender = InstagramDMSender()

        test_user = {
            'username': 'test_user',  # 替换为真实username
            'name': 'Test User'
        }

        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)
        logger.info(f"\n📝 Formatted message:\n{formatted_message}\n")

        logger.info("✅ Instagram DM sender initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Instagram test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tiktok():
    """测试TikTok DM"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing TikTok DM Sender")
    logger.info("="*60)

    try:
        from src.tiktok_dm_sender import TikTokDMSender

        sender = TikTokDMSender()

        test_user = {
            'username': 'test_user',  # 替换为真实username
            'name': 'Test User'
        }

        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)
        logger.info(f"\n📝 Formatted message:\n{formatted_message}\n")

        logger.info("✅ TikTok DM sender initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ TikTok test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    logger.info("\n" + "="*60)
    logger.info("🚀 Testing All DM Senders")
    logger.info("="*60)

    results = {}

    # 测试所有平台
    results['LinkedIn'] = test_linkedin()
    results['Twitter'] = test_twitter()
    results['Reddit'] = test_reddit()
    results['Instagram'] = test_instagram()
    results['TikTok'] = test_tiktok()

    # 打印总结
    logger.info("\n" + "="*60)
    logger.info("📊 Test Summary")
    logger.info("="*60)

    for platform, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {platform}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    logger.info(f"\n🎯 Results: {passed}/{total} platforms initialized successfully")

    if passed == total:
        logger.info("\n✅ All DM senders are ready!")
        logger.info("\nℹ️  Next steps:")
        logger.info("   1. Update test user profiles with real usernames/URLs")
        logger.info("   2. Uncomment the send_dm() calls to test actual sending")
        logger.info("   3. Start with 1-2 test messages to verify everything works")
    else:
        logger.info("\n⚠️  Some platforms failed initialization")
        logger.info("   Check the error messages above for details")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
