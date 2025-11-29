"""
Twitter Web Scraper - Playwright Version with Persistent Login
使用 Playwright 和保存的登录态爬取 Twitter 粉丝
"""

import os
import re
import time
import random
import logging
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TwitterPlaywrightScraper:
    """Twitter scraper using Playwright with persistent authentication"""

    def __init__(self, headless: bool = False, auth_file: str = "auth.json"):
        """
        Initialize scraper with Playwright

        Args:
            headless: Run browser in headless mode
            auth_file: Path to saved authentication state file
        """
        self.headless = headless
        self.auth_file = auth_file
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Check if auth file exists
        if not os.path.exists(auth_file):
            logger.warning(f"⚠️  Authentication file '{auth_file}' not found!")
            logger.warning("Please run 'python login_and_save_auth.py' first to save your login state.")
            raise FileNotFoundError(f"Authentication file '{auth_file}' not found. Run login_and_save_auth.py first.")

    def start(self):
        """Start Playwright browser with saved authentication"""
        logger.info("🚀 Starting Playwright browser...")

        self.playwright = sync_playwright().start()

        # Launch browser with anti-detection
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox'
            ]
        )

        # Create context with saved authentication state
        logger.info(f"🔐 Loading authentication from {self.auth_file}...")
        self.context = self.browser.new_context(
            storage_state=self.auth_file,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Create page
        self.page = self.context.new_page()

        # Inject anti-detection script
        self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override plugins and languages
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });

            // Override chrome property
            window.chrome = {
                runtime: {}
            };

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        logger.info("✓ Browser started with saved authentication")

    def close(self):
        """Close browser and cleanup"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("✓ Browser closed")

    def _human_like_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _random_mouse_movement(self, page: Page):
        """Simulate random mouse movements like a human"""
        # Move mouse to random positions
        for _ in range(random.randint(1, 3)):
            x = random.randint(100, 1200)
            y = random.randint(100, 800)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))

    def _human_scroll(self, page: Page):
        """Scroll like a human - irregular, with pauses"""
        # Humans don't scroll smoothly - they scroll, pause, read, scroll more

        # Sometimes scroll a little
        if random.random() < 0.3:
            scroll = random.randint(100, 300)
        # Sometimes scroll medium
        elif random.random() < 0.7:
            scroll = random.randint(300, 600)
        # Sometimes scroll a lot
        else:
            scroll = random.randint(600, 1000)

        # Scroll in steps (humans don't scroll in one motion)
        steps = random.randint(2, 5)
        scroll_per_step = scroll // steps

        for _ in range(steps):
            page.evaluate(f"window.scrollBy({{top: {scroll_per_step}, behavior: 'smooth'}})")
            time.sleep(random.uniform(0.05, 0.15))

        # Pause to "read" content
        reading_pause = random.uniform(0.8, 2.5)
        time.sleep(reading_pause)

        # Sometimes scroll back up a bit (like re-reading)
        if random.random() < 0.15:
            scroll_back = random.randint(-200, -50)
            page.evaluate(f"window.scrollBy({{top: {scroll_back}, behavior: 'smooth'}})")
            time.sleep(random.uniform(0.3, 0.8))

    def _simulate_reading(self, text_length: int):
        """Simulate time spent reading based on text length"""
        # Average reading speed: 200-250 words per minute
        # Average word length: 5 characters
        words = text_length / 5
        reading_time = (words / 225) * 60  # seconds

        # Add randomness (some people read faster/slower)
        reading_time *= random.uniform(0.7, 1.3)

        # But don't spend too long on any single item
        reading_time = min(reading_time, 3.0)

        # At least glance at it
        reading_time = max(reading_time, 0.5)

        time.sleep(reading_time)

    def _random_pause(self):
        """Occasionally pause like a human getting distracted"""
        if random.random() < 0.1:  # 10% chance of distraction
            pause_type = random.choice(['short', 'medium', 'long'])
            if pause_type == 'short':
                # Quick distraction (2-5 seconds)
                time.sleep(random.uniform(2, 5))
                logger.info("⏸️  Quick pause...")
            elif pause_type == 'medium':
                # Medium distraction (5-10 seconds)
                time.sleep(random.uniform(5, 10))
                logger.info("⏸️  Taking a short break...")
            else:
                # Longer break (10-20 seconds) - rare
                if random.random() < 0.3:  # Only 3% of all pauses
                    time.sleep(random.uniform(10, 20))
                    logger.info("⏸️  Taking a breather...")

    def _scroll_page(self, page: Page, scrolls: int = 3):
        """Scroll page like a human - DEPRECATED, use _human_scroll instead"""
        for i in range(scrolls):
            self._human_scroll(page)

    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email from text using regex"""
        if not text:
            return None

        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)

        return matches[0] if matches else None

    def get_followers(
        self,
        username: str,
        max_followers: int = 100,
        extract_emails: bool = True
    ) -> List[Dict[str, str]]:
        """
        Scrape followers from a Twitter user

        Args:
            username: Target Twitter username (without @)
            max_followers: Maximum number of followers to scrape
            extract_emails: Whether to extract emails from bios

        Returns:
            List of follower dictionaries with username, name, bio, email, etc.
        """
        if not self.page:
            self.start()

        followers = []
        url = f"https://twitter.com/{username}/followers"

        logger.info(f"🔍 Navigating to: {url}")

        try:
            # Navigate to followers page (use domcontentloaded instead of networkidle)
            # Twitter has many background requests, networkidle is too strict
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # Humans take time to let page render before interacting
            time.sleep(random.uniform(1.5, 3.0))

            # Wait for the page to load more content (like a human waiting)
            logger.info("⏳ Waiting for content to load...")
            initial_wait = random.uniform(3, 6)  # Humans wait different amounts
            time.sleep(initial_wait)

            # Move mouse around like exploring the page
            self._random_mouse_movement(self.page)

            # Check if we're logged in by looking for key elements
            if "login" in self.page.url.lower():
                logger.error("❌ Not logged in! Your auth.json may have expired.")
                logger.error("Please run 'python login_and_save_auth.py' again.")
                return []

            logger.info(f"✓ Page loaded successfully")

            # Wait for follower cells to appear
            logger.info("⏳ Waiting for follower list to appear...")
            try:
                self.page.wait_for_selector('[data-testid="UserCell"]', timeout=15000)
                logger.info("✓ Follower cells found")

                # Simulate looking at the page
                time.sleep(random.uniform(1, 2))
                self._random_mouse_movement(self.page)

            except Exception as e:
                logger.warning(f"⚠️  Could not find follower cells with primary selector, trying alternatives...")
                # Try waiting for any content
                time.sleep(3)

            logger.info(f"📊 Scraping up to {max_followers} followers...")

            # Scroll and collect followers
            scroll_attempts = 0
            max_scroll_attempts = max_followers // 5 + 10  # More scrolling attempts
            no_new_followers_count = 0

            while len(followers) < max_followers and scroll_attempts < max_scroll_attempts:
                # Random pause - simulate getting distracted
                self._random_pause()

                # Move mouse occasionally
                if random.random() < 0.3:  # 30% chance
                    self._random_mouse_movement(self.page)

                # Find all follower cells - try multiple selectors
                follower_cells = self.page.query_selector_all('[data-testid="UserCell"]')

                if not follower_cells:
                    # Try alternative selectors
                    follower_cells = self.page.query_selector_all('div[data-testid="cellInnerDiv"]')

                if not follower_cells:
                    # Try even more general selector
                    follower_cells = self.page.query_selector_all('article[role="article"]')

                logger.info(f"🔍 Found {len(follower_cells)} cells on page")

                current_count = len(followers)

                # Extract data from each cell
                for cell in follower_cells:
                    if len(followers) >= max_followers:
                        break

                    try:
                        # Extract username - try multiple strategies
                        follower_username = None

                        # Strategy 1: Find link with @
                        username_link = cell.query_selector('a[href^="/"][role="link"]')
                        if username_link:
                            href = username_link.get_attribute('href')
                            if href and href.startswith('/'):
                                follower_username = href.split('/')[1].split('?')[0]

                        # Strategy 2: Find span with @ symbol
                        if not follower_username:
                            spans = cell.query_selector_all('span')
                            for span in spans:
                                text = span.inner_text()
                                if text.startswith('@'):
                                    follower_username = text[1:]  # Remove @
                                    break

                        # Skip if no username found
                        if not follower_username:
                            continue

                        # Skip if we already have this follower
                        if any(f.get('username') == follower_username for f in followers):
                            continue

                        # Extract display name - look for spans without @
                        follower_name = follower_username
                        name_spans = cell.query_selector_all('span')
                        for span in name_spans:
                            text = span.inner_text()
                            if text and not text.startswith('@') and len(text) > 1 and len(text) < 50:
                                follower_name = text
                                break

                        # Extract bio - look for user description
                        bio = ""
                        bio_selectors = [
                            '[data-testid="UserDescription"]',
                            'div[dir="auto"]',
                            '[data-testid="UserBio"]'
                        ]
                        for selector in bio_selectors:
                            bio_elem = cell.query_selector(selector)
                            if bio_elem:
                                bio = bio_elem.inner_text()
                                break

                        # Extract email from bio if requested
                        email = None
                        if extract_emails and bio:
                            email = self._extract_email_from_text(bio)

                        # Build profile URL
                        profile_url = f"https://twitter.com/{follower_username}"

                        follower_data = {
                            'username': follower_username,
                            'name': follower_name,
                            'bio': bio,
                            'email': email,
                            'profile_url': profile_url,
                            'scraped_at': datetime.now().isoformat()
                        }

                        followers.append(follower_data)

                        # Simulate reading the profile (based on bio length)
                        text_to_read = f"{follower_name} {bio}"
                        self._simulate_reading(len(text_to_read))

                        # Log progress
                        email_indicator = f"- {email}" if email else ""
                        logger.info(f"✓ [{len(followers)}/{max_followers}] @{follower_username} {email_indicator}")

                    except Exception as e:
                        logger.debug(f"Error extracting follower data: {e}")
                        continue

                # Check if we got new followers
                new_followers = len(followers) - current_count
                if new_followers == 0:
                    no_new_followers_count += 1
                    if no_new_followers_count >= 3:
                        logger.info("⏸️  No new followers found after multiple scrolls, stopping...")
                        break
                else:
                    no_new_followers_count = 0

                # Scroll to load more
                if len(followers) < max_followers:
                    logger.info(f"📜 Scrolling to load more... (Current: {len(followers)}/{max_followers})")

                    # Human-like scrolling
                    scroll_count = random.randint(1, 3)
                    for _ in range(scroll_count):
                        self._human_scroll(self.page)

                        # Sometimes hover over a profile (without clicking)
                        if random.random() < 0.2:  # 20% chance
                            self._random_mouse_movement(self.page)
                            time.sleep(random.uniform(0.5, 1.5))

                    scroll_attempts += 1

            logger.info(f"✅ Scraped {len(followers)} followers total")

            if extract_emails:
                emails_found = sum(1 for f in followers if f.get('email'))
                logger.info(f"📧 Found {emails_found} emails ({emails_found/len(followers)*100:.1f}%)")

            return followers

        except Exception as e:
            logger.error(f"❌ Error scraping followers: {e}")
            import traceback
            traceback.print_exc()
            return followers

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    # Test the scraper
    with TwitterPlaywrightScraper(headless=False) as scraper:
        followers = scraper.get_followers(
            username="elonmusk",
            max_followers=20,
            extract_emails=True
        )

        print("\n" + "=" * 60)
        print(f"Total followers scraped: {len(followers)}")

        if followers:
            print("\nSample followers:")
            for i, f in enumerate(followers[:5], 1):
                email = f.get('email', 'No email')
                print(f"{i}. @{f['username']} - {email}")
