#!/usr/bin/env python3
"""
Quora自动回答系统 - 永久运行版
参考 auto_twitter_forever.py 的架构

功能：
1. 每天搜索相关问题
2. AI生成高质量回答
3. 在指定时间段自动发布回答
4. 无需人工干预，永久运行
"""

import sys
sys.path.insert(0, 'src')

from quora_scraper import QuoraScraper
from quora_answer_poster import QuoraAnswerPoster
import os
from openai import OpenAI
import json
import time
import logging
from datetime import datetime, timedelta
import random
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


class QuoraForeverBot:
    """Quora自动回答机器人 - 永久运行模式"""

    def __init__(self):
        self.scraper = None
        self.poster = None
        self.auth_config = None

        # 产品信息配置
        self.product_name = "HireMeAI"
        self.product_url = "https://interviewasssistant.com"
        self.product_description = """AI-powered interview preparation assistant that simulates real interviews and provides instant feedback"""

        # 搜索关键词（可以配置多个）
        self.search_keywords = [
            "job interview preparation",
            "interview tips",
            "how to prepare for interview",
            "AI interview assistant",
            "job interview anxiety",
            "mock interview practice"
        ]

        # 每天回答的问题数量
        self.daily_answers = 3

        # 加载认证
        self._load_auth()

    def _load_auth(self):
        """加载Quora认证信息"""
        try:
            # 尝试从quora_auth.json加载
            if os.path.exists('quora_auth.json'):
                with open('quora_auth.json', 'r', encoding='utf-8') as f:
                    self.auth_config = json.load(f)
                logger.info("✅ 已加载Quora认证信息 (quora_auth.json)")
                return

            # 尝试从platforms_auth.json加载
            if os.path.exists('platforms_auth.json'):
                with open('platforms_auth.json', 'r', encoding='utf-8') as f:
                    platforms_auth = json.load(f)
                    if 'quora' in platforms_auth:
                        self.auth_config = platforms_auth['quora']
                        logger.info("✅ 已加载Quora认证信息 (platforms_auth.json)")
                        return

            logger.warning("⚠️  未找到Quora认证信息，请先运行 quora_login_and_save_auth.py")

        except Exception as e:
            logger.error(f"❌ 加载认证失败: {str(e)}")

    def generate_answer(self, question_text: str) -> str:
        """
        使用AI生成高质量回答

        Args:
            question_text: 问题文本

        Returns:
            生成的回答
        """
        logger.info(f"🤖 生成回答: {question_text[:50]}...")

        prompt = f"""You are an expert helping people with job interview preparation.

Question: {question_text}

Generate a high-quality, helpful answer with these requirements:
1. **Valuable content first** - Provide genuinely useful advice, tips, or insights
2. **Personal experience tone** - Write as if sharing from real experience
3. **Specific and actionable** - Include concrete steps or examples
4. **Natural product mention** - Mention {self.product_name} ({self.product_url}) naturally if relevant, but don't force it
5. **Professional and friendly** - Balance expertise with approachability

Structure:
- Start with a direct, helpful answer
- Provide 2-4 key points with brief explanations
- If relevant, mention {self.product_name} as one helpful tool among others
- Keep it concise (200-400 words)

Style:
✅ "Based on helping hundreds of job seekers, here's what works best..."
✅ "The key mistake most people make is..."
✅ "I've found that [specific technique] makes a huge difference..."

❌ Avoid:
- Pure advertising
- Overly promotional tone
- Generic advice without specifics
- Claims without substance

Output ONLY the answer text, no title or extra formatting:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()

        # 确保包含产品链接（如果回答中提到了产品名）
        if self.product_name in answer and self.product_url not in answer:
            # 找到产品名的位置，添加链接
            answer = answer.replace(
                self.product_name,
                f"{self.product_name} ({self.product_url})",
                1  # 只替换第一次出现
            )

        logger.info(f"   ✅ 回答已生成 ({len(answer)} 字符)")
        return answer

    def search_and_score_questions(self, keywords: str, max_questions: int = 20) -> list:
        """
        搜索并评分问题

        Args:
            keywords: 搜索关键词
            max_questions: 最多搜索多少个问题

        Returns:
            评分后的问题列表（按相关度排序）
        """
        logger.info(f"🔍 搜索问题: '{keywords}'")

        if not self.scraper:
            self.scraper = QuoraScraper(self.auth_config)
            self.scraper.setup_browser(headless=True)

        # 搜索问题
        questions = self.scraper.search_questions(keywords, max_questions=max_questions)

        if not questions:
            logger.warning("   ⚠️  未找到问题")
            return []

        # 简单评分：根据关键词匹配度
        for q in questions:
            score = 0
            question_lower = q['question_text'].lower()

            # 包含核心关键词
            if 'interview' in question_lower:
                score += 3
            if 'job' in question_lower:
                score += 2
            if 'prepare' in question_lower or 'preparation' in question_lower:
                score += 2
            if 'tips' in question_lower or 'advice' in question_lower:
                score += 1

            q['relevance_score'] = score

        # 按评分排序
        questions.sort(key=lambda x: x['relevance_score'], reverse=True)

        logger.info(f"   ✅ 找到 {len(questions)} 个问题，已评分排序")
        return questions

    def generate_daily_schedule(self, target_date=None):
        """
        生成一天的回答调度

        Args:
            target_date: 目标日期

        Returns:
            (filename, schedule)
        """
        if target_date is None:
            target_date = datetime.now()

        logger.info(f"\n📝 生成 {target_date.strftime('%Y-%m-%d')} 的Quora回答调度...")

        # 搜索问题（从多个关键词中随机选择）
        all_questions = []
        keywords_to_use = random.sample(self.search_keywords, min(2, len(self.search_keywords)))

        for keywords in keywords_to_use:
            questions = self.search_and_score_questions(keywords, max_questions=10)
            all_questions.extend(questions)

        # 去重（基于URL）
        seen_urls = set()
        unique_questions = []
        for q in all_questions:
            if q['question_url'] not in seen_urls:
                seen_urls.add(q['question_url'])
                unique_questions.append(q)

        # 按评分排序，选择top N
        unique_questions.sort(key=lambda x: x['relevance_score'], reverse=True)
        selected_questions = unique_questions[:self.daily_answers]

        if len(selected_questions) < self.daily_answers:
            logger.warning(f"   ⚠️  只找到 {len(selected_questions)} 个问题（目标 {self.daily_answers}）")

        # 为每个问题生成回答
        schedule_items = []
        time_slots = ["10:00-11:00", "14:00-15:00", "18:00-19:00"]

        for i, question in enumerate(selected_questions):
            logger.info(f"\n   📄 问题 {i+1}/{len(selected_questions)}:")
            logger.info(f"      {question['question_text'][:80]}...")

            # 生成回答
            answer = self.generate_answer(question['question_text'])

            schedule_items.append({
                "time_slot": time_slots[i] if i < len(time_slots) else f"{10+i*2}:00-{11+i*2}:00",
                "question_text": question['question_text'],
                "question_url": question['question_url'],
                "answer": answer,
                "posted": False
            })

            logger.info(f"      ✅ 回答已生成")
            time.sleep(1)  # 避免API限流

        # 创建调度
        schedule = {
            "generated_at": datetime.now().isoformat(),
            "target_date": target_date.strftime('%Y-%m-%d'),
            "schedule": schedule_items
        }

        # 保存调度文件
        filename = f"quora_schedule_{target_date.strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ 调度文件已保存: {filename}")
        logger.info(f"   共 {len(schedule_items)} 个问题待回答")

        return filename, schedule

    def load_or_generate_today_schedule(self):
        """加载或生成今天的调度"""
        today = datetime.now()
        filename = f"quora_schedule_{today.strftime('%Y%m%d')}.json"

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

        # 解析时间段 "10:00-11:00"
        start_str, end_str = time_slot_str.split('-')
        start_hour, start_min = map(int, start_str.split(':'))
        end_hour, end_min = map(int, end_str.split(':'))

        start_time = datetime.now().replace(hour=start_hour, minute=start_min, second=0).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_min, second=0).time()

        return start_time <= current_time <= end_time

    def post_single_answer(self, question_url: str, answer_text: str) -> bool:
        """
        发布单个回答

        Args:
            question_url: 问题URL
            answer_text: 回答内容

        Returns:
            是否成功
        """
        try:
            if not self.poster:
                self.poster = QuoraAnswerPoster(self.auth_config)
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    raise Exception("Quora登录验证失败")

            success = self.poster.post_answer(question_url, answer_text)

            if success:
                logger.info(f"✅ 回答发布成功！")
                return True
            else:
                logger.error("❌ 回答发布失败")
                return False

        except Exception as e:
            logger.error(f"❌ 发布错误: {str(e)}")
            return False

    def run_today_schedule(self, filename, schedule):
        """运行今天的调度"""
        logger.info("\n📋 今日调度:")
        for item in schedule['schedule']:
            status = "✅ 已发布" if item['posted'] else "⏳ 待发布"
            logger.info(f"   {item['time_slot']}: {status}")
            logger.info(f"      问题: {item['question_text'][:60]}...")

        logger.info("\n⏰ 开始监控，将在指定时间段自动发布...")

        while True:
            now = datetime.now()

            # 检查是否已经到了第二天
            today_str = now.strftime('%Y%m%d')
            expected_filename = f"quora_schedule_{today_str}.json"
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

                    # 在时间段内随机延迟
                    random_delay = random.randint(60, 600)  # 1-10分钟
                    logger.info(f"⏳ 随机延迟 {random_delay//60} 分钟，使发布更自然...")
                    time.sleep(random_delay)

                    logger.info(f"📤 发布回答...")
                    logger.info(f"   问题: {item['question_text'][:80]}...")

                    success = self.post_single_answer(item['question_url'], item['answer'])

                    if success:
                        item['posted'] = True
                        item['posted_at'] = datetime.now().isoformat()
                        self.save_schedule(filename, schedule)
                        logger.info("✅ 状态已保存")

                    # 发布后等待，避免重复
                    time.sleep(60)

            # 检查是否所有都已发布
            all_posted = all(item['posted'] for item in schedule['schedule'])
            if all_posted:
                logger.info("\n" + "=" * 80)
                logger.info("🎉 今日所有回答已发布完成！")
                logger.info("=" * 80)
                break

            # 每分钟检查一次
            time.sleep(60)

    def run_forever(self):
        """永久运行"""
        logger.info("=" * 80)
        logger.info("🚀 Quora自动回答系统 - 永久运行模式")
        logger.info("=" * 80)
        logger.info("功能:")
        logger.info(f"  • 每天自动搜索 {len(self.search_keywords)} 类相关问题")
        logger.info(f"  • 使用AI生成 {self.daily_answers} 个高质量回答")
        logger.info("  • 在指定时间段自动发布 (10:00, 14:00, 18:00)")
        logger.info("  • 无需人工干预，永久运行")
        logger.info("=" * 80)
        logger.info(f"产品: {self.product_name}")
        logger.info(f"链接: {self.product_url}")
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
                logger.info(f"   将在 {tomorrow.strftime('%Y-%m-%d %H:%M:%S')} 生成新的问题和回答\n")

                time.sleep(wait_seconds + 60)  # 多等1分钟确保进入新的一天

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断...")
        finally:
            # 关闭浏览器
            if self.scraper:
                logger.info("🔒 关闭scraper浏览器...")
                try:
                    self.scraper.close_browser()
                except Exception as e:
                    logger.warning(f"⚠️  关闭scraper浏览器时出错: {str(e)}")

            if self.poster:
                logger.info("🔒 关闭poster浏览器...")
                try:
                    self.poster.close_browser()
                except Exception as e:
                    logger.warning(f"⚠️  关闭poster浏览器时出错: {str(e)}")

            logger.info("\n✅ 系统已停止")


if __name__ == "__main__":
    # 检查API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    # 启动机器人
    bot = QuoraForeverBot()
    bot.run_forever()
