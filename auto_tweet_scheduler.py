#!/usr/bin/env python3
"""
Twitter自动定时发布系统
每天在指定时间段自动发布build in public风格的tweets
"""
import sys
sys.path.insert(0, 'src')
from twitter_poster import TwitterPoster
import json
import time
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterScheduler:
    def __init__(self, schedule_file):
        self.schedule_file = schedule_file
        self.load_schedule()
        self.poster = None

    def load_schedule(self):
        """加载调度文件"""
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                self.schedule_data = json.load(f)
            logger.info(f"✅ 已加载调度文件: {self.schedule_file}")
        except FileNotFoundError:
            logger.error(f"❌ 找不到调度文件: {self.schedule_file}")
            sys.exit(1)

    def save_schedule(self):
        """保存调度文件"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule_data, f, indent=2, ensure_ascii=False)

    def is_in_time_slot(self, time_slot_str):
        """检查当前时间是否在指定时间段内"""
        now = datetime.now()
        current_time = now.time()

        # 解析时间段 "09:00-10:00"
        start_str, end_str = time_slot_str.split('-')
        start_hour, start_min = map(int, start_str.split(':'))
        end_hour, end_min = map(int, end_str.split(':'))

        start_time = datetime.now().replace(hour=start_hour, minute=start_min, second=0).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_min, second=0).time()

        return start_time <= current_time <= end_time

    def post_single_tweet(self, tweet_text):
        """发布单条tweet"""
        try:
            if not self.poster:
                self.poster = TwitterPoster()
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    raise Exception("Twitter登录验证失败")

            # 构造单条tweet格式
            content = {
                'tweets': [tweet_text],
                'total_tweets': 1
            }

            success = self.poster.create_post(content)

            if success:
                logger.info(f"✅ Tweet发布成功！")
                logger.info(f"   内容: {tweet_text[:100]}...")
                return True
            else:
                logger.error("❌ Tweet发布失败")
                return False

        except Exception as e:
            logger.error(f"❌ 发布错误: {str(e)}")
            return False

    def run_schedule(self):
        """运行调度，监控并在正确时间发布"""
        logger.info("=" * 80)
        logger.info("🚀 Twitter自动调度系统已启动")
        logger.info("=" * 80)

        logger.info("\n📋 今日调度:")
        for item in self.schedule_data['schedule']:
            status = "✅ 已发布" if item['posted'] else "⏳ 待发布"
            logger.info(f"   {item['time_slot']}: {status}")
            logger.info(f"      {item['tweet'][:80]}...")

        logger.info("\n⏰ 开始监控，将在指定时间段自动发布...")
        logger.info("   按Ctrl+C停止\n")

        try:
            while True:
                now = datetime.now()
                current_time_str = now.strftime("%H:%M:%S")

                # 检查每个时间段
                for item in self.schedule_data['schedule']:
                    if not item['posted'] and self.is_in_time_slot(item['time_slot']):
                        logger.info(f"\n{'='*80}")
                        logger.info(f"⏰ 时间到！当前时间段: {item['time_slot']}")
                        logger.info(f"{'='*80}")

                        # 在时间段内随机延迟，使发布更自然
                        random_delay = random.randint(1, 300)  # 0-5分钟
                        logger.info(f"⏳ 随机延迟 {random_delay} 秒，使发布更自然...")
                        time.sleep(random_delay)

                        logger.info(f"📤 发布Tweet...")
                        success = self.post_single_tweet(item['tweet'])

                        if success:
                            item['posted'] = True
                            item['posted_at'] = datetime.now().isoformat()
                            self.save_schedule()
                            logger.info("✅ 状态已保存")

                        # 发布后等待，避免重复发布
                        time.sleep(60)

                # 检查是否所有都已发布
                all_posted = all(item['posted'] for item in self.schedule_data['schedule'])
                if all_posted:
                    logger.info("\n" + "=" * 80)
                    logger.info("🎉 今日所有tweets已发布完成！")
                    logger.info("=" * 80)
                    break

                # 每分钟检查一次
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断，保存状态...")
            self.save_schedule()

        finally:
            if self.poster:
                logger.info("🔒 关闭浏览器...")
                self.poster.close_browser()

            logger.info("\n✅ 调度系统已停止")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("用法: python3 auto_tweet_scheduler.py <schedule_file.json>")
        logger.error("示例: python3 auto_tweet_scheduler.py twitter_schedule_20250122.json")
        sys.exit(1)

    schedule_file = sys.argv[1]
    scheduler = TwitterScheduler(schedule_file)
    scheduler.run_schedule()
