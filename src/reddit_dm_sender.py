"""
Reddit DM Sender - Reddit私信发送器
"""

import json
import logging
from typing import Dict
from playwright.sync_api import sync_playwright
from src.dm_sender_base import DMSenderBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedditDMSender(DMSenderBase):
    """Reddit私信发送器"""

    def __init__(self, auth_file: str = "reddit_auth.json"):
        """初始化Reddit DM发送器"""
        # 优先使用storage_state文件
        import os
        self.use_storage_state = os.path.exists(auth_file)

        if self.use_storage_state:
            # 使用storage_state（推荐）
            self.storage_state_file = auth_file
            logger.info(f"Using storage_state from {auth_file}")
            super().__init__({}, 'Reddit')
        else:
            # 尝试从platforms_auth.json读取
            try:
                with open("platforms_auth.json", 'r') as f:
                    config = json.load(f)
                auth_config = config.get('reddit', {})
            except FileNotFoundError:
                logger.error(f"❌ No Reddit auth found")
                auth_config = {}

            super().__init__(auth_config, 'Reddit')
            self.storage_state_file = None

        self.username = self.auth_config.get('username', '')
        self.password = self.auth_config.get('password', '')

    def _setup_browser(self):
        """设置Playwright浏览器并登录Reddit"""
        if not self.playwright:
            logger.info("🌐 Setting up Reddit browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            # 使用storage_state或创建新context
            if self.use_storage_state and self.storage_state_file:
                logger.info(f"🔐 Loading authentication from {self.storage_state_file}...")
                self.context = self.browser.new_context(
                    storage_state=self.storage_state_file,
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    viewport={'width': 1280, 'height': 720}
                )
            else:
                self.context = self.browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    viewport={'width': 1280, 'height': 720}
                )

            self.page = self.context.new_page()

            # 如果没有storage_state，尝试用户名密码登录
            if not self.use_storage_state and self.username and self.password:
                self._login_reddit()

    def _login_reddit(self):
        """登录Reddit"""
        try:
            logger.info("   🔐 Logging in to Reddit...")
            self.page.goto('https://www.reddit.com/login/', wait_until='domcontentloaded')
            self._random_delay(2, 3)

            # 输入用户名
            username_input = self.page.wait_for_selector('input[name="username"]', timeout=5000)
            username_input.fill(self.username)

            # 输入密码
            password_input = self.page.wait_for_selector('input[name="password"]', timeout=5000)
            password_input.fill(self.password)

            # 点击登录
            login_button = self.page.wait_for_selector('button[type="submit"]', timeout=5000)
            login_button.click()

            self._random_delay(3, 5)
            logger.info("   ✅ Logged in to Reddit")

        except Exception as e:
            logger.error(f"❌ Failed to login to Reddit: {e}")

    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送Reddit私信

        Args:
            user_profile: 用户资料（必须包含username）
            message: 消息内容

        Returns:
            是否成功发送
        """
        username = user_profile.get('username', user_profile.get('author'))
        if not username:
            logger.error("❌ No Reddit username found")
            return False

        # 移除u/前缀
        username = username.replace('u/', '').replace('/u/', '')

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to u/{username}...")

            # 访问用户主页
            profile_url = f"https://www.reddit.com/user/{username}"
            self.page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            self._random_delay(2, 3)

            # 检查是否登录
            if 'login' in self.page.url:
                logger.error("❌ Not logged in to Reddit")
                return False

            # 查找"Send Message"按钮或链接
            # Reddit有多种UI，尝试不同的选择器
            message_link_selectors = [
                'a[href*="/message/compose"]',
                'button:has-text("Send Message")',
                'a:has-text("Send Message")',
                'button:has-text("Chat")',
            ]

            message_link = None
            for selector in message_link_selectors:
                try:
                    message_link = self.page.wait_for_selector(selector, timeout=3000)
                    if message_link:
                        logger.info(f"   ✅ Found message button: {selector}")
                        break
                except:
                    continue

            if not message_link:
                # 尝试直接访问compose URL
                logger.info("   ℹ️  Using direct compose URL...")
                compose_url = f"https://www.reddit.com/message/compose/?to={username}"
                self.page.goto(compose_url, wait_until='domcontentloaded')
                self._random_delay(2, 3)
            else:
                message_link.click()
                self._random_delay(2, 3)

            # 填写收件人（如果需要）
            recipient_input = None
            try:
                recipient_input = self.page.query_selector('input[name="message-recipient-input"]')
                if recipient_input and recipient_input.is_visible():
                    logger.info("   ✅ Found recipient input, filling...")
                    recipient_input.fill(username)
                    self._random_delay(0.5, 1)
            except Exception as e:
                logger.debug(f"   No recipient input found (may be pre-filled): {e}")

            # 查找主题输入框 - 使用实际的name属性
            subject_input = None
            try:
                # Reddit使用message-title作为主题字段
                subject_input = self.page.query_selector('input[name="message-title"]')
                if not subject_input or not subject_input.is_visible():
                    # 尝试其他选择器
                    subject_selectors = [
                        'input[name="subject"]',
                        'input[placeholder*="subject"]',
                        'input[placeholder*="Subject"]',
                    ]
                    for selector in subject_selectors:
                        try:
                            subject_input = self.page.wait_for_selector(selector, timeout=2000)
                            if subject_input and subject_input.is_visible():
                                break
                        except:
                            continue
            except:
                pass

            if subject_input and subject_input.is_visible():
                logger.info("   ✅ Found subject input")
                subject_input.fill("Quick question about HireMeAI")
                self._random_delay(0.5, 1)
            else:
                logger.warning("   ⚠️  Could not find subject input")

            # 查找消息输入框 - 使用实际的name属性
            message_box = None
            try:
                # Reddit使用message-content作为消息字段
                message_box = self.page.query_selector('textarea[name="message-content"]')
                if message_box and message_box.is_visible():
                    logger.info("   ✅ Found message box (message-content)")
                else:
                    # 尝试其他选择器
                    message_selectors = [
                        'textarea[name="text"]',
                        'textarea[name="message"]',
                        'div[contenteditable="true"]',
                    ]
                    for selector in message_selectors:
                        try:
                            message_box = self.page.wait_for_selector(selector, timeout=2000)
                            if message_box and message_box.is_visible():
                                logger.info(f"   ✅ Found message box: {selector}")
                                break
                        except:
                            continue
            except:
                pass

            # 如果还是找不到，尝试查找所有可见的textarea
            if not message_box or not message_box.is_visible():
                logger.info("   ℹ️  Trying to find visible textarea...")
                all_textareas = self.page.query_selector_all('textarea')
                for textarea in all_textareas:
                    if textarea.is_visible():
                        message_box = textarea
                        logger.info(f"   ✅ Found visible textarea")
                        break

            if not message_box or not message_box.is_visible():
                logger.error("❌ Could not find message input box")
                return False

            # 输入消息
            logger.info("   ✏️  Typing message...")
            # 先点击激活
            message_box.click()
            self._random_delay(0.3, 0.5)
            # 清空现有内容
            message_box.fill('')
            self._random_delay(0.2, 0.3)
            # 逐字输入
            self._type_like_human(message_box, message)
            self._random_delay(1, 2)

            # 触发input事件来激活按钮
            self.page.evaluate('''(textarea) => {
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.dispatchEvent(new Event('change', { bubbles: true }));
            }''', message_box)

            # 发送消息
            # Reddit Chat使用无文本的submit按钮，优先用aria-label
            send_button_selectors = [
                'button[type="submit"][aria-label*="Send"]',  # Chat模式：aria-label="Send message"
                'button[type="submit"]',                      # 通用submit按钮
                'button:has-text("Send")',                    # 传统模式
                'button:has-text("send")',
                'button[aria-label*="Send"]',                 # 任何Send aria-label
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    # 等待按钮出现并可见
                    send_button = self.page.wait_for_selector(selector, timeout=5000, state='visible')
                    if send_button:
                        logger.info(f"   ✅ Found send button: {selector}")
                        break
                except:
                    continue

            if not send_button:
                logger.error("❌ Could not find send button")
                # 尝试找所有type=submit的按钮
                logger.info("   ℹ️  Trying to find any submit button...")
                submit_buttons = self.page.query_selector_all('button[type="submit"]')
                for btn in submit_buttons:
                    if btn.is_visible():
                        send_button = btn
                        logger.info("   ✅ Found visible submit button")
                        break

            if not send_button:
                logger.error("❌ Still could not find send button")
                return False

            # 等待按钮可用（Chat按钮在输入内容后才会enable）
            logger.info("   ⏳ Waiting for send button to be enabled...")
            try:
                # 等待按钮不再disabled
                for _ in range(10):  # 最多等10秒
                    is_disabled = send_button.is_disabled()
                    if not is_disabled:
                        logger.info("   ✅ Send button is now enabled")
                        break
                    self._random_delay(0.8, 1.2)
                else:
                    logger.warning("   ⚠️  Button may still be disabled, trying anyway...")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not check button state: {e}")

            # 点击发送
            send_button.click()
            logger.info("   ✅ Message sent!")
            self._random_delay(2, 3)

            return True

        except Exception as e:
            logger.error(f"❌ Error sending Reddit DM: {e}")
            import traceback
            traceback.print_exc()
            return False


# 测试代码
if __name__ == "__main__":
    sender = RedditDMSender()

    test_user = {
        'username': 'test_user',
        'name': 'Test User'
    }

    test_message = """Hey {{name}}, I came across your posts — really insightful stuff.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

    formatted_message = sender.format_message(test_message, test_user)
    print(f"\n📝 Formatted message:\n{formatted_message}\n")
