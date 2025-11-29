#!/usr/bin/env python3
"""
用真实用户测试DM发送功能
警告：这会真的发送消息！只用于测试！
"""

import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 测试消息模板
TEST_MESSAGE_TEMPLATE = """Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""


def test_linkedin_real():
    """测试LinkedIn DM - 真实发送"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing LinkedIn DM (REAL)")
    logger.info("="*60)

    try:
        from src.linkedin_dm_sender import LinkedInDMSender
        from src.linkedin_scraper import LinkedInScraper

        # 先搜索一些用户
        scraper = LinkedInScraper()
        logger.info("🔍 Searching for LinkedIn users...")
        users = scraper.search_users(['startup', 'founder'], limit=3)

        if not users:
            logger.warning("   ⚠️  No users found")
            return False

        logger.info(f"   Found {len(users)} users")

        # 选择第一个用户来测试
        test_user = users[0]
        logger.info(f"\n📋 Test user: {test_user.get('name', 'Unknown')}")
        logger.info(f"   URL: {test_user.get('profile_url')}")

        # 初始化DM发送器
        sender = LinkedInDMSender()
        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)

        logger.info(f"\n📝 Message to send:\n{formatted_message}\n")

        # 确认是否要发送
        response = input("⚠️  Send this message? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("   ❌ Cancelled by user")
            return False

        # 发送消息
        success = sender.send_dm(test_user, formatted_message)

        if success:
            logger.info("\n✅ LinkedIn DM sent successfully!")
        else:
            logger.error("\n❌ LinkedIn DM failed")

        return success

    except Exception as e:
        logger.error(f"❌ LinkedIn test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_twitter_real():
    """测试Twitter DM - 真实发送"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing Twitter DM (REAL)")
    logger.info("="*60)

    try:
        from src.twitter_dm_sender import TwitterDMSender
        from src.twitter_scraper import TwitterScraper

        # 搜索用户
        scraper = TwitterScraper()
        logger.info("🔍 Searching for Twitter users...")
        users = scraper.search_users(['startup', 'founder'], limit=3)

        if not users:
            logger.warning("   ⚠️  No users found")
            return False

        logger.info(f"   Found {len(users)} users")

        # 选择第一个用户
        test_user = users[0]
        logger.info(f"\n📋 Test user: @{test_user.get('username')}")

        # 初始化DM发送器
        sender = TwitterDMSender()
        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)

        logger.info(f"\n📝 Message to send:\n{formatted_message}\n")

        # 确认
        response = input("⚠️  Send this message? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("   ❌ Cancelled by user")
            return False

        # 发送
        success = sender.send_dm(test_user, formatted_message)

        if success:
            logger.info("\n✅ Twitter DM sent successfully!")
        else:
            logger.error("\n❌ Twitter DM failed")

        return success

    except Exception as e:
        logger.error(f"❌ Twitter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reddit_real():
    """测试Reddit DM - 真实发送"""
    logger.info("\n" + "="*60)
    logger.info("🧪 Testing Reddit DM (REAL)")
    logger.info("="*60)

    try:
        from src.reddit_dm_sender import RedditDMSender
        from src.reddit_scraper import RedditScraper

        # 搜索用户
        scraper = RedditScraper()
        logger.info("🔍 Searching for Reddit users...")
        users = scraper.search_users(['startup', 'entrepreneur'], limit=3)

        if not users:
            logger.warning("   ⚠️  No users found")
            return False

        logger.info(f"   Found {len(users)} users")

        # 选择第一个用户
        test_user = users[0]
        logger.info(f"\n📋 Test user: u/{test_user.get('username')}")

        # 初始化DM发送器
        sender = RedditDMSender()
        formatted_message = sender.format_message(TEST_MESSAGE_TEMPLATE, test_user)

        logger.info(f"\n📝 Message to send:\n{formatted_message}\n")

        # 确认
        response = input("⚠️  Send this message? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("   ❌ Cancelled by user")
            return False

        # 发送
        success = sender.send_dm(test_user, formatted_message)

        if success:
            logger.info("\n✅ Reddit DM sent successfully!")
        else:
            logger.error("\n❌ Reddit DM failed")

        return success

    except Exception as e:
        logger.error(f"❌ Reddit test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行测试"""
    logger.info("\n" + "="*60)
    logger.info("🚀 Real DM Sending Test")
    logger.info("="*60)
    logger.info("\n⚠️  WARNING: This will send REAL messages!")
    logger.info("   Only proceed if you want to test with actual users\n")

    # 询问用户想测试哪个平台
    logger.info("Which platform do you want to test?")
    logger.info("  1. LinkedIn")
    logger.info("  2. Twitter/X")
    logger.info("  3. Reddit")
    logger.info("  4. Instagram")
    logger.info("  5. TikTok")
    logger.info("  0. Exit")

    choice = input("\nEnter platform number: ")

    if choice == '1':
        return test_linkedin_real()
    elif choice == '2':
        return test_twitter_real()
    elif choice == '3':
        return test_reddit_real()
    elif choice == '4':
        logger.info("Instagram test not implemented yet")
        return False
    elif choice == '5':
        logger.info("TikTok test not implemented yet")
        return False
    else:
        logger.info("Exiting...")
        return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⏸️  Test cancelled by user")
        sys.exit(0)
