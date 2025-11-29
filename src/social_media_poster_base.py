#!/usr/bin/env python3
"""
社交媒体发布器基类
"""

from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, Page, Browser
import json
import time
import random
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaPosterBase(ABC):
    def __init__(self, platform_name: str, auth_file: str = None):
        self.platform_name = platform_name
        self.auth_file = auth_file or f"{platform_name}_auth.json"
        self.browser = None
        self.page = None
        self.playwright = None

    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延迟，模拟人类行为"""
        time.sleep(random.uniform(min_sec, max_sec))

    def _load_auth(self) -> dict:
        """加载认证信息"""
        try:
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ 认证文件不存在: {self.auth_file}")
            return None

    def setup_browser(self, headless: bool = False):
        """设置浏览器"""
        logger.info(f"🌐 设置 {self.platform_name} 浏览器...")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )

        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        # 加载cookies
        auth_data = self._load_auth()
        if auth_data and 'cookies' in auth_data:
            context.add_cookies(auth_data['cookies'])
            logger.info("   ✅ Cookies已加载")

        self.page = context.new_page()
        return self.page

    def close_browser(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    @abstractmethod
    def find_post_button(self) -> bool:
        """查找发布按钮（需要子类实现）"""
        pass

    @abstractmethod
    def create_post(self, content: dict) -> bool:
        """创建帖子（需要子类实现）"""
        pass

    def verify_login(self) -> bool:
        """验证登录状态"""
        try:
            # 子类应该重写这个方法
            return True
        except Exception as e:
            logger.error(f"❌ 登录验证失败: {str(e)}")
            return False

    def take_screenshot(self, name: str = "debug"):
        """截图调试"""
        filename = f"{self.platform_name}_{name}_{int(time.time())}.png"
        self.page.screenshot(path=filename)
        logger.info(f"📸 截图已保存: {filename}")
        return filename
