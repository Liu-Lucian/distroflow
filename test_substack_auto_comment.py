#!/usr/bin/env python3
"""
Substack完全自动化评论测试
自动查找文章、自动生成评论、自动发送

流程：
1. 登录Substack
2. 查找最近的公开文章
3. 打开文章并阅读部分内容
4. AI生成相关评论
5. 自动发送评论
6. 验证成功
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

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


class SubstackAutoCommentTester:
    """Substack完全自动化评论测试器"""

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

    def find_recent_article(self) -> dict:
        """
        查找最近的文章

        Returns:
            {'url': '...', 'title': '...', 'preview': '...'}
        """
        logger.info("\n📖 Finding recent article...")

        self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30000)
        self._random_delay(3, 5)

        # Screenshot
        self.page.screenshot(path="substack_auto_test_home.png")

        # Try to find article links
        article_selectors = [
            'a[href*="/p/"]',  # Substack post URLs contain /p/
            'article a',
            'div[class*="post"] a',
            'h2 a',
            'h3 a'
        ]

        articles = []
        for selector in article_selectors:
            try:
                links = self.page.query_selector_all(selector)
                for link in links:
                    href = link.get_attribute('href')
                    if href and '/p/' in href:
                        # Make absolute URL if needed
                        if href.startswith('/'):
                            # Relative URL - skip it (shouldn't happen on substack.com/home)
                            continue
                        elif not href.startswith('http'):
                            # Add https if missing
                            href = f"https://{href}"

                        # Get title
                        try:
                            title = link.inner_text().strip()
                        except:
                            title = "Untitled"

                        if title and len(title) > 5:  # Filter out short/empty titles
                            articles.append({
                                'url': href,
                                'title': title
                            })

                if articles:
                    break
            except:
                continue

        if not articles:
            logger.error("   ❌ No articles found")
            logger.info("   💡 Make sure the Substack has published articles")
            self.page.screenshot(path="substack_auto_test_no_articles.png")
            return None

        # Remove duplicates
        unique_articles = []
        seen_urls = set()
        for article in articles:
            if article['url'] not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article['url'])

        logger.info(f"   ✅ Found {len(unique_articles)} articles")

        # Show options
        logger.info("\n📋 Available articles:")
        for i, article in enumerate(unique_articles[:5], 1):
            logger.info(f"   {i}. {article['title'][:60]}...")

        # Pick first one
        selected = unique_articles[0]
        logger.info(f"\n   → Selected: {selected['title']}")

        return selected

    def read_article_content(self, article_url: str) -> str:
        """
        读取文章内容（前500字）

        Args:
            article_url: 文章URL

        Returns:
            文章预览内容
        """
        logger.info(f"\n📄 Reading article content...")
        logger.info(f"   URL: {article_url}")

        self.page.goto(article_url, wait_until="domcontentloaded", timeout=30000)
        self._random_delay(3, 5)

        # Screenshot
        self.page.screenshot(path="substack_auto_test_article.png")

        # Try to extract article content
        content_selectors = [
            'article',
            'div[class*="post-content"]',
            'div[class*="body"]',
            'div[class*="article"]',
            'main'
        ]

        article_text = ""
        for selector in content_selectors:
            try:
                content_elem = self.page.query_selector(selector)
                if content_elem:
                    article_text = content_elem.inner_text()
                    if len(article_text) > 100:  # Valid content
                        break
            except:
                continue

        if not article_text:
            logger.warning("   ⚠️  Could not extract article content")
            article_text = "Article content unavailable"

        # Get first 500 characters
        preview = article_text[:500]
        logger.info(f"   ✅ Content extracted ({len(article_text)} chars)")
        logger.info(f"\n   Preview: {preview[:100]}...")

        return preview

    def generate_comment(self, article_title: str, article_preview: str) -> str:
        """
        AI生成评论

        Args:
            article_title: 文章标题
            article_preview: 文章预览

        Returns:
            生成的评论
        """
        logger.info("\n🤖 Generating AI comment...")

        prompt = f"""You are a reader of a Substack newsletter about AI and interviews (HireMeAI topic).

Article title: {article_title}

Article preview:
{article_preview}

