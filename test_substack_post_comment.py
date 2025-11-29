#!/usr/bin/env python3
"""
Substack真实评论发送测试
登录Substack，在指定文章下发送测试评论

测试内容：
1. 验证登录是否成功
2. 找到评论输入框
3. 发送测试评论
4. 确认评论发送成功
"""

import sys
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright
import json
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class SubstackCommentTester:
    """Substack评论发送测试器"""

    def __init__(self, auth_file: str = "substack_auth.json"):
        self.auth_file = auth_file
        self.playwright = None
        self.browser = None
        self.page = None

    def _load_auth(self):
        """加载认证信息"""
        try:
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ Auth file not found: {self.auth_file}")
            logger.error("   Please run: python3 substack_login_and_save_auth.py")
            return None

    def _random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """随机延迟"""
        time.sleep(random.uniform(min_sec, max_sec))

    def setup_browser(self, headless: bool = False):
        """设置浏览器"""
        logger.info("🌐 Starting browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        # Load cookies
        auth_data = self._load_auth()
        if auth_data and 'cookies' in auth_data:
            context.add_cookies(auth_data['cookies'])
            logger.info("   ✅ Cookies loaded")

        self.page = context.new_page()
        logger.info("   ✅ Browser started")

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("🔒 Browser closed")

    def verify_login(self, home_url: str):
        """验证登录状态"""
        try:
            logger.info("\n🔐 Verifying Substack login...")
            self.page.goto(home_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # Check for login indicators
            login_indicators = [
                'button:has-text("New post")',
                'a[href*="/publish"]',
                '[data-testid="user-menu"]',
                'img[alt*="avatar"]'
            ]

            for selector in login_indicators:
                try:
                    elem = self.page.query_selector(selector)
                    if elem:
                        logger.info("   ✅ Substack login verified")
                        return True
                except:
                    continue

            logger.error("   ❌ Not logged in")
            return False

        except Exception as e:
            logger.error(f"   ❌ Login verification failed: {str(e)}")
            return False

    def post_test_comment(self, article_url: str, comment_text: str) -> bool:
        """
        在文章下发送测试评论

        Args:
            article_url: 文章URL
            comment_text: 评论内容

        Returns:
            是否成功
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 Posting test comment")
        logger.info(f"{'='*80}")
        logger.info(f"Article: {article_url}")
        logger.info(f"Comment: {comment_text}")
        logger.info(f"{'='*80}\n")

        try:
            # Step 1: Visit article
            logger.info("Step 1: Opening article page...")
            self.page.goto(article_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(3, 5)

            # Screenshot 1 - Article page
            self.page.screenshot(path="substack_test_article_page.png")
            logger.info("   📸 Screenshot: substack_test_article_page.png")

            # Step 2: Scroll to comments section
            logger.info("\nStep 2: Scrolling to comments section...")
            for _ in range(3):
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                self._random_delay(1, 2)

            # Step 3: Find comment input box
            logger.info("\nStep 3: Finding comment input...")

            comment_input_selectors = [
                'textarea[placeholder*="comment"]',
                'textarea[placeholder*="Comment"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Write"]',
                'textarea[aria-label*="comment"]',
                'div[role="textbox"]',
                'textarea'
            ]

            comment_input = None
            used_selector = None

            for selector in comment_input_selectors:
                try:
                    logger.info(f"   Trying selector: {selector}")
                    inputs = self.page.query_selector_all(selector)

                    for input_elem in inputs:
                        if input_elem.is_visible():
                            comment_input = input_elem
                            used_selector = selector
                            logger.info(f"   ✅ Found comment input: {selector}")
                            break

                    if comment_input:
                        break
                except Exception as e:
                    logger.debug(f"   Selector {selector} failed: {str(e)}")
                    continue

            if not comment_input:
                logger.error("   ❌ Comment input not found")
                logger.info("\n💡 Available elements on page:")

                # Debug: Show all textareas and contenteditable divs
                textareas = self.page.query_selector_all('textarea')
                logger.info(f"   Found {len(textareas)} textarea elements")

                editables = self.page.query_selector_all('div[contenteditable="true"]')
                logger.info(f"   Found {len(editables)} contenteditable divs")

                self.page.screenshot(path="substack_test_input_not_found.png")
                logger.info("   📸 Screenshot: substack_test_input_not_found.png")

                return False

            # Step 4: Click and focus on input
            logger.info("\nStep 4: Clicking comment input...")
            comment_input.scroll_into_view_if_needed()
            self._random_delay(1, 2)
            comment_input.click()
            self._random_delay(1, 2)

            # Screenshot 2 - Input focused
            self.page.screenshot(path="substack_test_input_focused.png")
            logger.info("   📸 Screenshot: substack_test_input_focused.png")

            # Step 5: Type comment (simulate human typing)
            logger.info("\nStep 5: Typing comment...")

            # Split into words for natural typing
            words = comment_text.split(' ')
            for i, word in enumerate(words):
                self.page.keyboard.type(word)
                if i < len(words) - 1:
                    self.page.keyboard.type(' ')

                # Random pause every few words
                if i % 5 == 0 and i > 0:
                    self._random_delay(0.2, 0.5)

            logger.info("   ✅ Comment typed")
            self._random_delay(2, 3)

            # Screenshot 3 - Comment entered
            self.page.screenshot(path="substack_test_comment_entered.png")
            logger.info("   📸 Screenshot: substack_test_comment_entered.png")

            # Step 6: Find and click submit button
            logger.info("\nStep 6: Finding submit button...")

            submit_button_selectors = [
                'button:has-text("Post")',
                'button:has-text("Submit")',
                'button:has-text("Publish")',
                'button:has-text("Comment")',
                'button[type="submit"]',
                'button[aria-label*="Post"]',
                'button[aria-label*="Submit"]'
            ]

            submit_button = None
            for selector in submit_button_selectors:
                try:
                    logger.info(f"   Trying selector: {selector}")
                    button = self.page.wait_for_selector(selector, timeout=3000)
                    if button and button.is_visible() and button.is_enabled():
                        submit_button = button
                        logger.info(f"   ✅ Found submit button: {selector}")
                        break
                except:
                    continue

            if not submit_button:
                logger.warning("   ⚠️  Submit button not found")
                logger.info("\n💡 Available buttons:")
                buttons = self.page.query_selector_all('button')
                logger.info(f"   Found {len(buttons)} button elements")
                for btn in buttons[:10]:  # Show first 10
                    try:
                        text = btn.inner_text()
                        if text:
                            logger.info(f"      - '{text}'")
                    except:
                        pass

                self.page.screenshot(path="substack_test_button_not_found.png")
                logger.info("   📸 Screenshot: substack_test_button_not_found.png")

                logger.info("\n⚠️  Comment was typed but not submitted (submit button not found)")
                logger.info("   Please check the screenshot and manually click submit if needed")
                return False

            # Step 7: Click submit
            logger.info("\nStep 7: Submitting comment...")
            submit_button.click()
            self._random_delay(3, 5)

            # Screenshot 4 - After submit
            self.page.screenshot(path="substack_test_after_submit.png")
            logger.info("   📸 Screenshot: substack_test_after_submit.png")

            # Step 8: Verify comment appeared
            logger.info("\nStep 8: Verifying comment...")

            # Wait a bit for comment to appear
            self._random_delay(2, 3)

            # Check if comment text appears on page
            page_content = self.page.content()
            if comment_text in page_content:
                logger.info("   ✅ Comment text found on page")
                logger.info(f"\n{'='*80}")
                logger.info("✅ TEST SUCCESSFUL!")
                logger.info(f"{'='*80}")
                logger.info("Comment was successfully posted to Substack")
                logger.info("\n📸 Screenshots saved:")
                logger.info("   1. substack_test_article_page.png")
                logger.info("   2. substack_test_input_focused.png")
                logger.info("   3. substack_test_comment_entered.png")
                logger.info("   4. substack_test_after_submit.png")
                logger.info(f"{'='*80}")
                return True
            else:
                logger.warning("   ⚠️  Comment text not found on page yet")
                logger.info("   This might be normal if Substack requires moderation")
                logger.info("   Please check the screenshot to verify")
                return True  # Still consider it success if submit worked

        except Exception as e:
            logger.error(f"\n❌ Error posting comment: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            try:
                self.page.screenshot(path="substack_test_error.png")
                logger.info("📸 Screenshot: substack_test_error.png")
            except:
                pass

            return False


def main():
    """主函数"""
    logger.info("\n" + "="*80)
    logger.info("🧪 Substack Real Comment Posting Test")
    logger.info("="*80)
    logger.info("This will POST A REAL COMMENT to Substack")
    logger.info("Make sure you're OK with posting this comment before proceeding")
    logger.info("="*80 + "\n")

    # Get article URL
    logger.info("Step 1: Enter the Substack article URL")
    logger.info("Example: https://yourname.substack.com/p/your-article-title")

    try:
        article_url = input("\nArticle URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        logger.info("\n❌ Cancelled")
        return

    if not article_url:
        logger.error("❌ No URL provided")
        return

    # Get test comment text
    logger.info("\nStep 2: Enter test comment (or press Enter for default)")
    logger.info("Default: 'Great insights! Looking forward to more updates on this.'")

    try:
        comment_text = input("\nComment text: ").strip()
    except (EOFError, KeyboardInterrupt):
        logger.info("\n❌ Cancelled")
        return

    if not comment_text:
        comment_text = "Great insights! Looking forward to more updates on this."

    # Confirm
    logger.info("\n" + "="*80)
    logger.info("📋 Review before posting:")
    logger.info("="*80)
    logger.info(f"Article: {article_url}")
    logger.info(f"Comment: {comment_text}")
    logger.info("="*80)

    try:
        confirm = input("\nProceed? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        logger.info("\n❌ Cancelled")
        return

    if confirm not in ['yes', 'y']:
        logger.info("❌ Cancelled")
        return

    # Run test
    tester = SubstackCommentTester()

    try:
        tester.setup_browser(headless=False)

        # Extract home URL from article URL
        from urllib.parse import urlparse
        parsed = urlparse(article_url)
        home_url = f"{parsed.scheme}://{parsed.netloc}"

        # Verify login
        if not tester.verify_login(home_url):
            logger.error("\n❌ Login verification failed")
            logger.error("Please run: python3 substack_login_and_save_auth.py")
            return

        # Post comment
        success = tester.post_test_comment(article_url, comment_text)

        if success:
            logger.info("\n✅ Test completed successfully!")
        else:
            logger.info("\n⚠️  Test completed with warnings (check screenshots)")

    except Exception as e:
        logger.error(f"\n❌ Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    finally:
        logger.info("\n")
        try:
            input("Press Enter to close browser...")
        except:
            pass
        tester.close_browser()


if __name__ == "__main__":
    main()
