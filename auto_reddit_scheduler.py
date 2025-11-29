#!/usr/bin/env python3
"""
Reddit自动发帖调度系统
智能养号策略，永久运行
"""
import sys
sys.path.insert(0, 'src')
from reddit_poster import RedditPoster
from reddit_account_manager import RedditAccountManager
from generate_reddit_build_in_public import generate_reddit_post
import time
import logging
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditScheduler:
    def __init__(self):
        self.account_manager = RedditAccountManager()
        self.poster = None

    def run_forever(self):
        """永久运行"""
        logger.info("=" * 80)
        logger.info("🚀 Reddit Build in Public自动发帖系统 - 永久运行模式")
        logger.info("=" * 80)

        # 显示账号状态
        stats = self.account_manager.get_stats()
        logger.info("\n📊 账号状态:")
        for key, value in stats.items():
            logger.info(f"   {key}: {value}")

        logger.info("\n⏰ 开始监控，智能发帖...")
        logger.info("   按Ctrl+C停止\n")

        try:
            while True:
                # 检查是否可以发帖
                can_post, reason = self.account_manager.can_post_now()

                if can_post:
                    logger.info("\n" + "=" * 80)
                    logger.info("✅ 满足发帖条件，开始发帖流程")
                    logger.info("=" * 80)

                    # 生成内容
                    logger.info("\n📝 生成Build in Public内容...")
                    post_types = ["progress", "technical", "story", "learning", "milestone"]
                    post_type = random.choice(post_types)

                    try:
                        post_data = generate_reddit_post(post_type)
                        logger.info(f"   ✅ 内容生成完成 (类型: {post_type})")
                        logger.info(f"   标题: {post_data['title'][:60]}...")
                        logger.info(f"   板块: {post_data['subreddit']}")

                        # 发布帖子
                        success = self.post_to_reddit(
                            post_data['subreddit'].replace('r/', ''),
                            post_data['title'],
                            post_data['body']
                        )

                        # 记录结果
                        self.account_manager.record_post(
                            post_data['subreddit'],
                            post_data['title'],
                            success
                        )

                        if success:
                            logger.info("\n✅ 发帖成功！")
                            logger.info(f"   今日已发: {self.account_manager.get_today_posts_count()}/{self.account_manager.get_daily_post_limit()}")

                            # 随机等待（避免规律性）
                            wait_time = random.randint(1800, 3600)  # 30-60分钟
                            logger.info(f"\n⏳ 随机等待 {wait_time//60} 分钟...")
                            time.sleep(wait_time)
                        else:
                            logger.error("\n❌ 发帖失败，1小时后重试")
                            time.sleep(3600)

                    except Exception as e:
                        logger.error(f"\n❌ 生成或发帖出错: {str(e)}")
                        time.sleep(3600)

                else:
                    logger.info(f"\n⏸️  暂不满足发帖条件: {reason}")
                    logger.info("   1小时后再检查...\n")
                    time.sleep(3600)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断...")
        finally:
            if self.poster:
                try:
                    self.poster.close_browser()
                except:
                    pass
            logger.info("\n✅ 调度系统已停止")

    def post_to_reddit(self, subreddit, title, body):
        """发帖到Reddit"""
        try:
            if not self.poster:
                self.poster = RedditPoster()
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    logger.error("❌ Reddit登录失败")
                    return False

            success = self.poster.create_post(subreddit, title, body)

            if success:
                time.sleep(30)  # 保持浏览器打开30秒检查

            return success

        except Exception as e:
            logger.error(f"❌ 发帖错误: {str(e)}")
            return False

if __name__ == "__main__":
    scheduler = RedditScheduler()
    scheduler.run_forever()
