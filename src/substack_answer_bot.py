#!/usr/bin/env python3
"""
Substack 自动回答系统
监控Substack文章评论，自动生成并发布有价值的回答

特点：
- 简短、热情但不过分
- 可使用网络用语
- 不直接推销产品
- 回答相关领域问题（面试、AI、职业发展等）
"""

from playwright.sync_api import sync_playwright, Page
import time
import logging
import random
import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubstackAnswerBot:
    """Substack自动回答机器人"""

    def __init__(self, auth_file: str = "substack_auth.json", substack_url: str = None):
        """
        初始化回答机器人

        Args:
            auth_file: 认证文件路径
            substack_url: 你的Substack域名
        """
        self.auth_file = auth_file
        self.substack_url = substack_url
        self.playwright = None
        self.browser = None
        self.page = None
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # 已回答的评论ID（避免重复回答）
        self.answered_comments = self._load_answered_comments()

    def _load_answered_comments(self) -> set:
        """加载已回答的评论ID"""
        try:
            with open('substack_answered_comments.json', 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()

    def _save_answered_comments(self):
        """保存已回答的评论ID"""
        with open('substack_answered_comments.json', 'w') as f:
            json.dump(list(self.answered_comments), f)

    def _load_auth(self) -> dict:
        """加载认证信息"""
        try:
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ 认证文件不存在: {self.auth_file}")
            return None

    def _random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def setup_browser(self, headless: bool = True):
        """设置浏览器"""
        logger.info("🌐 启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        # 加载cookies
        auth_data = self._load_auth()
        if auth_data and 'cookies' in auth_data:
            context.add_cookies(auth_data['cookies'])
            logger.info("   ✅ Cookies已加载")

        self.page = context.new_page()
        logger.info("   ✅ 浏览器已启动")

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("🔒 浏览器已关闭")

    def verify_login(self) -> bool:
        """验证登录状态"""
        try:
            logger.info("🔐 验证Substack登录状态...")
            home_url = f"https://{self.substack_url}" if self.substack_url else "https://substack.com"
            self.page.goto(home_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # 检查登录标志
            login_indicators = [
                'button:has-text("New post")',
                'a[href*="/publish"]',
                '[data-testid="user-menu"]'
            ]

            for selector in login_indicators:
                try:
                    elem = self.page.query_selector(selector)
                    if elem:
                        logger.info("   ✅ Substack登录状态有效")
                        return True
                except:
                    continue

            logger.error("   ❌ 未检测到登录状态")
            return False

        except Exception as e:
            logger.error(f"   ❌ 验证登录失败: {str(e)}")
            return False

    def generate_answer(self, comment_text: str, context: str = "") -> str:
        """
        生成回答 - 核心AI逻辑

        Args:
            comment_text: 评论内容
            context: 文章上下文（可选）

        Returns:
            生成的回答
        """
        logger.info("🤖 生成AI回答...")

        # Product context
        product_context = """
You are the founder of HireMeAI (https://interviewasssistant.com), an AI-powered real-time interview assistant.

Product core features:
- Voice recognition (95%+ accuracy)
- Speaker identification (92% accuracy)
- Real-time AI answer generation (<1s latency)
- STAR framework interview optimization

Your response style requirements:
✅ Warm, concise, practical
✅ Use casual internet language naturally (e.g., "damn", "ngl", "tbh", "lowkey", "fr")
✅ Answer seemingly "unrelated" but relevant questions (interview tips, AI applications, career advice)
✅ Don't be overly enthusiastic, don't hard-sell the product
✅ If very relevant, you can naturally mention HireMeAI, but it's not required

❌ Avoid:
- Long-winded responses
- Overly formal tone
- Direct product pitches
- Excessive praise or enthusiasm
"""

        prompt = f"""{product_context}

Article context:
{context if context else "No specific context"}

Comment:
{comment_text}

Generate a brief, valuable response in ENGLISH (50-150 words):
- Directly answer the core question
- Share practical insights or experience
- Natural, warm but not over-the-top tone
- Use casual internet language appropriately
- If highly relevant, casually mention HireMeAI (https://interviewasssistant.com), but don't force it

Output ONLY the response text in ENGLISH, no additional explanation:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"   ✅ 回答已生成: {answer[:50]}...")
            return answer

        except Exception as e:
            logger.error(f"   ❌ 生成回答失败: {str(e)}")
            return None

    def should_answer_comment(self, comment_text: str) -> bool:
        """
        判断是否应该回答这条评论

        Args:
            comment_text: 评论内容

        Returns:
            是否应该回答
        """
        # 使用简单规则过滤
        comment_lower = comment_text.lower()

        # 太短的评论不回答
        if len(comment_text) < 10:
            return False

        # 检查是否包含问题词
        question_keywords = ['?', '？', 'how', 'why', 'what', 'when', 'where', 'who',
                           'can', 'could', 'would', 'should', '如何', '怎么', '为什么',
                           '什么', '哪里', '谁', '能不能', '可以']

        has_question = any(keyword in comment_lower for keyword in question_keywords)

        # 检查是否包含相关主题
        relevant_topics = ['interview', 'job', 'career', 'ai', 'resume', 'cv',
                          'hiring', 'recruiter', '面试', '工作', '职业', '简历',
                          '求职', 'tech', 'coding', 'programming', '技术']

        is_relevant = any(topic in comment_lower for topic in relevant_topics)

        # 问题 OR 相关主题都可以回答
        return has_question or is_relevant

    def scrape_comments(self, article_url: str, max_comments: int = 20) -> List[Dict]:
        """
        抓取文章评论

        Args:
            article_url: 文章URL
            max_comments: 最多抓取数量

        Returns:
            评论列表
        """
        logger.info(f"📖 抓取文章评论: {article_url}")

        try:
            self.page.goto(article_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(3, 5)

            # 滚动加载评论
            logger.info("   📜 滚动加载评论...")
            for _ in range(3):
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                self._random_delay(1, 2)

            # 查找评论元素
            comment_selectors = [
                'div[data-testid="comment"]',
                'div.comment',
                'article.comment',
                'div[class*="Comment"]'
            ]

            comments = []
            for selector in comment_selectors:
                try:
                    comment_elements = self.page.query_selector_all(selector)
                    if comment_elements:
                        logger.info(f"   ✅ 找到 {len(comment_elements)} 条评论")

                        for elem in comment_elements[:max_comments]:
                            try:
                                # 提取评论文本
                                comment_text = elem.inner_text()

                                # 提取评论ID（用于去重）
                                comment_id = elem.get_attribute('data-comment-id') or str(hash(comment_text))

                                # 检查是否已回答
                                if comment_id in self.answered_comments:
                                    logger.debug(f"   ⏭️  跳过已回答评论: {comment_id}")
                                    continue

                                # 检查是否应该回答
                                if not self.should_answer_comment(comment_text):
                                    logger.debug(f"   ⏭️  跳过不相关评论: {comment_text[:50]}...")
                                    continue

                                comments.append({
                                    'id': comment_id,
                                    'text': comment_text,
                                    'element': elem
                                })

                            except Exception as e:
                                logger.debug(f"   解析评论失败: {str(e)}")
                                continue

                        break
                except:
                    continue

            logger.info(f"   ✅ 发现 {len(comments)} 条可回答的评论")
            return comments

        except Exception as e:
            logger.error(f"   ❌ 抓取评论失败: {str(e)}")
            return []

    def post_reply(self, comment_element, reply_text: str) -> bool:
        """
        发布回复到评论

        Args:
            comment_element: 评论元素
            reply_text: 回复内容

        Returns:
            是否成功
        """
        try:
            logger.info(f"   💬 发布回复...")

            # 查找回复按钮
            reply_button = comment_element.query_selector('button:has-text("Reply")')
            if not reply_button:
                reply_button = comment_element.query_selector('a:has-text("Reply")')

            if not reply_button:
                logger.warning("   ⚠️  未找到回复按钮")
                return False

            # 点击回复按钮
            reply_button.click()
            self._random_delay(1, 2)

            # 查找回复输入框
            reply_input_selectors = [
                'textarea[placeholder*="reply"]',
                'textarea[placeholder*="Reply"]',
                'div[contenteditable="true"]',
                'textarea'
            ]

            reply_input = None
            for selector in reply_input_selectors:
                try:
                    reply_input = self.page.wait_for_selector(selector, timeout=3000)
                    if reply_input and reply_input.is_visible():
                        break
                except:
                    continue

            if not reply_input:
                logger.warning("   ⚠️  未找到回复输入框")
                return False

            # 输入回复内容
            reply_input.click()
            self._random_delay(0.5, 1)

            # 模拟人类打字
            words = reply_text.split(' ')
            for word in words:
                self.page.keyboard.type(word + ' ')
                if random.random() < 0.1:  # 10%概率停顿
                    self._random_delay(0.2, 0.5)

            self._random_delay(1, 2)

            # 查找发送按钮
            send_button_selectors = [
                'button:has-text("Post")',
                'button:has-text("Send")',
                'button:has-text("Reply")',
                'button[type="submit"]'
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.wait_for_selector(selector, timeout=3000)
                    if send_button and send_button.is_visible() and send_button.is_enabled():
                        break
                except:
                    continue

            if not send_button:
                logger.warning("   ⚠️  未找到发送按钮")
                return False

            # 发送回复
            send_button.click()
            self._random_delay(2, 3)

            logger.info(f"      ✅ 回复已发送")
            return True

        except Exception as e:
            logger.error(f"   ❌ 发布回复失败: {str(e)}")
            return False

    def run_on_article(self, article_url: str, max_replies: int = 5):
        """
        在单篇文章上运行回答机器人

        Args:
            article_url: 文章URL
            max_replies: 最多回复数量
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 开始处理文章: {article_url}")
        logger.info(f"{'='*80}")

        # 抓取评论
        comments = self.scrape_comments(article_url)

        if not comments:
            logger.info("   ℹ️  没有需要回答的评论")
            return

        # 限制回复数量
        comments = comments[:max_replies]
        logger.info(f"   📝 将回复 {len(comments)} 条评论")

        # 逐条回答
        for i, comment in enumerate(comments, 1):
            logger.info(f"\n--- 评论 {i}/{len(comments)} ---")
            logger.info(f"内容: {comment['text'][:100]}...")

            # 生成回答
            answer = self.generate_answer(comment['text'])

            if not answer:
                logger.warning("   ⚠️  生成回答失败，跳过")
                continue

            logger.info(f"回答: {answer}")

            # 发布回复
            success = self.post_reply(comment['element'], answer)

            if success:
                # 标记为已回答
                self.answered_comments.add(comment['id'])
                self._save_answered_comments()
                logger.info(f"   ✅ 第 {i} 条评论回复成功")
            else:
                logger.warning(f"   ❌ 第 {i} 条评论回复失败")

            # 评论间延迟，避免被检测
            if i < len(comments):
                delay = random.randint(60, 180)  # 1-3分钟
                logger.info(f"   ⏳ 等待 {delay} 秒后继续...")
                time.sleep(delay)

        logger.info(f"\n✅ 文章处理完成，共回复 {len(comments)} 条评论")


if __name__ == "__main__":
    """测试脚本"""
    import sys

    # 测试配置
    SUBSTACK_DOMAIN = "yourname.substack.com"
    TEST_ARTICLE_URL = f"https://{SUBSTACK_DOMAIN}/p/your-article-slug"

    bot = SubstackAnswerBot(substack_url=SUBSTACK_DOMAIN)

    try:
        bot.setup_browser(headless=False)

        if bot.verify_login():
            print("✅ 登录验证成功")

            print(f"\n测试文章: {TEST_ARTICLE_URL}")
            print("⚠️  测试模式：只回复前3条评论\n")

            # 运行回答机器人
            bot.run_on_article(TEST_ARTICLE_URL, max_replies=3)

        else:
            print("❌ 登录验证失败，请先运行 substack_login_and_save_auth.py")

    finally:
        input("\n按Enter关闭浏览器...")
        bot.close_browser()
