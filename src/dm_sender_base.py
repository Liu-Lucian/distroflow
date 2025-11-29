"""
DM Sender Base Class - 私信发送基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DMSenderBase(ABC):
    """私信发送基类"""

    def __init__(self, auth_config: Dict, platform_name: str):
        """
        初始化DM发送器

        Args:
            auth_config: 认证配置
            platform_name: 平台名称
        """
        self.auth_config = auth_config
        self.platform_name = platform_name
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    @abstractmethod
    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送私信

        Args:
            user_profile: 用户资料
            message: 消息内容

        Returns:
            是否成功发送
        """
        pass

    @abstractmethod
    def _setup_browser(self):
        """设置浏览器（登录等）"""
        pass

    def _close_browser(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def cleanup(self):
        """清理资源（别名）"""
        self._close_browser()

    def _random_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def _type_like_human(self, element, text: str):
        """像人类一样输入文本"""
        try:
            element.click()
        except Exception as e:
            # 如果普通click被overlay阻挡，使用JavaScript点击
            logger.debug(f"Regular click failed: {e}, trying JavaScript click")
            try:
                self.page.evaluate('(element) => element.click()', element)
            except:
                pass  # 继续尝试输入

        time.sleep(0.5)
        for char in text:
            element.type(char)
            time.sleep(random.uniform(0.05, 0.15))

    def format_message(self, template: str, user_profile: Dict) -> str:
        """
        格式化消息模板

        Args:
            template: 消息模板
            user_profile: 用户资料

        Returns:
            格式化后的消息
        """
        message = template

        # 替换常见变量
        replacements = {
            '{{name}}': user_profile.get('name', user_profile.get('username', 'there')),
            '{{username}}': user_profile.get('username', ''),
            '{{company}}': user_profile.get('company', user_profile.get('organization', 'your company')),
            '{{project}}': user_profile.get('project', user_profile.get('repository', 'your project')),
            '{{product}}': user_profile.get('product', user_profile.get('project', 'your product')),
        }

        for key, value in replacements.items():
            if key in message:
                message = message.replace(key, value)

        return message
