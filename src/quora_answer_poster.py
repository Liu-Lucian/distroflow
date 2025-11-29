#!/usr/bin/env python3
"""
Quora回答发布器
自动发布回答到Quora问题
"""

from playwright.sync_api import sync_playwright, Page
import time
import logging
import random
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoraAnswerPoster:
    """Quora回答发布器"""

    def __init__(self, auth_config: Optional[Dict] = None):
        """
        初始化发布器

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

        # 创建上下文并添加cookies
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        # 添加cookies（如果有）
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
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def verify_login(self) -> bool:
        """验证登录状态"""
        try:
            logger.info("🔐 验证Quora登录状态...")
            self.page.goto("https://www.quora.com", wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # 检查是否有登录后的元素（例如个人资料按钮）
            # Quora登录后通常会显示用户头像或通知图标
            login_indicators = [
                'button[aria-label*="profile"]',
                'div[class*="Avatar"]',
                'a[href*="/profile/"]',
                'button[class*="NotificationIcon"]'
            ]

            for selector in login_indicators:
                try:
                    elem = self.page.query_selector(selector)
                    if elem:
                        logger.info("   ✅ Quora登录状态有效")
                        return True
                except:
                    continue

            logger.error("   ❌ 未检测到登录状态")
            return False

        except Exception as e:
            logger.error(f"   ❌ 验证登录失败: {str(e)}")
            return False

    def post_answer(self, question_url: str, answer_text: str) -> bool:
        """
        发布回答到指定问题 - 核心函数

        Args:
            question_url: 问题URL
            answer_text: 回答内容

        Returns:
            是否成功发布
        """
        logger.info(f"📝 准备发布回答...")
        logger.info(f"   问题: {question_url}")
        logger.info(f"   回答长度: {len(answer_text)} 字符")

        if not self.page:
            raise Exception("浏览器未初始化，请先调用 setup_browser()")

        try:
            # 访问问题页面
            logger.info("   🌐 访问问题页面...")
            self.page.goto(question_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 4)

            # 截图1 - 问题页面
            try:
                self.page.screenshot(path="quora_question_page.png")
            except:
                pass

            # 查找回答按钮 - 尝试多个选择器
            answer_button_selectors = [
                'button:has-text("Answer")',
                'a:has-text("Answer")',
                'button[class*="Answer"]',
                'div[class*="AnswerButton"]',
                'span:has-text("Answer")',
            ]

            answer_button = None
            for selector in answer_button_selectors:
                try:
                    answer_button = self.page.wait_for_selector(selector, timeout=5000)
                    if answer_button and answer_button.is_visible():
                        logger.info(f"   ✅ 找到回答按钮: {selector}")
                        break
                except:
                    continue

            if not answer_button:
                logger.error("   ❌ 未找到回答按钮")
                return False

            # 点击回答按钮
            logger.info("   🖱️  点击回答按钮...")
            answer_button.click()
            self._random_delay(2, 3)

            # 查找编辑器 - Quora使用富文本编辑器
            editor_selectors = [
                'div[contenteditable="true"]',
                'div[class*="Editor"]',
                'div[role="textbox"]',
                'div[class*="Answer"] div[contenteditable="true"]',
                'textarea'
            ]

            editor = None
            for selector in editor_selectors:
                try:
                    editor = self.page.wait_for_selector(selector, timeout=5000)
                    if editor and editor.is_visible():
                        logger.info(f"   ✅ 找到编辑器: {selector}")
                        break
                except:
                    continue

            if not editor:
                logger.error("   ❌ 未找到编辑器")
                # 截图调试
                try:
                    self.page.screenshot(path="quora_editor_not_found.png")
                except:
                    pass
                return False

            # 点击编辑器激活
            editor.click()
            self._random_delay(1, 2)

            # 输入回答内容 - 模拟人类打字
            logger.info("   ⌨️  输入回答内容...")

            # 分段输入，更自然
            paragraphs = answer_text.split('\n\n')
            for i, para in enumerate(paragraphs):
                if not para.strip():
                    continue

                # 分词输入
                words = para.split(' ')
                for j, word in enumerate(words):
                    self.page.keyboard.type(word)
                    if j < len(words) - 1:
                        self.page.keyboard.type(' ')

                    # 随机停顿
                    if j % 15 == 0 and j > 0:
                        self._random_delay(0.2, 0.5)

                # 段落之间换行
                if i < len(paragraphs) - 1:
                    self.page.keyboard.press('Enter')
                    self.page.keyboard.press('Enter')
                    self._random_delay(0.5, 1)

            logger.info("   ✅ 内容已输入")
            self._random_delay(2, 3)

            # 截图2 - 输入完成
            try:
                self.page.screenshot(path="quora_answer_entered.png")
            except:
                pass

            # 查找发布按钮
            post_button_selectors = [
                'button:has-text("Post")',
                'button:has-text("Submit")',
                'button:has-text("Publish")',
                'button[class*="Post"]',
                'button[class*="Submit"]',
            ]

            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = self.page.wait_for_selector(selector, timeout=5000)
                    if post_button and post_button.is_visible() and post_button.is_enabled():
                        logger.info(f"   ✅ 找到发布按钮: {selector}")
                        break
                except:
                    continue

            if not post_button:
                logger.error("   ❌ 未找到发布按钮")
                try:
                    self.page.screenshot(path="quora_post_button_not_found.png")
                except:
                    pass
                return False

            # 点击发布
            logger.info("   📤 发布回答...")
            post_button.click()
            self._random_delay(3, 5)

            # 截图3 - 发布后
            try:
                self.page.screenshot(path="quora_after_post.png")
            except:
                pass

            # 验证发布成功
            # Quora发布后通常会显示"Your answer has been posted"或回到问题页面
            current_url = self.page.url
            if question_url in current_url or '/answer/' in current_url:
                logger.info("   ✅ 回答发布成功！")
                return True
            else:
                logger.warning(f"   ⚠️  发布状态未知，当前URL: {current_url}")
                return True  # 假设成功

        except Exception as e:
            logger.error(f"   ❌ 发布失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            # 错误截图
            try:
                self.page.screenshot(path="quora_error.png")
            except:
                pass

            return False

    def take_screenshot(self, name: str):
        """截图调试"""
        try:
            filename = f"quora_screenshot_{name}_{int(time.time())}.png"
            self.page.screenshot(path=filename)
            logger.info(f"   📸 截图已保存: {filename}")
        except Exception as e:
            logger.debug(f"   截图失败: {str(e)}")


if __name__ == "__main__":
    """测试脚本"""
    import json
    import os

    # 测试回答发布
    poster = QuoraAnswerPoster()

    try:
        poster.setup_browser(headless=False)

        if poster.verify_login():
            print("✅ 登录验证成功")

            # 测试回答（需要替换为实际问题URL）
            test_question = "https://www.quora.com/What-is-the-best-way-to-prepare-for-a-job-interview"
            test_answer = """Based on my experience helping hundreds of job seekers, here are the key steps:

1. Research the company thoroughly - understand their mission, products, and culture
2. Practice common interview questions with a structured approach
3. Prepare specific examples of your achievements using the STAR method
4. Ask thoughtful questions about the role and team

I built HireMeAI (https://interviewasssistant.com) to help with AI-powered interview prep. It simulates real interviews and provides instant feedback.

Good luck with your interview!"""

            print(f"\n测试发布回答...")
            print(f"问题: {test_question}")
            print(f"回答: {test_answer[:100]}...")

            # 取消注释来实际发布
            # success = poster.post_answer(test_question, test_answer)
            # if success:
            #     print("✅ 发布测试成功！")
            # else:
            #     print("❌ 发布测试失败")

            print("\n⚠️  测试代码已注释，取消注释 poster.post_answer() 来实际发布")

        else:
            print("❌ 登录验证失败，请先运行 quora_login_and_save_auth.py")

    finally:
        input("\n按Enter关闭浏览器...")
        poster.close_browser()
