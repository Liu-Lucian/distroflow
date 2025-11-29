"""
Twitter/X DM Sender - Twitter私信发送器
"""

import json
import logging
from typing import Dict
from playwright.sync_api import sync_playwright
from src.dm_sender_base import DMSenderBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterDMSender(DMSenderBase):
    """Twitter/X私信发送器"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """初始化Twitter DM发送器"""
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('twitter', {})
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'Twitter')
        self.cookies = auth_config.get('cookies', [])

    def _setup_browser(self):
        """设置Playwright浏览器并加载Twitter cookies"""
        if not self.playwright:
            logger.info("🌐 Setting up Twitter browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1280, 'height': 720}
            )

            if self.cookies:
                self.context.add_cookies(self.cookies)
                logger.info("   ✅ Twitter cookies loaded")

            self.page = self.context.new_page()

    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送Twitter DM

        Args:
            user_profile: 用户资料（必须包含username）
            message: 消息内容

        Returns:
            是否成功发送
        """
        username = user_profile.get('username', user_profile.get('screen_name'))
        if not username:
            logger.error("❌ No Twitter username found")
            return False

        # 移除@符号
        username = username.lstrip('@')

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to @{username}...")

            # 方法1: 直接访问DM compose URL
            dm_url = f"https://twitter.com/messages/compose?recipient_id={username}"

            # 先访问用户主页获取user ID
            profile_url = f"https://twitter.com/{username}"
            self.page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            self._random_delay(2, 3)

            # 检查是否登录
            if 'login' in self.page.url:
                logger.error("❌ Not logged in to Twitter")
                return False

            # 查找"Message"按钮
            message_button_selectors = [
                'div[data-testid="sendDMFromProfile"]',
                'a[data-testid="sendDMFromProfile"]',
                'button[data-testid="sendDMFromProfile"]',
                'div[aria-label="Message"]',
            ]

            message_button = None
            for selector in message_button_selectors:
                try:
                    message_button = self.page.wait_for_selector(selector, timeout=3000)
                    if message_button:
                        logger.info(f"   ✅ Found message button: {selector}")
                        break
                except:
                    continue

            if not message_button:
                logger.warning("   ⚠️  DMs may not be enabled for this user")
                return False

            # 点击Message按钮
            message_button.click()
            self._random_delay(2, 3)

            # 等待DM输入框
            dm_box_selectors = [
                'div[data-testid="dmComposerTextInput"]',
                'div[contenteditable="true"][data-testid="dmComposerTextInput"]',
                'div.public-DraftEditor-content',
            ]

            dm_box = None
            for selector in dm_box_selectors:
                try:
                    dm_box = self.page.wait_for_selector(selector, timeout=5000)
                    if dm_box:
                        logger.info(f"   ✅ Found DM input box: {selector}")
                        break
                except:
                    continue

            if not dm_box:
                logger.error("❌ Could not find DM input box")
                return False

            # 输入消息
            logger.info("   ✏️  Typing message...")
            self._type_like_human(dm_box, message)
            self._random_delay(1, 2)

            # 发送消息
            send_button_selectors = [
                'div[data-testid="dmComposerSendButton"]',
                'button[data-testid="dmComposerSendButton"]',
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.wait_for_selector(selector, timeout=3000)
                    if send_button:
                        logger.info(f"   ✅ Found send button: {selector}")
                        break
                except:
                    continue

            if not send_button:
                logger.error("❌ Could not find send button")
                return False

            send_button.click()
            logger.info("   ✅ DM sent!")
            self._random_delay(2, 3)

            return True

        except Exception as e:
            logger.error(f"❌ Error sending Twitter DM: {e}")
            import traceback
            traceback.print_exc()
            return False


# 测试代码
if __name__ == "__main__":
    sender = TwitterDMSender()

    test_user = {
        'username': 'test_user',
        'company': 'Test Corp',
        'project': 'AI Project'
    }

    test_message = """Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

    formatted_message = sender.format_message(test_message, test_user)
    print(f"\n📝 Formatted message:\n{formatted_message}\n")
