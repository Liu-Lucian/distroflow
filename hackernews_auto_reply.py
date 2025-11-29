#!/usr/bin/env python3
"""
Hacker News 自动技术回答系统
使用 Claude API (Anthropic) 生成高质量技术评论
参考 auto_twitter_forever.py 的调度架构

运行方式：
1. 先设置 API key: export ANTHROPIC_API_KEY='sk-ant-api03-...'
2. 运行一次登录: python3 hackernews_login_and_save_auth.py
3. 启动自动化: python3 hackernews_auto_reply.py
"""
import sys
sys.path.insert(0, 'src')

from hackernews_commenter import HackerNewsCommenter
import os
import json
import time
import logging
from datetime import datetime, timedelta
import random
from anthropic import Anthropic

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Claude API
client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

class HackerNewsAutoReplier:
    def __init__(self):
        self.commenter = None
        self.schedule_dir = "schedules"

        # 创建 schedules 目录
        os.makedirs(self.schedule_dir, exist_ok=True)

    def generate_technical_comment(self, story_title: str, story_url: str, story_context: str = "") -> str:
        """
        使用 Claude API 生成技术性评论

        Args:
            story_title: HN 帖子标题
            story_url: HN 帖子链接 (用于获取更多上下文)
            story_context: 帖子的额外上下文信息

        Returns:
            str: 生成的评论文本
        """
        logger.info(f"🤖 使用 Claude 生成评论: {story_title[:60]}...")

        prompt = f"""You are the technical founder of HireMeAI (即答侠), an AI-powered interview assistant (https://interviewasssistant.com).

You are commenting on this Hacker News story:
Title: {story_title}
URL: {story_url}

Generate a GENUINE, TECHNICALLY VALUABLE comment for Hacker News:

CRITICAL REQUIREMENTS:
1. **Technical Depth** - Share concrete experience, code insights, or architectural decisions
   - Include actual numbers, metrics, or technical details
   - Example: "We reduced latency by 60% by switching from polling to WebSockets"

2. **Specificity** - Be precise and detailed
   - Don't use vague language like "interesting" or "great post"
   - Share real implementation challenges and solutions

3. **Add Value** - Provide perspective that helps other builders
   - Share lessons learned, gotchas, or best practices
   - Offer concrete advice or ask thoughtful technical questions

4. **Natural Product Mention** - Reference HireMeAI ONLY if genuinely relevant
   - Never force a product mention - authenticity is key
   - If relevant: "When building our AI interview assistant, we faced similar..."
   - If not relevant: Skip product mention entirely

5. **Conversational Tone** - Sound like a real engineer, not a marketer
   - Use first person ("We", "I")
   - Be humble and curious
   - Ask questions if appropriate

6. **HN Community Standards**:
   - NO marketing language
   - NO generic praise ("great post!", "thanks for sharing!")
   - NO self-promotion disguised as contribution
   - Focus on TECHNICAL SUBSTANCE

7. **Length**: 2-4 short paragraphs (50-150 words total)

GOOD EXAMPLES:
✅ "We hit this exact issue when building real-time feedback for interviews. The key was switching from REST polling (200ms latency) to WebSockets with delta updates. Reduced bandwidth by 80% and made the UX feel instant. The tricky part was handling reconnections gracefully - we ended up using a sliding window buffer."

✅ "Interesting approach with the sliding window. One gotcha we discovered: when users have flaky connections (common on mobile), you need exponential backoff + jitter on reconnects. Otherwise you get thundering herd problems. Have you considered using QUIC instead of TCP for the transport layer?"

BAD EXAMPLES:
❌ "Great post! Really interesting insights. Check out HireMeAI if you need interview help!"
❌ "This is exactly what we're doing at HireMeAI. Visit our site to learn more."
❌ "Thanks for sharing! Very relevant to my work."

OUTPUT ONLY THE COMMENT TEXT (no meta-commentary, no "Here's a comment:", just the raw comment):"""

        try:
            # 调用 Claude API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # 最新 Claude Sonnet
                max_tokens=500,
                temperature=0.8,  # 适度随机性，保持真实感
                messages=[{"role": "user", "content": prompt}]
            )

            comment = message.content[0].text.strip()

            logger.info(f"   ✅ 生成成功 ({len(comment)} 字符)")
            logger.info(f"   预览: {comment[:100]}...")

            return comment

        except Exception as e:
            logger.error(f"   ❌ Claude API 调用失败: {str(e)}")
            return ""

    def select_stories_to_comment(self, stories: list, count: int = 3) -> list:
        """
        选择值得评论的帖子

        策略：
        1. 优先选择有一定讨论度的帖子 (有评论但不太多)
        2. 避开新闻类、政治类帖子
        3. 优先选择技术讨论、Show HN、Ask HN
        4. 分数在 50-500 之间的帖子 (不太新，不太老)

        Args:
            stories: 帖子列表
            count: 要选择的帖子数量

        Returns:
            list: 选中的帖子
        """
        logger.info(f"📊 从 {len(stories)} 个帖子中选择 {count} 个...")

        # 过滤策略
        filtered = []
        for story in stories:
            title = story['title'].lower()
            points = story['points']
            comments = story['comments']

            # 跳过的条件
            skip = False

            # 1. 跳过没有评论的帖子
            if comments == 0:
                skip = True

            # 2. 跳过评论太多的热门帖子 (难以获得可见性)
            if comments > 200:
                skip = True

            # 3. 跳过分数太低的帖子
            if points < 10:
                skip = True

            # 4. 跳过分数太高的超热门帖子 (已经过了冷启动期)
            if points > 500:
                skip = True

            # 5. 优先选择技术相关的帖子
            tech_keywords = [
                'api', 'framework', 'library', 'algorithm', 'database',
                'performance', 'scale', 'architecture', 'code', 'programming',
                'ai', 'ml', 'llm', 'gpt', 'claude', 'model',
                'show hn', 'ask hn', 'interview', 'hiring', 'career',
                'startup', 'build', 'launch', 'product'
            ]

            has_tech_keyword = any(kw in title for kw in tech_keywords)

            if not skip and has_tech_keyword:
                filtered.append(story)
            elif not skip and len(filtered) < count * 2:  # 如果不够，也加入非关键词的
                filtered.append(story)

        # 排序：优先选择有一定讨论但不太热的帖子
        # 排序策略: comments / (points + 10)
        # 这样可以找到"讨论热度相对较高"的帖子
        filtered.sort(key=lambda s: s['comments'] / (s['points'] + 10), reverse=True)

        selected = filtered[:count]

        logger.info(f"   ✅ 已选择 {len(selected)} 个帖子:")
        for i, story in enumerate(selected, 1):
            logger.info(f"      {i}. {story['title'][:60]}... (👍 {story['points']}, 💬 {story['comments']})")

        return selected

    def generate_daily_schedule(self, target_date=None):
        """
        生成当日评论计划

        参考 auto_twitter_forever.py 的 generate_daily_schedule()
        但针对 HN 特点调整：
        - 每天 2-3 条评论（而不是 4 条推文）
        - 时间段：上午 09:00-11:00, 下午 14:00-16:00, 晚上 19:00-21:00
        - 评论对象从首页帖子中智能选择

        Returns:
            tuple: (filename, schedule)
        """
        if target_date is None:
            target_date = datetime.now()

        date_str = target_date.strftime('%Y-%m-%d')
        filename = f"{self.schedule_dir}/hackernews_schedule_{date_str}.json"

        logger.info("=" * 80)
        logger.info(f"📅 生成 {date_str} 的 HN 评论计划")
        logger.info("=" * 80)

        # 初始化 commenter
        if self.commenter is None:
            self.commenter = HackerNewsCommenter()
            self.commenter.setup_browser(headless=True)

            # 验证登录
            if not self.commenter.verify_login():
                logger.error("❌ HN 登录验证失败，请先运行: python3 hackernews_login_and_save_auth.py")
                return None, None

        # 获取首页帖子
        logger.info("📰 获取 HN 首页帖子...")
        stories = self.commenter.get_frontpage_stories(limit=30)

        if not stories:
            logger.error("❌ 获取首页帖子失败")
            return None, None

        logger.info(f"   ✅ 获取到 {len(stories)} 个帖子")

        # 选择 3 个值得评论的帖子
        selected_stories = self.select_stories_to_comment(stories, count=3)

        if not selected_stories:
            logger.error("❌ 没有找到合适的帖子")
            return None, None

        # 为每个帖子生成评论
        schedule = {
            "generated_at": datetime.now().isoformat(),
            "date": date_str,
            "schedule": []
        }

        # 时间段定义
        time_slots = [
            ("09:00-11:00", 9, 11),   # 上午
            ("14:00-16:00", 14, 16),  # 下午
            ("19:00-21:00", 19, 21),  # 晚上
        ]

        for i, story in enumerate(selected_stories):
            time_slot_name, start_hour, end_hour = time_slots[i]

            logger.info(f"\n📝 为帖子 {i+1} 生成评论...")
            logger.info(f"   标题: {story['title'][:70]}...")
            logger.info(f"   链接: {story['url']}")

            # 使用 Claude 生成评论
            comment = self.generate_technical_comment(
                story_title=story['title'],
                story_url=story['url']
            )

            if not comment:
                logger.warning(f"   ⚠️  评论生成失败，跳过此帖子")
                continue

            # 随机选择时间段内的具体时间
            random_hour = random.randint(start_hour, end_hour - 1)
            random_minute = random.randint(0, 59)

            schedule_item = {
                "time_slot": time_slot_name,
                "scheduled_time": f"{random_hour:02d}:{random_minute:02d}",
                "story": {
                    "id": story['id'],
                    "title": story['title'],
                    "url": story['url'],
                    "points": story['points'],
                    "comments": story['comments']
                },
                "comment": comment,
                "posted": False
            }

            schedule["schedule"].append(schedule_item)

        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

        logger.info("\n" + "=" * 80)
        logger.info(f"✅ 评论计划已生成: {filename}")
        logger.info(f"   共 {len(schedule['schedule'])} 条评论")
        for i, item in enumerate(schedule['schedule'], 1):
            logger.info(f"   {i}. {item['time_slot']} - {item['story']['title'][:50]}...")
        logger.info("=" * 80)

        return filename, schedule

    def load_or_generate_today_schedule(self):
        """
        加载或生成今日计划

        参考 auto_twitter_forever.py 的同名函数
        """
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        filename = f"{self.schedule_dir}/hackernews_schedule_{date_str}.json"

        # 如果今日计划已存在，加载它
        if os.path.exists(filename):
            logger.info(f"📂 加载现有计划: {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                schedule = json.load(f)
            return filename, schedule

        # 否则生成新计划
        return self.generate_daily_schedule(today)

    def run_today_schedule(self, filename: str, schedule: dict):
        """
        执行今日评论计划

        参考 auto_twitter_forever.py 的同名函数
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"🚀 开始执行今日计划: {schedule['date']}")
        logger.info("=" * 80)

        # 初始化 commenter (如果还没初始化)
        if self.commenter is None:
            self.commenter = HackerNewsCommenter()
            self.commenter.setup_browser(headless=False)  # 非 headless 方便调试

            if not self.commenter.verify_login():
                logger.error("❌ HN 登录验证失败")
                return

        while True:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")

            # 检查是否已经到了第二天
            if current_time.strftime('%Y-%m-%d') != schedule['date']:
                logger.info("\n✅ 今日计划已完成，准备生成明日计划...")
                break

            # 查找当前时间段内需要发布的评论
            posted_any = False

            for item in schedule['schedule']:
                if item['posted']:
                    continue

                scheduled_time = item['scheduled_time']

                # 检查是否到了发布时间
                if current_time_str >= scheduled_time:
                    logger.info("\n" + "-" * 80)
                    logger.info(f"⏰ 时间到: {scheduled_time}")
                    logger.info(f"📝 准备评论: {item['story']['title'][:60]}...")
                    logger.info("-" * 80)

                    # 发布评论
                    success = self.commenter.post_comment(
                        story_url=item['story']['url'],
                        comment_text=item['comment']
                    )

                    if success:
                        logger.info("   ✅ 评论发布成功!")
                        item['posted'] = True
                        posted_any = True

                        # 保存更新后的计划
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(schedule, f, ensure_ascii=False, indent=2)

                        # 随机延迟 3-8 分钟（模拟人类行为）
                        delay = random.randint(180, 480)
                        logger.info(f"   ⏳ 等待 {delay//60} 分钟后继续...")
                        time.sleep(delay)
                    else:
                        logger.error("   ❌ 评论发布失败")

            # 检查是否所有评论都已发布
            all_posted = all(item['posted'] for item in schedule['schedule'])
            if all_posted:
                logger.info("\n" + "=" * 80)
                logger.info("✅ 今日所有评论已发布完成!")
                logger.info("   等待明日...")
                logger.info("=" * 80)

                # 等待到第二天
                tomorrow = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                wait_seconds = (tomorrow - current_time).total_seconds()
                logger.info(f"⏳ 将在 {wait_seconds//3600} 小时后生成明日计划")
                time.sleep(wait_seconds)
                break

            # 如果这一轮没有发布任何评论，等待 5 分钟后再检查
            if not posted_any:
                logger.info(f"⏳ 当前时间 {current_time_str}，等待下一个时间段...")
                time.sleep(300)  # 5 分钟

    def run_forever(self):
        """
        永久运行模式

        参考 auto_twitter_forever.py 的同名函数
        每天：
        1. 加载或生成今日计划
        2. 执行计划
        3. 等待到第二天
        4. 重复
        """
        logger.info("\n" + "=" * 80)
        logger.info("🤖 Hacker News 自动评论系统启动")
        logger.info("=" * 80)
        logger.info("模式: 永久运行")
        logger.info("频率: 每天 2-3 条技术评论")
        logger.info("AI: Claude (Anthropic)")
        logger.info("=" * 80)

        try:
            while True:
                # 加载或生成今日计划
                filename, schedule = self.load_or_generate_today_schedule()

                if filename is None or schedule is None:
                    logger.error("❌ 无法生成计划，60秒后重试...")
                    time.sleep(60)
                    continue

                # 执行今日计划
                self.run_today_schedule(filename, schedule)

                # 循环会在执行完今日计划后继续，生成明日计划

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断，正在关闭...")
        except Exception as e:
            logger.error(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.commenter:
                self.commenter.close_browser()
            logger.info("\n✅ 系统已关闭")


if __name__ == "__main__":
    # 检查 API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ 错误: 未设置 ANTHROPIC_API_KEY")
        print("\n请先设置 API key:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'")
        print("\n然后再运行此脚本")
        exit(1)

    # 创建并运行
    replier = HackerNewsAutoReplier()
    replier.run_forever()
