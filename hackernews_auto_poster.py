#!/usr/bin/env python3
"""
Hacker News 自动发帖系统
使用 Claude API 生成真诚的技术分享帖子

发帖策略:
- 每月 1 次 Show HN (产品展示)
- 每周 1 次 Ask HN (技术讨论)
- 语气轻松、真诚、技术导向
- 避免直接推销，分享经验为主

运行: python3 hackernews_auto_poster.py
"""
import sys
sys.path.insert(0, 'src')

from hackernews_poster import HackerNewsPoster
import os
import json
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
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

class HackerNewsAutoPoster:
    def __init__(self):
        self.poster = None
        self.schedule_dir = "schedules"
        self.product_url = "https://interviewasssistant.com"
        self.product_name = "HireMeAI (即答侠)"

        # 创建 schedules 目录
        os.makedirs(self.schedule_dir, exist_ok=True)

    def generate_show_hn_post(self) -> Dict:
        """
        生成 Show HN 帖子（每月1次）
        展示产品，但要像分享 side project，不要推销
        """
        logger.info("🚀 生成 Show HN 帖子...")

        # 读取产品介绍
        try:
            with open('产品介绍.md', 'r', encoding='utf-8') as f:
                product_intro = f.read()
        except:
            product_intro = "AI面试实时辅助系统"

        prompt = f"""You are a technical founder building HireMeAI, an AI interview assistant.

Generate a "Show HN" post that shares your project on Hacker News.

Product context:
{product_intro[:1500]}

CRITICAL REQUIREMENTS:
1. **Tone**: Casual, technical founder vibe (use lol, tbh, ngl, imo naturally)
2. **Authenticity**: Sound like you're sharing a side project, NOT selling a product
3. **Technical Focus**: Share interesting engineering challenges you solved
4. **HN Community Standards**:
   - NO marketing language
   - NO "try it now", "sign up", "best tool ever"
   - YES technical details, honest reflections, asking for feedback
5. **Format**: Title + Body (2-4 paragraphs)

GOOD EXAMPLES (HN style):
✅ "Show HN: Real-time AI interview coach (tbh the latency was a nightmare)"
✅ "Show HN: Interview assistant using GPT-4o + Azure Speech (feedback welcome)"

BAD EXAMPLES:
❌ "Show HN: The Best AI Interview Tool You'll Ever Use!"
❌ "Show HN: Revolutionary Interview Platform - Try Now!"

Key technical highlights to mention (pick 2-3):
- Reduced first-byte latency from 2.7s → 1.0s (60% improvement)
- Real-time speaker recognition (Picovoice Eagle)
- Vector similarity search for answer matching (ChromaDB)
- Dual-level caching architecture

Body should:
- Start with honest context (e.g., "Been working on this for X months...")
- Share 1-2 technical challenges (e.g., "the hardest part was...")
- Mention specific stack/metrics
- Ask for feedback genuinely
- Maybe mention product URL casually at end

Output format (JSON):
{{
  "title": "Show HN: ...",
  "url": "{self.product_url}",
  "text": "Body text here..."
}}

CRITICAL JSON FORMATTING:
- Output ONLY valid JSON (no markdown code fences)
- In the "text" field, use \\n for paragraph breaks (escaped newlines)
- Escape all special characters properly
- Do NOT use actual newlines inside string values

IMPORTANT: Use casual tech founder language. Sound like a real engineer sharing, not a marketer pitching.
"""

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                temperature=0.9,  # Higher temperature for more natural variation
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()

            # Parse JSON response
            # Claude might wrap in ```json, so clean it
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()

            # Try direct parsing first
            try:
                post_data = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract and fix JSON manually
                # Find the JSON object boundaries
                try:
                    # Extract just the JSON part (between first { and last })
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = response[start:end]

                        # Use regex to find and fix unescaped newlines in string values
                        # Match: "key": "value with\nnewlines"
                        def fix_string_value(match):
                            key = match.group(1)
                            value = match.group(2)
                            # Escape newlines and other special chars in the value
                            value = value.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                            return f'"{key}": "{value}"'

                        # Pattern: "key": "value"
                        json_str = re.sub(r'"([^"]+)":\s*"([^"]*(?:\n[^"]*)*)"', fix_string_value, json_str, flags=re.MULTILINE)

                        post_data = json.loads(json_str)
                    else:
                        raise ValueError("Cannot find JSON object in response")
                except Exception as inner_e:
                    logger.error(f"   ⚠️  JSON fix failed: {str(inner_e)}")
                    # Last resort: try simple newline escape
                    fixed_response = response.replace('\n', '\\n')
                    fixed_response = fixed_response.replace('{\\n', '{\n').replace('\\n}', '\n}')
                    fixed_response = fixed_response.replace(',\\n', ',\n')
                    post_data = json.loads(fixed_response)

            logger.info(f"   ✅ Show HN 生成成功")
            logger.info(f"   标题: {post_data['title']}")
            logger.info(f"   正文: {post_data.get('text', '')[:100]}...")

            return post_data

        except Exception as e:
            logger.error(f"   ❌ 生成失败: {str(e)}")
            return None

    def generate_ask_hn_post(self) -> Dict:
        """
        生成 Ask HN 帖子（每周1次）
        提出技术问题，分享经验，邀请讨论
        """
        logger.info("❓ 生成 Ask HN 帖子...")

        # 技术主题池（和产品相关但不直接推销）
        topics = [
            "real-time AI streaming latency optimization",
            "voice recognition in production (speaker diarization)",
            "vector similarity search at scale",
            "reducing GPT API costs with caching",
            "SSE vs WebSockets for AI streaming",
            "building AI tools that feel instant (<1s response)",
            "handling speech recognition accuracy issues",
            "ChromaDB vs other vector databases"
        ]

        selected_topic = random.choice(topics)

        prompt = f"""You are a technical founder working on real-time AI systems (interview assistant specifically).

Generate an "Ask HN" post about this topic: {selected_topic}

CRITICAL REQUIREMENTS:
1. **Tone**: Casual, genuinely curious (use lol, tbh, ngl, imo, glhf naturally)
2. **Purpose**: REAL technical question, not disguised marketing
3. **Share Context**: Briefly mention what you're building, but focus on the technical challenge
4. **HN Community Standards**:
   - Ask genuine questions that help other builders too
   - Share specific numbers/metrics
   - Be humble and curious
   - DON'T pitch your product
5. **Format**: Title + Body (2-4 paragraphs)

GOOD EXAMPLES (Ask HN style):
✅ "Ask HN: How to reduce latency in real-time AI streaming?"
✅ "Ask HN: Best practices for speaker diarization in production?"
✅ "Ask HN: WebSockets vs SSE for AI response streaming?"

BAD EXAMPLES:
❌ "Ask HN: Should you use my product?" (promotional)
❌ "Ask HN: What do you think of this feature?" (vague)

Body structure:
- **Context** (1-2 sentences): "I'm building [brief desc], currently facing [problem]..."
- **Current Approach**: Share what you've tried with specific metrics
- **Specific Question**: What you want advice on
- **Additional Context**: Technical constraints or trade-offs

Example body:
"I'm building a real-time interview assistant and trying to optimize latency (tbh sub-1s first-byte is hard).

Current stack:
- Azure Speech SDK (streaming ASR)
- GPT-4o for responses
- SSE for client updates

We've gotten first-byte down from 2.7s → 1.0s through:
- Precomputing common answers (80% hit rate)
- Dual-level caching (memory + disk)
- Vector similarity search (ChromaDB)

But 1s still feels slow. Anyone hit sub-500ms? Is WebSockets + delta updates worth the complexity?

ngl the hardest part is making it feel instant while maintaining quality. Any advice?"

Output format (JSON):
{{
  "title": "Ask HN: ...",
  "text": "Body text here..."
}}

CRITICAL JSON FORMATTING:
- Output ONLY valid JSON (no markdown code fences)
- In the "text" field, use \\n for paragraph breaks (escaped newlines)
- Escape all special characters properly
- Do NOT use actual newlines inside string values

IMPORTANT: Sound genuinely curious, not promotional. This is a REAL technical question.
"""

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                temperature=0.9,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()

            # Parse JSON
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()

            # Try direct parsing first
            try:
                post_data = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract and fix JSON manually
                # Find the JSON object boundaries
                try:
                    # Extract just the JSON part (between first { and last })
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = response[start:end]

                        # Use regex to find and fix unescaped newlines in string values
                        # Match: "key": "value with\nnewlines"
                        def fix_string_value(match):
                            key = match.group(1)
                            value = match.group(2)
                            # Escape newlines and other special chars in the value
                            value = value.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                            return f'"{key}": "{value}"'

                        # Pattern: "key": "value"
                        json_str = re.sub(r'"([^"]+)":\s*"([^"]*(?:\n[^"]*)*)"', fix_string_value, json_str, flags=re.MULTILINE)

                        post_data = json.loads(json_str)
                    else:
                        raise ValueError("Cannot find JSON object in response")
                except Exception as inner_e:
                    logger.error(f"   ⚠️  JSON fix failed: {str(inner_e)}")
                    # Last resort: try simple newline escape
                    fixed_response = response.replace('\n', '\\n')
                    fixed_response = fixed_response.replace('{\\n', '{\n').replace('\\n}', '\n}')
                    fixed_response = fixed_response.replace(',\\n', ',\n')
                    post_data = json.loads(fixed_response)

            logger.info(f"   ✅ Ask HN 生成成功")
            logger.info(f"   标题: {post_data['title']}")
            logger.info(f"   正文: {post_data.get('text', '')[:100]}...")

            return post_data

        except Exception as e:
            logger.error(f"   ❌ 生成失败: {str(e)}")
            return None

    def generate_monthly_schedule(self, target_month=None):
        """
        生成当月发帖计划
        - 1 个 Show HN (月初)
        - 4 个 Ask HN (每周1次)
        """
        if target_month is None:
            target_month = datetime.now()

        month_str = target_month.strftime('%Y-%m')
        filename = f"{self.schedule_dir}/hackernews_posts_{month_str}.json"

        logger.info("=" * 80)
        logger.info(f"📅 生成 {month_str} 的 HN 发帖计划")
        logger.info("=" * 80)

        schedule = {
            "generated_at": datetime.now().isoformat(),
            "month": month_str,
            "posts": []
        }

        # 1. 生成 1 个 Show HN（月初，第1周）
        logger.info("\n📝 生成 Show HN 帖子...")
        show_hn = self.generate_show_hn_post()

        if show_hn:
            # 随机选择月初某一天 (1-7号)
            post_date = target_month.replace(day=random.randint(1, 7))
            post_time = f"{random.randint(9, 11):02d}:{random.randint(0, 59):02d}"

            schedule["posts"].append({
                "type": "Show HN",
                "scheduled_date": post_date.strftime('%Y-%m-%d'),
                "scheduled_time": post_time,
                "post_data": show_hn,
                "posted": False
            })

        # 2. 生成 4 个 Ask HN（每周1次，周二或周三）
        for week in range(4):
            logger.info(f"\n📝 生成第 {week+1} 周的 Ask HN...")
            ask_hn = self.generate_ask_hn_post()

            if ask_hn:
                # 每周的周二或周三 (day_of_week: 1=Monday, 2=Tuesday, 3=Wednesday)
                week_offset = week * 7
                target_day = target_month.replace(day=1) + timedelta(days=week_offset)

                # 找到该周的周二或周三
                while target_day.weekday() not in [1, 2]:  # 1=Tuesday, 2=Wednesday
                    target_day += timedelta(days=1)

                # 确保不超过当月
                if target_day.month == target_month.month:
                    post_time = f"{random.randint(9, 16):02d}:{random.randint(0, 59):02d}"

                    schedule["posts"].append({
                        "type": "Ask HN",
                        "scheduled_date": target_day.strftime('%Y-%m-%d'),
                        "scheduled_time": post_time,
                        "post_data": ask_hn,
                        "posted": False
                    })

        # 按日期排序
        schedule["posts"].sort(key=lambda x: f"{x['scheduled_date']} {x['scheduled_time']}")

        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

        logger.info("\n" + "=" * 80)
        logger.info(f"✅ 发帖计划已生成: {filename}")
        logger.info(f"   共 {len(schedule['posts'])} 个帖子")
        for i, post in enumerate(schedule['posts'], 1):
            logger.info(f"   {i}. [{post['type']}] {post['scheduled_date']} {post['scheduled_time']} - {post['post_data']['title'][:50]}...")
        logger.info("=" * 80)

        return filename, schedule

    def load_or_generate_current_schedule(self):
        """加载或生成当月计划"""
        current_month = datetime.now()
        month_str = current_month.strftime('%Y-%m')
        filename = f"{self.schedule_dir}/hackernews_posts_{month_str}.json"

        # 如果当月计划已存在，加载它
        if os.path.exists(filename):
            logger.info(f"📂 加载现有计划: {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                schedule = json.load(f)
            return filename, schedule

        # 否则生成新计划
        return self.generate_monthly_schedule(current_month)

    def execute_schedule(self, filename: str, schedule: dict):
        """
        执行发帖计划
        检查是否到了发帖时间，如果是则发帖
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"🚀 开始执行发帖计划: {schedule['month']}")
        logger.info("=" * 80)

        # 初始化 poster
        if self.poster is None:
            self.poster = HackerNewsPoster()
            self.poster.setup_browser(headless=False)  # 非 headless 方便调试

            if not self.poster.verify_login():
                logger.error("❌ HN 登录验证失败")
                return

        while True:
            current_time = datetime.now()
            current_date_str = current_time.strftime("%Y-%m-%d")
            current_time_str = current_time.strftime("%H:%M")

            # 检查是否已经到了下个月
            if current_time.strftime('%Y-%m') != schedule['month']:
                logger.info("\n✅ 当月计划已完成，准备生成下月计划...")
                break

            # 查找当前时间段内需要发布的帖子
            posted_any = False

            for post in schedule['posts']:
                if post['posted']:
                    continue

                scheduled_date = post['scheduled_date']
                scheduled_time = post['scheduled_time']

                # 检查是否到了发布时间
                if current_date_str == scheduled_date and current_time_str >= scheduled_time:
                    logger.info("\n" + "-" * 80)
                    logger.info(f"⏰ 时间到: {scheduled_date} {scheduled_time}")
                    logger.info(f"📝 准备发布: [{post['type']}] {post['post_data']['title'][:60]}...")
                    logger.info("-" * 80)

                    # 发布帖子
                    success = self.poster.submit_post(post['post_data'])

                    if success:
                        logger.info("   ✅ 帖子发布成功!")
                        post['posted'] = True
                        posted_any = True

                        # 保存更新后的计划
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(schedule, f, ensure_ascii=False, indent=2)

                        # 随机延迟 10-20 分钟（HN 发帖不需要太频繁）
                        delay = random.randint(600, 1200)
                        logger.info(f"   ⏳ 等待 {delay//60} 分钟后继续...")
                        time.sleep(delay)
                    else:
                        logger.error("   ❌ 帖子发布失败")

            # 检查是否所有帖子都已发布
            all_posted = all(post['posted'] for post in schedule['posts'])
            if all_posted:
                logger.info("\n" + "=" * 80)
                logger.info("✅ 当月所有帖子已发布完成!")
                logger.info("   等待下个月...")
                logger.info("=" * 80)

                # 等待到下个月
                next_month = (current_time.replace(day=1) + timedelta(days=32)).replace(day=1)
                wait_seconds = (next_month - current_time).total_seconds()
                logger.info(f"⏳ 将在 {wait_seconds//86400} 天后生成下月计划")
                time.sleep(wait_seconds)
                break

            # 如果这一轮没有发布任何帖子，等待 30 分钟后再检查
            if not posted_any:
                logger.info(f"⏳ 当前时间 {current_time_str}，等待下一个时间段...")
                time.sleep(1800)  # 30 分钟

    def run_forever(self):
        """
        永久运行模式
        每月自动生成和执行发帖计划
        """
        logger.info("\n" + "=" * 80)
        logger.info("🤖 Hacker News 自动发帖系统启动")
        logger.info("=" * 80)
        logger.info("模式: 永久运行")
        logger.info("频率: 每月 1 个 Show HN + 4 个 Ask HN")
        logger.info("AI: Claude (Anthropic)")
        logger.info("=" * 80)

        try:
            while True:
                # 加载或生成当月计划
                filename, schedule = self.load_or_generate_current_schedule()

                if filename is None or schedule is None:
                    logger.error("❌ 无法生成计划，60秒后重试...")
                    time.sleep(60)
                    continue

                # 执行当月计划
                self.execute_schedule(filename, schedule)

                # 循环会在执行完当月计划后继续，生成下月计划

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断，正在关闭...")
        except Exception as e:
            logger.error(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.poster:
                self.poster.close_browser()
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
    auto_poster = HackerNewsAutoPoster()

    # 可以选择只生成计划（测试用）
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--generate-only':
        print("\n📝 只生成计划，不执行发帖...")
        filename, schedule = auto_poster.generate_monthly_schedule()
        print(f"\n✅ 计划已生成: {filename}")
        print(f"   共 {len(schedule['posts'])} 个帖子")
        print("\n运行以下命令开始执行:")
        print(f"  python3 {sys.argv[0]}")
    else:
        auto_poster.run_forever()
