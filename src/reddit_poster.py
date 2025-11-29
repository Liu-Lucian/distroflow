#!/usr/bin/env python3
"""
Reddit自动发帖 - 基于Playwright
遵循养号策略，避免被封
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import json
import time
import logging
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditPoster:
    def __init__(self, auth_file='reddit_auth.json'):
        self.auth_file = auth_file
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.reddit_url = "https://www.reddit.com"

    def load_cookies(self):
        """加载Reddit cookies"""
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            return auth_data.get('cookies', [])
        except FileNotFoundError:
            logger.error(f"❌ 找不到认证文件: {self.auth_file}")
            logger.info("   请先运行 python3 reddit_login_and_save_auth.py")
            return []

    def setup_browser(self, headless=False):
        """设置浏览器"""
        logger.info("🌐 启动浏览器...")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        # 加载cookies
        cookies = self.load_cookies()
        if cookies:
            self.context.add_cookies(cookies)
            logger.info("   ✅ 已加载认证cookies")

        self.page = self.context.new_page()
        logger.info("   ✅ 浏览器启动完成")

    def verify_login(self):
        """验证是否已登录"""
        logger.info("🔐 验证登录状态...")

        try:
            self.page.goto(self.reddit_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # 检查是否有登录按钮（如果有说明未登录）
            login_selectors = ['a[href*="login"]', 'button:has-text("Log In")']
            for selector in login_selectors:
                login_button = self.page.query_selector(selector)
                if login_button and login_button.is_visible():
                    logger.error("   ❌ 未登录")
                    return False

            # 检查用户菜单（登录后会有）
            user_selectors = ['[id*="user-menu"]', '[aria-label*="User Menu"]', 'button[id*="user"]']
            for selector in user_selectors:
                user_menu = self.page.query_selector(selector)
                if user_menu:
                    logger.info("   ✅ 登录验证成功")
                    return True

            logger.warning("   ⚠️  无法确认登录状态")
            return False

        except Exception as e:
            logger.error(f"   ❌ 验证失败: {str(e)}")
            return False

    def create_post(self, subreddit, title, body):
        """发布帖子"""
        logger.info(f"\n📤 准备发布到 r/{subreddit}...")
        logger.info(f"   标题: {title[:60]}...")

        try:
            # 1. 进入subreddit
            subreddit_url = f"{self.reddit_url}/r/{subreddit}"
            logger.info(f"   访问 {subreddit_url}")
            self.page.goto(subreddit_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # 2. 点击Create Post
            create_selectors = [
                'a[href*="submit"]',
                'button:has-text("Create")',
                'a:has-text("Create Post")'
            ]

            create_button = None
            for selector in create_selectors:
                try:
                    create_button = self.page.wait_for_selector(selector, timeout=3000)
                    if create_button and create_button.is_visible():
                        break
                except:
                    continue

            if not create_button:
                logger.error("   ❌ 找不到Create Post按钮")
                return False

            create_button.click()
            time.sleep(3)

            # 3. 填写标题
            logger.info("   填写标题...")
            title_selectors = ['textarea[placeholder*="Title"]', 'input[placeholder*="Title"]']

            title_input = None
            for selector in title_selectors:
                try:
                    title_input = self.page.wait_for_selector(selector, timeout=3000)
                    if title_input and title_input.is_visible():
                        break
                except:
                    continue

            if not title_input:
                logger.error("   ❌ 找不到标题输入框")
                return False

            title_input.fill(title)
            time.sleep(1)

            # 4. 填写正文
            logger.info("   填写正文...")
            body_selectors = ['div[contenteditable="true"]', 'textarea[placeholder*="Text"]']

            body_input = None
            for selector in body_selectors:
                try:
                    body_input = self.page.wait_for_selector(selector, timeout=3000)
                    if body_input and body_input.is_visible():
                        break
                except:
                    continue

            if not body_input:
                logger.error("   ❌ 找不到正文输入框")
                return False

            body_input.click()
            time.sleep(0.5)
            self.page.keyboard.type(body, delay=random.randint(10, 30))
            time.sleep(2)

            # 5. 发布
            logger.info("   发布帖子...")
            post_selectors = ['button:has-text("Post")', 'button:has-text("Submit")']

            post_button = None
            for selector in post_selectors:
                try:
                    post_button = self.page.query_selector(selector)
                    if post_button and post_button.is_visible() and not post_button.is_disabled():
                        break
                except:
                    continue

            if not post_button:
                logger.error("   ❌ 找不到Post按钮")
                return False

            post_button.click()
            time.sleep(5)

            # 检查成功
            if '/comments/' in self.page.url:
                logger.info(f"\n✅ 帖子发布成功！\n   URL: {self.page.url}")
                return True
            else:
                logger.warning("   ⚠️  可能发布失败")
                return False

        except Exception as e:
            logger.error(f"   ❌ 发布失败: {str(e)}")
            return False

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
