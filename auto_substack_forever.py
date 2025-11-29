#!/usr/bin/env python3
"""
Substack自动发布与回答系统 - 永久运行版

功能：
1. 每周自动生成1篇Build in Public风格的Substack文章
2. 自动发布到Substack
3. 监控已发布文章的评论，自动生成并发布回答
4. 回答风格：简短、热情、不推销、可用网络用语

运行模式：
- 周一发布新文章
- 每天2次检查评论（上午10点、下午4点）
- 永久运行，无需人工干预
"""
import sys
sys.path.insert(0, 'src')
from substack_poster import SubstackPoster
from substack_answer_bot import SubstackAnswerBot
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

# ==================== 配置区 ====================
SUBSTACK_DOMAIN = "yourname.substack.com"  # 替换为你的Substack域名
PUBLISH_DAY = 0  # 周一发布（0=周一, 1=周二...6=周日）
PUBLISH_HOUR = 9  # 早上9点发布
COMMENT_CHECK_HOURS = [10, 16]  # 每天10点和16点检查评论
MAX_REPLIES_PER_CHECK = 5  # 每次检查最多回复5条评论
# ===============================================


class SubstackForeverBot:
    def __init__(self):
        self.poster = None
        self.answer_bot = None
        self.published_articles = self._load_published_articles()

    def _load_published_articles(self) -> list:
        """加载已发布的文章列表"""
        try:
            with open('substack_published_articles.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_published_articles(self):
        """保存已发布的文章列表"""
        with open('substack_published_articles.json', 'w') as f:
            json.dump(self.published_articles, f, indent=2)

    def generate_substack_article(self, week_number: int) -> dict:
        """
        生成单篇Substack文章 - 采用用户提供的高转化率格式

        Args:
            week_number: 第几周

        Returns:
            文章内容字典
        """
        logger.info(f"📝 生成第 {week_number} 周的 Build in Public 文章...")

        prompt = f"""You are building HireMeAI (即答侠 - https://interviewasssistant.com) in public on Substack.

Generate a high-quality Substack article for Week {week_number} following this proven structure:

**TITLE FORMAT** (Attention + Value + Solution Hint):
- ✅ "Week {week_number}: Teaching AI How to Handle 'Tell Me About Yourself'"
- ✅ "Why 90% of Candidates Fail Behavioral Interviews (and How AI Can Help)"
- ✅ "Building HireMeAI: The Speaker Recognition Breakthrough"

**ARTICLE STRUCTURE** (800-1200 words):

1️⃣ **Hook Opening** (1-2 paragraphs)
   - Start with a compelling personal story or data point
   - Build credibility through experience
   - Example: "I've analyzed 500+ failed interviews. Here's the pattern..."

2️⃣ **The Problem** (2-3 paragraphs)
   - Identify the specific pain point
   - Use data or real examples
   - Make readers feel understood

3️⃣ **The Insight/Solution** (3-4 paragraphs)
   - Share your technical discovery or approach
   - Include specific numbers/metrics
   - Behind-the-scenes of HireMeAI development
   - Example: "This week we achieved 92% speaker identification accuracy using Picovoice Eagle..."

4️⃣ **Case/Example** (2 paragraphs)
   - Real test scenario or user feedback
   - Specific outcome or learning
   - Make it tangible

5️⃣ **Takeaway** (1-2 paragraphs)
   - Elevate to broader insight
   - Thought-provoking reflection
   - Example: "Good interviews are less about words and more about awareness..."

6️⃣ **Call to Action**
   - Natural next step
   - "Try the beta at https://interviewasssistant.com"
   - "Questions? Email liu.lucian6@gmail.com"

**TONE & STYLE**:
- Write in ENGLISH
- Conversational but professional
- Use 1-2 emojis (sparingly)
- Short paragraphs (2-4 sentences)
- Include specific metrics/data
- Build in public transparency

**TOPICS TO COVER** (choose one that fits Week {week_number}):
- Technical breakthroughs (speaker ID, voice recognition, latency optimization)
- User feedback & insights
- Interview psychology & preparation strategies
- AI application in career development
- Product iteration decisions
- Startup failures & learnings
- Real interview scenarios

Output format (JSON):
{{
    "title": "Week {week_number}: The Title Here",
    "subtitle": "Short engaging subtitle",
    "content": "Full article content in markdown format...",
    "cta": "Try HireMeAI at https://interviewasssistant.com"
}}

Output ONLY valid JSON, no extra text:"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=2000
            )

            article_json = response.choices[0].message.content.strip()

            # 移除可能的markdown代码块标记
            if article_json.startswith('```json'):
                article_json = article_json[7:]
            if article_json.startswith('```'):
                article_json = article_json[3:]
            if article_json.endswith('```'):
                article_json = article_json[:-3]

            article = json.loads(article_json.strip())

            logger.info(f"   ✅ 文章已生成")
            logger.info(f"      标题: {article['title']}")
            logger.info(f"      字数: {len(article['content'])} 字符")

            return article

        except Exception as e:
            logger.error(f"   ❌ 生成文章失败: {str(e)}")
            return None

    def publish_article(self, article: dict) -> bool:
        """
        发布文章到Substack

        Args:
            article: 文章内容

        Returns:
            是否成功
        """
        logger.info(f"📤 发布文章: {article['title']}")

        try:
            if not self.poster:
                self.poster = SubstackPoster(substack_url=SUBSTACK_DOMAIN)
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    raise Exception("Substack登录验证失败")

            # 构造发布内容
            content = {
                'title': article['title'],
                'subtitle': article.get('subtitle', ''),
                'content': article['content'],
                'publish_immediately': True
            }

            success = self.poster.create_post(content)

            if success:
                # 记录已发布的文章
                article_record = {
                    'title': article['title'],
                    'published_at': datetime.now().isoformat(),
                    'url': f"https://{SUBSTACK_DOMAIN}/p/{article['title'].lower().replace(' ', '-')[:50]}"
                }
                self.published_articles.append(article_record)
                self._save_published_articles()

                logger.info(f"✅ 文章发布成功！")
                return True
            else:
                logger.error(f"❌ 文章发布失败")
                return False

        except Exception as e:
            logger.error(f"❌ 发布错误: {str(e)}")
            return False

    def check_and_reply_comments(self):
        """检查并回复评论"""
        logger.info("\n" + "=" * 80)
        logger.info("💬 开始检查评论...")
        logger.info("=" * 80)

        if not self.published_articles:
            logger.info("   ℹ️  暂无已发布文章")
            return

        # 只检查最近的3篇文章
        recent_articles = self.published_articles[-3:]
        logger.info(f"   📖 检查最近 {len(recent_articles)} 篇文章的评论")

        for article in recent_articles:
            logger.info(f"\n检查文章: {article['title']}")
            logger.info(f"URL: {article['url']}")

            try:
                if not self.answer_bot:
                    self.answer_bot = SubstackAnswerBot(substack_url=SUBSTACK_DOMAIN)
                    self.answer_bot.setup_browser(headless=False)

                    if not self.answer_bot.verify_login():
                        raise Exception("Substack登录验证失败")

                # 运行回答机器人
                self.answer_bot.run_on_article(article['url'], max_replies=MAX_REPLIES_PER_CHECK)

                # 文章间延迟
                time.sleep(random.randint(60, 120))

            except Exception as e:
                logger.error(f"   ❌ 处理文章评论失败: {str(e)}")
                continue

        logger.info("\n✅ 评论检查完成")

    def should_publish_today(self) -> bool:
        """检查今天是否应该发布新文章"""
        now = datetime.now()
        return now.weekday() == PUBLISH_DAY

    def should_check_comments_now(self) -> bool:
        """检查现在是否应该检查评论"""
        now = datetime.now()
        return now.hour in COMMENT_CHECK_HOURS

    def get_week_number(self) -> int:
        """获取当前是第几周（从项目开始计算）"""
        # 假设从2025年1月1日开始
        start_date = datetime(2025, 1, 1)
        now = datetime.now()
        weeks = (now - start_date).days // 7 + 1
        return weeks

    def run_forever(self):
        """永久运行"""
        logger.info("=" * 80)
        logger.info("🚀 Substack自动发布与回答系统 - 永久运行模式")
        logger.info("=" * 80)
        logger.info("功能:")
        logger.info(f"  • 每周{['一', '二', '三', '四', '五', '六', '日'][PUBLISH_DAY]}自动生成并发布Build in Public文章")
        logger.info(f"  • 每天{COMMENT_CHECK_HOURS}点检查评论并自动回复")
        logger.info(f"  • 回复风格：简短、热情、不推销、可用网络用语")
        logger.info(f"  • 域名: {SUBSTACK_DOMAIN}")
        logger.info("=" * 80)
        logger.info("按Ctrl+C停止\n")

        last_publish_date = None
        last_comment_check_hour = None

        try:
            while True:
                now = datetime.now()

                # 检查是否应该发布新文章
                if self.should_publish_today():
                    today_str = now.strftime('%Y-%m-%d')

                    # 确保今天还没发布过
                    if last_publish_date != today_str and now.hour == PUBLISH_HOUR:
                        logger.info(f"\n{'='*80}")
                        logger.info(f"📅 发布日到！开始生成本周文章...")
                        logger.info(f"{'='*80}")

                        week_number = self.get_week_number()
                        article = self.generate_substack_article(week_number)

                        if article:
                            success = self.publish_article(article)
                            if success:
                                last_publish_date = today_str
                                logger.info("✅ 本周文章已发布")
                            else:
                                logger.error("❌ 发布失败，将在下次检查时重试")
                        else:
                            logger.error("❌ 生成文章失败")

                        # 发布后等待，避免重复
                        time.sleep(3600)  # 1小时

                # 检查是否应该检查评论
                current_hour = now.hour
                if self.should_check_comments_now() and last_comment_check_hour != current_hour:
                    logger.info(f"\n{'='*80}")
                    logger.info(f"⏰ 评论检查时间到！")
                    logger.info(f"{'='*80}")

                    self.check_and_reply_comments()
                    last_comment_check_hour = current_hour

                    # 检查后等待，避免重复
                    time.sleep(3600)  # 1小时

                # 每10分钟检查一次
                time.sleep(600)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断...")
        finally:
            logger.info("🔒 关闭浏览器...")
            if self.poster:
                try:
                    self.poster.close_browser()
                except Exception as e:
                    if "Connection closed" not in str(e):
                        logger.warning(f"⚠️  关闭poster浏览器时出现错误: {str(e)}")

            if self.answer_bot:
                try:
                    self.answer_bot.close_browser()
                except Exception as e:
                    if "Connection closed" not in str(e):
                        logger.warning(f"⚠️  关闭answer_bot浏览器时出现错误: {str(e)}")

            logger.info("\n✅ 系统已停止")


def generate_weekly_article_now():
    """
    立即生成并发布一篇文章（测试用）
    """
    logger.info("🧪 测试模式：立即生成并发布文章")

    bot = SubstackForeverBot()
    week_number = bot.get_week_number()

    article = bot.generate_substack_article(week_number)

    if article:
        logger.info("\n生成的文章：")
        logger.info(f"标题: {article['title']}")
        logger.info(f"副标题: {article.get('subtitle', '')}")
        logger.info(f"字数: {len(article['content'])} 字符")
        logger.info("\n" + "="*80)
        logger.info(article['content'][:500] + "...")
        logger.info("="*80)

        # 询问是否发布
        response = input("\n是否发布到Substack？(y/n): ")
        if response.lower() == 'y':
            success = bot.publish_article(article)
            if success:
                logger.info("✅ 发布成功！")
            else:
                logger.error("❌ 发布失败")
    else:
        logger.error("❌ 生成文章失败")


def check_comments_now():
    """
    立即检查并回复评论（测试用）
    """
    logger.info("🧪 测试模式：立即检查评论")

    bot = SubstackForeverBot()
    bot.check_and_reply_comments()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Substack自动发布与回答系统')
    parser.add_argument('--mode', choices=['forever', 'generate', 'comments'],
                       default='forever',
                       help='运行模式：forever=永久运行, generate=生成并发布文章, comments=检查评论')

    args = parser.parse_args()

    if args.mode == 'forever':
        bot = SubstackForeverBot()
        bot.run_forever()
    elif args.mode == 'generate':
        generate_weekly_article_now()
    elif args.mode == 'comments':
        check_comments_now()
