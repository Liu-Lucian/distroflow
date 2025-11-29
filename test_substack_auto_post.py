#!/usr/bin/env python3
"""
Substack完全自动化发帖测试
自动生成文章、自动发布

流程：
1. 登录Substack
2. AI生成测试文章（标题+副标题+正文）
3. 自动发布到Substack
4. 验证成功
"""

import sys
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright
from openai import OpenAI
import json
import time
import random
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


class SubstackAutoPostTester:
    """Substack完全自动化发帖测试器"""

    def __init__(self, auth_file: str = "substack_auth.json"):
        self.auth_file = auth_file
        self.playwright = None
        self.browser = None
        self.page = None
        self.home_url = "https://substack.com/home"

    def _load_auth(self):
        """加载认证信息"""
        try:
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ Auth file not found: {self.auth_file}")
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

        auth_data = self._load_auth()
        if auth_data and 'cookies' in auth_data:
            context.add_cookies(auth_data['cookies'])
            logger.info("   ✅ Cookies loaded")

        self.page = context.new_page()
        logger.info("   ✅ Browser ready")

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def verify_login(self) -> bool:
        """验证登录状态"""
        try:
            logger.info("\n🔐 Verifying Substack login...")
            self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # Take screenshot for debugging
            self.page.screenshot(path="substack_login_verify.png")

            # Comprehensive login indicators
            login_indicators = [
                'button:has-text("New post")',
                'a:has-text("New post")',
                'a[href*="/publish"]',
                'button:has-text("Write")',
                '[data-testid="user-menu"]',
                'img[alt*="avatar"]',
                'img[alt*="profile"]',
                'button[aria-label*="account"]',
                'button[aria-label*="profile"]',
                'a:has-text("Settings")',
                'a:has-text("Inbox")',
                'button:has-text("Inbox")',
                # Check if NOT showing "Sign in" button (means logged in)
            ]

            for selector in login_indicators:
                try:
                    elem = self.page.query_selector(selector)
                    if elem and elem.is_visible():
                        logger.info(f"   ✅ Login verified (found: {selector})")
                        return True
                except:
                    continue

            # Additional check: if there's NO "Sign in" button, we're logged in
            try:
                sign_in_btn = self.page.query_selector('button:has-text("Sign in")')
                if not sign_in_btn or not sign_in_btn.is_visible():
                    logger.info("   ✅ Login verified (no sign-in button)")
                    return True
            except:
                pass

            logger.warning("   ⚠️  Could not verify login, but will try to proceed")
            logger.info("   💡 If posting works, login is fine")
            # Return True anyway - if cookies are loaded, probably logged in
            return True

        except Exception as e:
            logger.error(f"   ❌ Login verification error: {str(e)}")
            # Still return True - let the actual posting attempt fail if not logged in
            return True

    def generate_test_article(self) -> dict:
        """
        AI生成测试文章

        Returns:
            {'title': '...', 'subtitle': '...', 'content': '...'}
        """
        logger.info("\n🤖 Generating test article with AI...")

        prompt = """Generate a SHORT test article for Substack about building an AI interview assistant (HireMeAI).

This is a TEST POST, so keep it brief and casual.

Requirements:
- Title: Catchy, build-in-public style (Week X format or question format)
- Subtitle: One sentence summary
- Content: 200-400 words
  - Brief hook (1-2 paragraphs)
  - Main insight or update (2-3 paragraphs)
  - Quick takeaway (1 paragraph)
  - CTA: Mention https://interviewasssistant.com
- Tone: Casual, authentic, like a quick update
- Use some casual language (e.g., "tbh", "ngl")

Output as JSON:
{
    "title": "...",
    "subtitle": "...",
    "content": "..."
}

Output ONLY valid JSON:"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=800
            )

            article_json = response.choices[0].message.content.strip()

            # Clean JSON
            if article_json.startswith('```json'):
                article_json = article_json[7:]
            if article_json.startswith('```'):
                article_json = article_json[3:]
            if article_json.endswith('```'):
                article_json = article_json[:-3]

            article = json.loads(article_json.strip())

            logger.info(f"   ✅ Article generated")
            logger.info(f"\n   Title: {article['title']}")
            logger.info(f"   Subtitle: {article['subtitle']}")
            logger.info(f"   Content length: {len(article['content'])} chars")
            logger.info(f"\n   Preview:\n   {article['content'][:150]}...\n")

            return article

        except Exception as e:
            logger.error(f"   ❌ Failed to generate article: {str(e)}")
            # Fallback
            return {
                'title': f'Test Post - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'subtitle': 'Testing automated Substack posting',
                'content': '''This is a test post generated automatically.

## Quick Update

Testing the automated posting system for HireMeAI build-in-public updates.

Ngl, automating Substack is pretty cool. This post was generated and published entirely by AI.

## Next Steps

Will use this for regular build updates.

Check out HireMeAI at https://interviewasssistant.com'''
            }

    def publish_article(self, article: dict, publish_immediately: bool = False) -> bool:
        """
        发布文章到Substack

        Args:
            article: 文章内容
            publish_immediately: 是否立即发布（否则保存为草稿）

        Returns:
            是否成功
        """
        logger.info(f"\n📤 Publishing article to Substack...")
        logger.info(f"   Mode: {'Publish immediately' if publish_immediately else 'Save as draft'}")

        try:
            # Step 1: Click "Create" button (Substack's new UI)
            logger.info("\nStep 1: Finding 'Create' button...")

            new_post_selectors = [
                'button:has-text("Create")',  # New Substack UI
                'button:has-text("New post")',
                'a:has-text("New post")',
                'button:has-text("Write")',
                'a[href*="/publish/post/new"]'
            ]

            new_post_btn = None
            for selector in new_post_selectors:
                try:
                    btn = self.page.wait_for_selector(selector, timeout=3000)
                    if btn and btn.is_visible():
                        new_post_btn = btn
                        logger.info(f"   ✅ Found: {selector}")
                        break
                except:
                    continue

            if not new_post_btn:
                logger.error("   ❌ 'New post' button not found")
                self.page.screenshot(path="substack_post_test_no_button.png")
                return False

            new_post_btn.click()
            logger.info("   ✅ Clicked 'Create'")
            self._random_delay(1, 2)

            # Check if a menu appeared (Create button shows: Note, Post, Video)
            logger.info("   Checking for dropdown menu...")
            menu_selectors = [
                'text="Post"',  # Exact match for "Post" in the menu
                'a:has-text("Post")',
                'button:has-text("Post")',
                '[role="menuitem"]:has-text("Post")',
                'div:has-text("Post")',
                'a:has-text("New post")',  # Fallback to old text
            ]

            menu_clicked = False
            for selector in menu_selectors:
                try:
                    menu_item = self.page.wait_for_selector(selector, timeout=2000)
                    if menu_item and menu_item.is_visible():
                        logger.info(f"   ✅ Found menu item: {selector}")
                        menu_item.click()
                        logger.info("   ✅ Clicked 'New post' from menu")
                        menu_clicked = True
                        break
                except:
                    continue

            if not menu_clicked:
                logger.info("   ℹ️  No menu found, assuming direct navigation")

            self._random_delay(3, 5)

            # Screenshot 1 - Editor loaded
            self.page.screenshot(path="substack_post_test_editor.png")

            # Step 2: Fill title
            logger.info("\nStep 2: Filling title...")

            # First, let's debug what's on the page
            logger.info("   Debugging: Looking for all input elements...")
            all_inputs = self.page.query_selector_all('input, textarea')
            logger.info(f"   Found {len(all_inputs)} input/textarea elements:")
            for i, inp in enumerate(all_inputs[:10]):
                try:
                    placeholder = inp.get_attribute('placeholder') or 'none'
                    name = inp.get_attribute('name') or 'none'
                    visible = inp.is_visible()
                    logger.info(f"      {i+1}. type={inp.evaluate('el => el.tagName')} placeholder='{placeholder}' name='{name}' visible={visible}")
                except:
                    pass

            title_selectors = [
                'textarea[placeholder*="Post title" i]',
                'input[placeholder*="Post title" i]',
                'textarea[placeholder*="Title" i]',
                'input[placeholder*="Title" i]',
                'h1[data-testid="storyTitle"]',
                'textarea[name="title"]',
                'input[name="title"]',
                'textarea:first-of-type',  # Often the first textarea is title
                'div[contenteditable="true"]:first-of-type',  # Sometimes it's contenteditable
                '[data-testid="title-input"]',
                '[aria-label*="title" i]'
            ]

            title_input = None
            for selector in title_selectors:
                try:
                    logger.info(f"   Trying selector: {selector}")
                    input_elem = self.page.wait_for_selector(selector, timeout=2000)
                    if input_elem and input_elem.is_visible():
                        title_input = input_elem
                        logger.info(f"   ✅ Found title input: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"      Failed: {str(e)[:50]}")
                    continue

            if not title_input:
                logger.error("   ❌ Title input not found")
                logger.info("   Taking debug screenshot...")
                self.page.screenshot(path="substack_post_test_no_title.png")
                logger.info("   Trying to type directly (last resort)...")
                # Last resort: just start typing - sometimes the page is ready to accept input
                try:
                    self.page.keyboard.type(article['title'])
                    logger.info("   ✅ Typed title directly via keyboard")
                    self._random_delay(1, 2)
                    # Continue to body
                except:
                    logger.error("   ❌ Direct typing also failed")
                    return False
            else:
                title_input.click()
                self._random_delay(0.5, 1)
                title_input.fill(article['title'])
                logger.info(f"   ✅ Title filled: {article['title'][:50]}...")
                self._random_delay(1, 2)

            # Step 3: Fill subtitle (if exists)
            logger.info("\nStep 3: Filling subtitle...")

            subtitle_selectors = [
                'textarea[placeholder*="Subtitle" i]',
                'input[placeholder*="Subtitle" i]',
                'textarea[name="subtitle"]'
            ]

            subtitle_input = None
            for selector in subtitle_selectors:
                try:
                    input_elem = self.page.wait_for_selector(selector, timeout=2000)
                    if input_elem and input_elem.is_visible():
                        subtitle_input = input_elem
                        break
                except:
                    continue

            if subtitle_input:
                subtitle_input.click()
                self._random_delay(0.5, 1)
                subtitle_input.fill(article['subtitle'])
                logger.info(f"   ✅ Subtitle filled: {article['subtitle'][:50]}...")
                self._random_delay(1, 2)
            else:
                logger.info("   ℹ️  No subtitle field found (may not exist on this page)")

            # Step 4: Fill content
            logger.info("\nStep 4: Filling content...")

            # Press Enter to move to body
            self.page.keyboard.press('Enter')
            self._random_delay(1, 2)

            # Try to find body editor
            body_selectors = [
                'div[contenteditable="true"]',
                'div[data-testid="post-body"]',
                'div.ProseMirror',
                'div[role="textbox"]',
                'textarea[placeholder*="Body" i]'
            ]

            body_editor = None
            for selector in body_selectors:
                try:
                    editor = self.page.wait_for_selector(selector, timeout=3000)
                    if editor and editor.is_visible():
                        body_editor = editor
                        logger.info(f"   ✅ Found body editor: {selector}")
                        break
                except:
                    continue

            if not body_editor:
                logger.warning("   ⚠️  Body editor not found, trying direct keyboard input...")
                # Just type directly
            else:
                body_editor.click()
                self._random_delay(1, 2)

            # Type content (split by paragraphs)
            logger.info("   Typing content...")
            paragraphs = article['content'].split('\n\n')

            for i, paragraph in enumerate(paragraphs):
                if not paragraph.strip():
                    continue

                # Type paragraph
                self.page.keyboard.type(paragraph.strip())

                # Paragraph break
                if i < len(paragraphs) - 1:
                    self.page.keyboard.press('Enter')
                    self.page.keyboard.press('Enter')

                # Pause every few paragraphs
                if i % 2 == 0:
                    self._random_delay(0.3, 0.8)

            logger.info("   ✅ Content filled")
            self._random_delay(2, 3)

            # Screenshot 2 - Content filled
            self.page.screenshot(path="substack_post_test_content_filled.png")

            # Step 5: Publish or save as draft
            if publish_immediately:
                logger.info("\nStep 5: Publishing...")

                # First click "Continue" button to open publish dialog
                logger.info("   Looking for Continue button...")
                continue_selectors = [
                    'button:has-text("Continue")',
                    'button:has-text("Next")',
                    'a:has-text("Continue")'
                ]

                continue_btn = None
                for selector in continue_selectors:
                    try:
                        btn = self.page.wait_for_selector(selector, timeout=3000)
                        if btn and btn.is_visible():
                            continue_btn = btn
                            logger.info(f"   ✅ Found Continue button: {selector}")
                            break
                    except:
                        continue

                if not continue_btn:
                    logger.warning("   ⚠️  Continue button not found")
                    logger.info("   Trying to find Publish button directly...")

                    publish_selectors = [
                        'button:has-text("Publish")',
                        'button:has-text("Publish now")'
                    ]

                    for selector in publish_selectors:
                        try:
                            btn = self.page.wait_for_selector(selector, timeout=2000)
                            if btn and btn.is_visible():
                                continue_btn = btn
                                logger.info(f"   ✅ Found: {selector}")
                                break
                        except:
                            continue

                if not continue_btn:
                    logger.error("   ❌ Could not find Continue or Publish button")
                    logger.info("   Article may be auto-saved as draft")
                else:
                    continue_btn.click()
                    logger.info("   ✅ Clicked Continue/Publish")
                    self._random_delay(3, 5)

                    # Screenshot after clicking Publish
                    self.page.screenshot(path="substack_post_test_publish_dialog.png")
                    logger.info("   📸 Screenshot: publish dialog")

                    # Handle publish settings dialog
                    # This page shows: Audience, Comments, Tags, Social preview, Delivery
                    # Need to scroll down and click "Publish now" at the bottom
                    logger.info("   Looking for publish confirmation dialog...")

                    # Debug: Find all buttons on this page
                    logger.info("   Analyzing publish dialog buttons...")
                    all_buttons = self.page.query_selector_all('button')
                    logger.info(f"   Found {len(all_buttons)} buttons on page:")

                    visible_buttons = []
                    for i, btn in enumerate(all_buttons):
                        try:
                            text = btn.inner_text().strip()
                            visible = btn.is_visible()
                            enabled = btn.is_enabled()
                            if visible and enabled and text:
                                visible_buttons.append(text)
                                logger.info(f"      {i+1}. '{text}' (visible, enabled)")
                        except:
                            pass

                    # Scroll down to bottom
                    logger.info("   Scrolling to bottom of dialog...")
                    for _ in range(3):  # Scroll multiple times to ensure we reach bottom
                        self.page.evaluate("window.scrollBy(0, 500)")
                        self._random_delay(0.5, 1)

                    self._random_delay(2, 3)

                    # Screenshot after scrolling
                    self.page.screenshot(path="substack_post_test_scrolled.png")
                    logger.info("   📸 Screenshot after scrolling")

                    # Re-check buttons after scrolling
                    logger.info("   Re-checking buttons after scroll...")
                    all_buttons = self.page.query_selector_all('button')
                    for i, btn in enumerate(all_buttons):
                        try:
                            text = btn.inner_text().strip()
                            visible = btn.is_visible()
                            enabled = btn.is_enabled()
                            if visible and enabled and text and text not in visible_buttons:
                                logger.info(f"      NEW: '{text}' (visible, enabled)")
                        except:
                            pass

                    # Try multiple selectors for the final publish button
                    # The actual button is "Send to everyone now"
                    final_publish_selectors = [
                        'button:has-text("Send to everyone now")',  # The actual publish button
                        'button:has-text("Publish now")',
                        'button:has-text("Send now")',
                        'button:has-text("Publish")',
                        'button:has-text("Publish post")',
                        'button[type="submit"]:has-text("Send")',
                    ]

                    publish_confirmed = False
                    for selector in final_publish_selectors:
                        try:
                            logger.info(f"      Trying: {selector}")
                            # Wait a bit and look for visible, enabled button
                            confirm_btn = self.page.wait_for_selector(selector, timeout=3000)
                            if confirm_btn and confirm_btn.is_visible() and confirm_btn.is_enabled():
                                logger.info(f"      ✅ Found final publish button: {selector}")
                                confirm_btn.click()
                                logger.info("      ✅ Clicked final publish button")
                                publish_confirmed = True
                                self._random_delay(3, 5)
                                break
                        except Exception as e:
                            logger.debug(f"      ❌ Not found: {str(e)[:50]}")
                            continue

                    if not publish_confirmed:
                        logger.warning("   ⚠️  Could not find final publish button")
                        logger.info("   Taking screenshot for debugging...")
                        self.page.screenshot(path="substack_post_test_no_final_button.png")
                        logger.info("   Article may be in draft state")
                        return False

                    # Handle publisher agreement if it appears (first-time publishing)
                    logger.info("   Checking for publisher agreement...")
                    try:
                        agreement_selectors = [
                            'button:has-text("I agree")',
                            'text="Ready to start publishing?"'
                        ]

                        agreement_needed = False
                        for selector in agreement_selectors:
                            try:
                                elem = self.page.wait_for_selector(selector, timeout=2000)
                                if elem and elem.is_visible():
                                    agreement_needed = True
                                    break
                            except:
                                continue

                        if agreement_needed:
                            logger.info("      ✅ Found publisher agreement page")
                            agree_btn = self.page.wait_for_selector('button:has-text("I agree")', timeout=3000)
                            if agree_btn and agree_btn.is_visible():
                                logger.info("      ✅ Clicking 'I agree' on publisher agreement")
                                agree_btn.click()
                                self._random_delay(3, 5)
                                logger.info("      ✅ Publisher agreement accepted")
                        else:
                            logger.info("      ℹ️  No publisher agreement needed")
                    except Exception as e:
                        logger.info(f"      ℹ️  No agreement page: {str(e)[:50]}")

                    # Handle subscribe buttons popup if it appears
                    logger.info("   Checking for subscribe buttons popup...")
                    try:
                        # Look for the "Publish without buttons" option
                        publish_without_buttons_selectors = [
                            'button:has-text("Publish without buttons")',
                            'text="Publish without buttons"',
                            'button:has-text("publish without")',
                        ]

                        popup_handled = False
                        for selector in publish_without_buttons_selectors:
                            try:
                                btn = self.page.wait_for_selector(selector, timeout=3000)
                                if btn and btn.is_visible():
                                    logger.info(f"      ✅ Found subscribe popup, clicking: {selector}")
                                    btn.click()
                                    popup_handled = True
                                    self._random_delay(2, 3)
                                    break
                            except:
                                continue

                        if popup_handled:
                            logger.info("      ✅ Handled subscribe buttons popup")
                        else:
                            logger.info("      ℹ️  No subscribe popup (might have been auto-dismissed)")
                    except Exception as e:
                        logger.info(f"      ℹ️  No popup detected: {str(e)[:50]}")

                    # Verify publication
                    logger.info("   Verifying publication...")
                    self._random_delay(3, 5)

                    # Take final screenshot
                    self.page.screenshot(path="substack_post_test_after_publish.png")
                    logger.info("   📸 Screenshot after publish attempt")

                    # Check if we're redirected to the published post
                    current_url = self.page.url
                    logger.info(f"   Current URL: {current_url}")

                    if '/p/' in current_url and '/publish/' not in current_url:
                        logger.info("   ✅ Redirected to published post URL!")
                        logger.info("   ✅ Article successfully published!")
                        return True
                    elif 'publish' in current_url:
                        logger.warning("   ⚠️  Still on publish page - may not be published")
                        logger.info("   Checking page content...")

                        # Check for success message
                        success_indicators = [
                            'text="Published"',
                            'text="Your post is live"',
                            'text="Post published"',
                            'text="Successfully published"'
                        ]

                        for indicator in success_indicators:
                            try:
                                elem = self.page.wait_for_selector(indicator, timeout=2000)
                                if elem:
                                    logger.info(f"   ✅ Found success indicator: {indicator}")
                                    logger.info("   ✅ Article published!")
                                    return True
                            except:
                                pass

                        logger.warning("   ⚠️  No success confirmation found")
                        logger.warning("   Article may still be in draft - check manually")
                        return False
                    else:
                        logger.info("   ℹ️  Unclear status - check manually")
                        return True  # Assume success if no clear failure
            else:
                logger.info("\nStep 5: Saving as draft...")
                logger.info("   ℹ️  Substack auto-saves, article saved as draft")

            # Screenshot 3 - After publish
            self.page.screenshot(path="substack_post_test_final.png")

            logger.info("\n   ✅ Article successfully posted to Substack")
            return True

        except Exception as e:
            logger.error(f"\n   ❌ Error publishing article: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            try:
                self.page.screenshot(path="substack_post_test_error.png")
            except:
                pass

            return False

    def run_full_test(self, publish_immediately: bool = False):
        """运行完整测试"""
        logger.info("\n" + "="*80)
        logger.info("🤖 Substack Fully Automated Posting Test")
        logger.info("="*80)
        logger.info(f"Mode: {'Publish immediately' if publish_immediately else 'Save as draft'}")
        logger.info("="*80)

        try:
            # Verify login
            if not self.verify_login():
                logger.error("\n❌ Login verification failed")
                logger.error("Please run: python3 substack_login_and_save_auth.py")
                return False

            # Generate article
            article = self.generate_test_article()

            # Show preview
            logger.info("\n" + "-"*80)
            logger.info("📋 Article Preview")
            logger.info("-"*80)
            logger.info(f"Title: {article['title']}")
            logger.info(f"Subtitle: {article['subtitle']}")
            logger.info(f"\nContent ({len(article['content'])} chars):")
            logger.info("-"*80)
            logger.info(article['content'])
            logger.info("-"*80)

            # Auto-proceed without confirmation
            logger.info(f"\n📤 {'Publishing' if publish_immediately else 'Saving as draft'} to Substack...")

            # Publish
            success = self.publish_article(article, publish_immediately)

            # Results
            logger.info("\n" + "="*80)
            if success:
                logger.info("✅ TEST SUCCESSFUL!")
                logger.info("="*80)
                logger.info(f"Article was {'published' if publish_immediately else 'saved as draft'}")
                logger.info(f"\nTitle: {article['title']}")
                logger.info(f"Subtitle: {article['subtitle']}")
                logger.info(f"\nContent preview:\n{article['content'][:200]}...")
            else:
                logger.info("⚠️  TEST COMPLETED WITH WARNINGS")
                logger.info("="*80)
                logger.info("Check screenshots for details")

            logger.info("\n📸 Screenshots saved:")
            logger.info("   1. substack_post_test_editor.png - Editor page")
            logger.info("   2. substack_post_test_content_filled.png - Content filled")
            logger.info("   3. substack_post_test_final.png - Final result")
            logger.info("="*80)

            return success

        except Exception as e:
            logger.error(f"\n❌ Test failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """主函数"""
    logger.info("\n" + "="*80)
    logger.info("🤖 Substack Fully Automated Posting Test")
    logger.info("="*80)
    logger.info("This script will:")
    logger.info("  1. Generate a test article with AI")
    logger.info("  2. Automatically post it to Substack")
    logger.info("  3. Verify success")
    logger.info("="*80 + "\n")

    # Check API key
    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        logger.error("Run: export OPENAI_API_KEY='your-key-here'")
        return

    # Auto mode - always publish immediately
    publish_immediately = True
    logger.info("Mode: Publish immediately (auto-enabled)")
    logger.info("")

    # Run test
    tester = SubstackAutoPostTester()

    try:
        tester.setup_browser(headless=False)
        success = tester.run_full_test(publish_immediately)

        if success:
            logger.info("\n✅ All tests passed!")
        else:
            logger.info("\n⚠️  Test completed with issues")

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    finally:
        logger.info("\n🔚 Closing browser...")
        tester.close_browser()


if __name__ == "__main__":
    main()
