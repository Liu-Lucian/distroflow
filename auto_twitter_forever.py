#!/usr/bin/env python3
"""
Twitter自动发布系统 - 永久运行版
每天自动生成4条Build in Public风格tweets并在指定时间发布
当天发布完成后自动生成第二天的tweets，无需人工干预
"""
import sys
sys.path.insert(0, 'src')
from twitter_poster import TwitterPoster
import os
from openai import OpenAI
import json
import time
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class TwitterForeverBot:
    def __init__(self):
        self.poster = None

    def generate_build_in_public_tweet(self):
        """生成单条build in public风格的tweet"""

        prompt = """You are the founder of HireMeAI (https://interviewasssistant.com), building in public on Twitter.

Generate a high-quality original tweet in ENGLISH with these requirements:
1. **Real experience sharing** - Share genuine stories about product development, user feedback, or technical challenges
2. **Data or insights** - Include specific numbers, test results, or valuable findings
3. **Thought-provoking perspective** - Provide new angles, counter-intuitive discoveries, or useful insights
4. **Natural product mention** - Don't hard-sell, make readers interested through context
5. **MUST include URL** - Naturally include https://interviewasssistant.com in the tweet

Topic ideas (choose one):
- Technical discoveries while building an AI interview assistant
- Real user feedback data and insights
- Interesting AI applications in interview preparation
- Startup failures and learnings
- Product iteration decisions and reasoning
- Observations about the interview industry

Style examples:
✅ "Just analyzed 100 users' interview prep data. Found something counter-intuitive: prep time ≠ success rate. The real key is..."
✅ "Week 3 of HireMeAI launch: conversion jumped from 2% to 15%. Changed only ONE thing: removed all fancy features, focused on solving one problem..."
✅ "Why do most AI interview assistants fail? Spent 3 months finding out. Hint: it's not a tech problem..."

❌ Avoid:
- Pure advertising "Our product is great, try it now!"
- Empty motivation "Just keep going"
- Claims without data

Format:
- **CRITICAL: Max 260 characters total (leaving buffer for safety)**
- MUST include https://interviewasssistant.com
- Use emoji sparingly (1-2 max)
- Add 1-2 relevant hashtags ONLY if they fit within character limit
- Be concise and impactful

Output ONLY the tweet text in ENGLISH, no title or extra explanation:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=150
        )

        tweet = response.choices[0].message.content.strip()

        # 确保包含URL
        if 'https://interviewasssistant.com' not in tweet:
            tweet += "\n\n👉 https://interviewasssistant.com"

        return tweet

    def generate_daily_schedule(self, target_date=None):
        """生成一天的tweets调度"""
        if target_date is None:
            target_date = datetime.now()

        logger.info(f"📝 生成 {target_date.strftime('%Y-%m-%d')} 的Build in Public tweets...")

        tweets = []
        for i in range(4):
            logger.info(f"   生成第 {i+1}/4 条...")
            tweet = self.generate_build_in_public_tweet()
            tweets.append(tweet)
            logger.info(f"   ✅ 完成 ({len(tweet)} 字符)")
            time.sleep(1)  # 避免API限流

        # 创建调度
        schedule = {
            "generated_at": datetime.now().isoformat(),
            "target_date": target_date.strftime('%Y-%m-%d'),
            "schedule": [
                {
                    "time_slot": "09:00-10:00",
                    "tweet": tweets[0],
                    "posted": False
                },
                {
                    "time_slot": "11:00-13:00",
                    "tweet": tweets[1],
                    "posted": False
                },
                {
                    "time_slot": "13:00-15:00",
                    "tweet": tweets[2],
                    "posted": False
                },
                {
                    "time_slot": "17:00-19:00",
                    "tweet": tweets[3],
                    "posted": False
                }
            ]
        }

        filename = f"twitter_schedule_{target_date.strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ 调度文件已保存: {filename}")
        return filename, schedule

    def load_or_generate_today_schedule(self):
        """加载或生成今天的调度"""
        today = datetime.now()
        filename = f"twitter_schedule_{today.strftime('%Y%m%d')}.json"

        # 检查今天的调度文件是否存在
        if os.path.exists(filename):
            logger.info(f"📖 加载已有调度文件: {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                schedule = json.load(f)
            return filename, schedule
        else:
            logger.info(f"🆕 未找到今日调度，生成新的...")
            return self.generate_daily_schedule(today)

    def save_schedule(self, filename, schedule):
        """保存调度文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

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

    def shorten_tweet(self, original_tweet):
        """生成更短的tweet版本"""
        logger.info("🔄 生成更短的tweet版本...")

        prompt = f"""The following tweet is too long for Twitter. Create a shorter version (max 260 characters) that:
1. Keeps the SAME core message and insight
2. MUST include "HireMeAI"
3. MUST include the URL: https://interviewasssistant.com
4. Use concise language, remove unnecessary words
5. Keep it engaging and authentic

Original tweet:
{original_tweet}

Output ONLY the shortened tweet text, nothing else:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )

        shortened = response.choices[0].message.content.strip()

        # 确保包含URL
        if 'https://interviewasssistant.com' not in shortened:
            shortened += " https://interviewasssistant.com"

        logger.info(f"   ✅ 缩短后: {len(shortened)} 字符")
        logger.info(f"   内容: {shortened[:100]}...")
        return shortened

    def post_single_tweet(self, tweet_text, retry_with_shorter=True):
        """发布单条tweet，失败时自动尝试更短版本"""
        try:
            if not self.poster:
                self.poster = TwitterPoster()
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    raise Exception("Twitter登录验证失败")

            # 检查字符长度
            if len(tweet_text) > 280:
                logger.warning(f"⚠️  Tweet过长 ({len(tweet_text)} 字符)，生成更短版本...")
                tweet_text = self.shorten_tweet(tweet_text)

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
                # 发布失败，如果还没尝试过缩短，尝试缩短版本
                if retry_with_shorter and len(tweet_text) > 200:
                    logger.warning("❌ 发布失败，可能是字符限额问题，尝试更短版本...")
                    shorter_tweet = self.shorten_tweet(tweet_text)
                    return self.post_single_tweet(shorter_tweet, retry_with_shorter=False)
                else:
                    logger.error("❌ Tweet发布失败")
                    return False

        except Exception as e:
            error_msg = str(e).lower()
            # 检测是否是字符限额错误
            if retry_with_shorter and ('character' in error_msg or 'length' in error_msg or len(tweet_text) > 280):
                logger.warning(f"❌ 发布错误（可能是字符限额），尝试更短版本: {str(e)}")
                shorter_tweet = self.shorten_tweet(tweet_text)
                return self.post_single_tweet(shorter_tweet, retry_with_shorter=False)
            else:
                logger.error(f"❌ 发布错误: {str(e)}")
                return False

    def run_today_schedule(self, filename, schedule):
        """运行今天的调度"""
        logger.info("\n📋 今日调度:")
        for item in schedule['schedule']:
            status = "✅ 已发布" if item['posted'] else "⏳ 待发布"
            logger.info(f"   {item['time_slot']}: {status}")
            logger.info(f"      {item['tweet'][:80]}...")

        logger.info("\n⏰ 开始监控，将在指定时间段自动发布...")

        while True:
            now = datetime.now()

            # 检查是否已经到了第二天
            today_str = now.strftime('%Y%m%d')
            expected_filename = f"twitter_schedule_{today_str}.json"
            if filename != expected_filename:
                logger.info("\n" + "=" * 80)
                logger.info("📅 已进入新的一天，退出当前调度...")
                logger.info("=" * 80)
                break

            # 检查每个时间段
            for item in schedule['schedule']:
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
                        self.save_schedule(filename, schedule)
                        logger.info("✅ 状态已保存")

                    # 发布后等待，避免重复发布
                    time.sleep(60)

            # 检查是否所有都已发布
            all_posted = all(item['posted'] for item in schedule['schedule'])
            if all_posted:
                logger.info("\n" + "=" * 80)
                logger.info("🎉 今日所有tweets已发布完成！")
                logger.info("=" * 80)
                break

            # 每分钟检查一次
            time.sleep(60)

    def run_forever(self):
        """永久运行"""
        logger.info("=" * 80)
        logger.info("🚀 Twitter自动发布系统 - 永久运行模式")
        logger.info("=" * 80)
        logger.info("功能:")
        logger.info("  • 每天自动生成4条Build in Public风格tweets")
        logger.info("  • 在指定时间段自动发布 (09:00, 11:00, 13:00, 17:00)")
        logger.info("  • 当天发布完成后自动生成第二天的内容")
        logger.info("  • 无需人工干预，永久运行")
        logger.info("=" * 80)
        logger.info("按Ctrl+C停止\n")

        try:
            while True:
                # 加载或生成今天的调度
                filename, schedule = self.load_or_generate_today_schedule()

                # 运行今天的调度
                self.run_today_schedule(filename, schedule)

                # 今天发完了，等待到第二天凌晨
                now = datetime.now()
                tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                wait_seconds = (tomorrow - now).total_seconds()

                logger.info(f"\n⏳ 今日任务完成，等待 {wait_seconds/3600:.1f} 小时到第二天...")
                logger.info(f"   将在 {tomorrow.strftime('%Y-%m-%d %H:%M:%S')} 生成新的tweets\n")

                time.sleep(wait_seconds + 60)  # 多等1分钟确保进入新的一天

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断...")
        finally:
            if self.poster:
                logger.info("🔒 关闭浏览器...")
                try:
                    self.poster.close_browser()
                except Exception as e:
                    # 忽略浏览器关闭时的连接错误（通常是浏览器已经关闭）
                    if "Connection closed" not in str(e):
                        logger.warning(f"⚠️  关闭浏览器时出现错误（已忽略）: {str(e)}")

            logger.info("\n✅ 系统已停止")

if __name__ == "__main__":
    bot = TwitterForeverBot()
    bot.run_forever()
