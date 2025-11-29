#!/usr/bin/env python3
"""
Quora互动模块
提升账号权重的轻量互动功能：点赞、评论、关注

策略：每天5-10次轻互动，提升曝光度
"""

from playwright.sync_api import sync_playwright, Page
import time
import logging
import random
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoraEngagement:
    """Quora互动器 - 提升账号权重"""

    def __init__(self, auth_config: Optional[Dict] = None):
        """
        初始化互动器

        Args:
            auth_config: 认证配置 (cookies)
        """
        self.auth_config = auth_config or {}
        self.playwright = None
        self.browser = None
        self.page = None

    def setup_browser(self, headless: bool = True):
        """设置浏览器"""
        logger.info("🌐 启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)

        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        if self.auth_config.get('cookies'):
            context.add_cookies(self.auth_config['cookies'])
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

    def _random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def find_related_questions(self, keywords: str, limit: int = 10) -> List[str]:
        """
        查找相关问题的URL

        Args:
            keywords: 关键词
            limit: 数量限制

        Returns:
            问题URL列表
        """
        logger.info(f"🔍 查找相关问题: '{keywords}'")

        if not self.page:
            raise Exception("浏览器未初始化")

        try:
            search_url = f"https://www.quora.com/search?q={keywords.replace(' ', '+')}"
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 4)

            # 提取问题链接
            question_links = []
            selectors = [
                'a[href*="/question/"]',
                'div[class*="Question"] a'
            ]

            for selector in selectors:
                elements = self.page.query_selector_all(selector)
                if elements:
                    for elem in elements[:limit]:
                        try:
                            href = elem.get_attribute('href')
                            if href and '/question/' in href:
                                if href.startswith('/'):
                                    href = f"https://www.quora.com{href}"
                                if href not in question_links:
                                    question_links.append(href)
                        except:
                            continue
                    break

            logger.info(f"   ✅ 找到 {len(question_links)} 个相关问题")
            return question_links[:limit]

        except Exception as e:
            logger.error(f"❌ 查找问题失败: {str(e)}")
            return []

    def upvote_answer(self, question_url: str) -> bool:
        """
        点赞问题中的一个优质回答

        Args:
            question_url: 问题URL

        Returns:
            是否成功
        """
        logger.info(f"👍 点赞回答...")

        try:
            self.page.goto(question_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 4)

            # 查找点赞按钮（upvote button）
            upvote_selectors = [
                'button[aria-label*="Upvote"]',
                'button:has-text("Upvote")',
                'div[class*="UpvoteButton"]',
                'button[class*="upvote"]'
            ]

            # 找到第一个未点赞的答案的点赞按钮
            for selector in upvote_selectors:
                buttons = self.page.query_selector_all(selector)
                if buttons:
                    # 点击第一个（通常是最高质量的答案）
                    button = buttons[0]
                    if button.is_visible():
                        button.click()
                        logger.info(f"   ✅ 已点赞")
                        self._random_delay(1, 2)
                        return True

            logger.warning("   ⚠️  未找到点赞按钮")
            return False

        except Exception as e:
            logger.error(f"   ❌ 点赞失败: {str(e)}")
            return False

    def leave_comment(self, question_url: str, comment_text: str) -> bool:
        """
        在回答下留评论（提升互动）

        Args:
            question_url: 问题URL
            comment_text: 评论内容

        Returns:
            是否成功
        """
        logger.info(f"💬 留评论...")

        try:
            self.page.goto(question_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 4)

            # 查找评论框
            comment_selectors = [
                'button:has-text("Comment")',
                'button[aria-label*="Comment"]',
                'div[class*="CommentButton"]'
            ]

            comment_button = None
            for selector in comment_selectors:
                try:
                    comment_button = self.page.wait_for_selector(selector, timeout=3000)
                    if comment_button and comment_button.is_visible():
                        break
                except:
                    continue

            if not comment_button:
                logger.warning("   ⚠️  未找到评论按钮")
                return False

            # 点击评论按钮
            comment_button.click()
            self._random_delay(1, 2)

            # 查找输入框
            input_selectors = [
                'div[contenteditable="true"]',
                'textarea[placeholder*="comment"]',
                'div[class*="CommentInput"]'
            ]

            comment_input = None
            for selector in input_selectors:
                try:
                    comment_input = self.page.wait_for_selector(selector, timeout=3000)
                    if comment_input and comment_input.is_visible():
                        break
                except:
                    continue

            if not comment_input:
                logger.warning("   ⚠️  未找到评论输入框")
                return False

            # 输入评论
            comment_input.click()
            self._random_delay(0.5, 1)

            # 模拟打字
            words = comment_text.split(' ')
            for i, word in enumerate(words):
                self.page.keyboard.type(word)
                if i < len(words) - 1:
                    self.page.keyboard.type(' ')
                if i % 10 == 0:
                    self._random_delay(0.1, 0.3)

            self._random_delay(1, 2)

            # 查找提交按钮
            submit_selectors = [
                'button:has-text("Post")',
                'button:has-text("Submit")',
                'button[aria-label*="Post"]'
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.page.query_selector(selector)
                    if submit_button and submit_button.is_visible():
                        break
                except:
                    continue

            if submit_button:
                submit_button.click()
                logger.info(f"   ✅ 评论已发布")
                self._random_delay(2, 3)
                return True
            else:
                logger.warning("   ⚠️  未找到提交按钮")
                return False

        except Exception as e:
            logger.error(f"   ❌ 评论失败: {str(e)}")
            return False

    def generate_helpful_comment(self, context: str = "general") -> str:
        """
        生成有价值的评论（不是spam）

        Args:
            context: 评论上下文

        Returns:
            评论文本
        """
        helpful_comments = [
            "Great insight! This aligns with what I've experienced as well.",
            "Thanks for sharing this detailed breakdown. Very helpful!",
            "Interesting perspective. Have you considered [alternative approach]?",
            "This is exactly what I was looking for. Appreciate the thorough explanation.",
            "Solid advice. I'd also add that [additional tip] can be helpful.",
            "Well explained! The examples really clarify the concept.",
            "Thanks for this. Do you have any resources for learning more about this?",
            "This helped me understand the nuances. Much appreciated!"
        ]

        return random.choice(helpful_comments)

    def daily_engagement_routine(self, keywords: List[str], target_interactions: int = 8) -> dict:
        """
        每日互动例程

        Args:
            keywords: 相关关键词列表
            target_interactions: 目标互动次数

        Returns:
            互动统计
        """
        logger.info(f"\n🎯 开始每日互动例程（目标: {target_interactions} 次互动）")

        stats = {
            "upvotes": 0,
            "comments": 0,
            "total": 0
        }

        # 随机选择关键词
        selected_keywords = random.sample(keywords, min(2, len(keywords)))

        for keyword in selected_keywords:
            # 查找相关问题
            questions = self.find_related_questions(keyword, limit=5)

            for question_url in questions:
                if stats["total"] >= target_interactions:
                    break

                # 随机选择互动类型（70%点赞，30%评论）
                if random.random() < 0.7:
                    # 点赞
                    if self.upvote_answer(question_url):
                        stats["upvotes"] += 1
                        stats["total"] += 1
                else:
                    # 评论
                    comment = self.generate_helpful_comment()
                    if self.leave_comment(question_url, comment):
                        stats["comments"] += 1
                        stats["total"] += 1

                # 随机延迟（避免被检测）
                self._random_delay(30, 90)  # 30-90秒

            if stats["total"] >= target_interactions:
                break

        logger.info(f"\n✅ 今日互动完成:")
        logger.info(f"   👍 点赞: {stats['upvotes']}")
        logger.info(f"   💬 评论: {stats['comments']}")
        logger.info(f"   📊 总计: {stats['total']}")

        return stats


if __name__ == "__main__":
    """测试脚本"""
    import json

    # 加载认证
    auth_config = None
    if os.path.exists('quora_auth.json'):
        with open('quora_auth.json', 'r') as f:
            auth_config = json.load(f)

    engagement = QuoraEngagement(auth_config)

    try:
        engagement.setup_browser(headless=False)

        # 测试每日互动
        keywords = ["AI interview", "job preparation", "career tips"]
        stats = engagement.daily_engagement_routine(keywords, target_interactions=3)

        print(f"\n互动统计: {stats}")

    finally:
        input("\n按Enter关闭浏览器...")
        engagement.close_browser()