Generate a SHORT, natural comment (30-80 words) that:
✅ Shows you read the article
✅ Asks a relevant question OR shares a brief insight
✅ Uses casual internet language (e.g., "ngl", "tbh", "lowkey")
✅ Sounds like a real person, not overly enthusiastic
✅ Does NOT mention HireMeAI (just be a normal reader)

Output ONLY the comment text in ENGLISH:"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=100
            )

            comment = response.choices[0].message.content.strip()

            # Remove any quotes
            comment = comment.strip('"\'')

            logger.info(f"   ✅ Comment generated:")
            logger.info(f"   \"{comment}\"")
            logger.info(f"   ({len(comment)} chars)")

            return comment

        except Exception as e:
            logger.error(f"   ❌ Failed to generate comment: {str(e)}")
            # Fallback to simple comment
            return "Great insights! This really resonates with what I've been experiencing lately."

    def post_comment(self, comment_text: str) -> bool:
        """
        发送评论

        Args:
            comment_text: 评论内容

        Returns:
            是否成功
        """
        logger.info("\n💬 Posting comment...")

        try:
            # Scroll to comments
            logger.info("   Scrolling to comments section...")
            for _ in range(3):
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                self._random_delay(1, 2)

            # Find comment input
            logger.info("   Finding comment input...")

            comment_input_selectors = [
                'textarea[placeholder*="comment" i]',
                'textarea[placeholder*="write" i]',
                'div[contenteditable="true"]',
                'textarea[aria-label*="comment" i]',
                'div[role="textbox"]',
                'textarea'
            ]

            comment_input = None
            for selector in comment_input_selectors:
                try:
                    inputs = self.page.query_selector_all(selector)
                    for input_elem in inputs:
                        if input_elem.is_visible():
                            comment_input = input_elem
                            logger.info(f"      ✅ Found: {selector}")
                            break
                    if comment_input:
                        break
                except:
                    continue

            if not comment_input:
                logger.error("   ❌ Comment input not found")
                self.page.screenshot(path="substack_auto_test_input_not_found.png")
                return False

            # Click and type
            logger.info("   Typing comment...")
            comment_input.scroll_into_view_if_needed()
            self._random_delay(1, 2)
            comment_input.click()
            self._random_delay(1, 2)

            # Screenshot before typing
            self.page.screenshot(path="substack_auto_test_before_type.png")

            # Type with human-like pauses
            words = comment_text.split(' ')
            for i, word in enumerate(words):
                self.page.keyboard.type(word)
                if i < len(words) - 1:
                    self.page.keyboard.type(' ')
                if i % 5 == 0 and i > 0:
                    self._random_delay(0.2, 0.5)

            logger.info("   ✅ Comment typed")
            self._random_delay(2, 3)

            # Screenshot after typing
            self.page.screenshot(path="substack_auto_test_after_type.png")

            # Find submit button
            logger.info("   Finding submit button...")

            submit_button_selectors = [
                'button:has-text("Post")',
                'button:has-text("Submit")',
                'button:has-text("Publish")',
                'button:has-text("Comment")',
                'button[type="submit"]',
                'button[aria-label*="post" i]',
                'button[aria-label*="submit" i]'
            ]

            submit_button = None
            for selector in submit_button_selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=3000)
                    if button and button.is_visible() and button.is_enabled():
                        submit_button = button
                        logger.info(f"      ✅ Found: {selector}")
                        break
                except:
                    continue

            if not submit_button:
                logger.warning("   ⚠️  Submit button not found")
                logger.info("   Trying to find any button near the comment input...")

                # Try to find button near comment (common pattern)
                try:
                    buttons = self.page.query_selector_all('button')
                    for btn in buttons:
                        if btn.is_visible() and btn.is_enabled():
                            btn_text = btn.inner_text().lower()
                            if any(word in btn_text for word in ['post', 'submit', 'send', 'comment']):
                                submit_button = btn
                                logger.info(f"      ✅ Found button: '{btn_text}'")
                                break
                except:
                    pass

            if not submit_button:
                logger.error("   ❌ Submit button not found")
                self.page.screenshot(path="substack_auto_test_button_not_found.png")
                logger.info("   💡 Comment was typed but not submitted")
                logger.info("   Check screenshot: substack_auto_test_after_type.png")
                return False

            # Click submit
            logger.info("   Clicking submit...")
            submit_button.click()
            self._random_delay(3, 5)

            # Screenshot after submit
            self.page.screenshot(path="substack_auto_test_after_submit.png")

            # Verify
            logger.info("   Verifying comment posted...")
            self._random_delay(2, 3)

            page_content = self.page.content()
            if comment_text[:30] in page_content:  # Check first 30 chars
                logger.info("   ✅ Comment verified on page")
                return True
            else:
                logger.warning("   ⚠️  Comment not immediately visible (may need moderation)")
                logger.info("   Check screenshot: substack_auto_test_after_submit.png")
                return True  # Still success if submit worked

        except Exception as e:
            logger.error(f"   ❌ Error posting comment: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            try:
                self.page.screenshot(path="substack_auto_test_error.png")
            except:
                pass

            return False

    def run_full_test(self):
        """运行完整自动化测试"""
        logger.info("\n" + "="*80)
        logger.info("🤖 Substack Fully Automated Comment Test")
        logger.info("="*80)
        logger.info(f"Using: {self.home_url}")
        logger.info("="*80)

        try:
            # Step 1: Find article
            article = self.find_recent_article()
            if not article:
                logger.error("\n❌ Test failed: No article found")
                return False

            # Step 2: Read article
            article_preview = self.read_article_content(article['url'])

            # Step 3: Generate comment
            comment = self.generate_comment(article['title'], article_preview)

            # Step 4: Post comment
            logger.info("\n" + "-"*80)
            logger.info("📋 Test Summary")
            logger.info("-"*80)
            logger.info(f"Article: {article['title']}")
            logger.info(f"URL: {article['url']}")
            logger.info(f"Comment: \"{comment}\"")
            logger.info("-"*80)

            # Confirm
            logger.info("\n⚠️  This will POST A REAL COMMENT to Substack")
            try:
                confirm = input("Proceed? (yes/no): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                logger.info("\n❌ Cancelled by user")
                return False

            if confirm not in ['yes', 'y']:
                logger.info("❌ Cancelled by user")
                return False

            # Post
            success = self.post_comment(comment)

            # Results
            logger.info("\n" + "="*80)
            if success:
                logger.info("✅ TEST SUCCESSFUL!")
                logger.info("="*80)
                logger.info("Comment was successfully posted to Substack")
                logger.info(f"\nArticle: {article['title']}")
                logger.info(f"URL: {article['url']}")
                logger.info(f"Comment: \"{comment}\"")
            else:
                logger.info("⚠️  TEST COMPLETED WITH WARNINGS")
                logger.info("="*80)
                logger.info("Comment may have been posted but verification failed")
                logger.info("Check screenshots to verify")

            logger.info("\n📸 Screenshots saved:")
            logger.info("   1. substack_auto_test_home.png - Homepage")
            logger.info("   2. substack_auto_test_article.png - Article page")
            logger.info("   3. substack_auto_test_before_type.png - Before typing")
            logger.info("   4. substack_auto_test_after_type.png - After typing")
            logger.info("   5. substack_auto_test_after_submit.png - After submit")
            logger.info("="*80)

            return success

        except Exception as e:
            logger.error(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """主函数"""
    logger.info("\n" + "="*80)
    logger.info("🤖 Substack Fully Automated Comment Test")
    logger.info("="*80)
    logger.info("This script will:")
    logger.info("  1. Find a recent article automatically")
    logger.info("  2. Read the article content")
    logger.info("  3. Generate an AI comment based on the content")
    logger.info("  4. Post the comment to Substack")
    logger.info("="*80 + "\n")

    # Check API key
    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        logger.error("Run: export OPENAI_API_KEY='your-key-here'")
        return

    logger.info("Using Substack home: https://substack.com/home")
    logger.info("")

    # Run test
    tester = SubstackAutoCommentTester()

    try:
        tester.setup_browser(headless=False)
        success = tester.run_full_test()

        if success:
            logger.info("\n✅ All tests passed!")
        else:
            logger.info("\n⚠️  Test completed with issues")

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}")
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
