"""
HackerNews Platform Integration
"""

from typing import List, Optional
from distroflow.platforms.base import BasePlatform, PlatformCapability, AuthConfig, PostResult
from distroflow.core.browser_manager import BrowserManager


class HackerNewsPlatform(BasePlatform):
    """HackerNews platform implementation."""

    def __init__(self):
        super().__init__("hackernews")
        self.base_url = "https://news.ycombinator.com"
        self.browser_manager: Optional[BrowserManager] = None

    async def setup_auth(self, auth_config: AuthConfig) -> bool:
        """Setup HN authentication."""
        try:
            self.browser_manager = BrowserManager(headless=False)
            await self.browser_manager.start()

            # Load cookies
            if auth_config.auth_type == "cookies":
                await self.browser_manager.load_cookies(
                    auth_config.credentials.get("cookie_path", "hackernews_auth.json")
                )

            # Verify by checking for user link
            await self.browser_manager.page.goto(self.base_url)
            await self.browser_manager.wait_for_navigation()

            user_link = await self.browser_manager.page.query_selector('a[href^="user?id="]')

            if user_link:
                self._authenticated = True
                self.logger.info("✅ HackerNews authentication successful")
                return True
            else:
                self.logger.error("❌ HackerNews authentication failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ HN auth error: {e}")
            return False

    async def post(
        self,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        media: Optional[List[str]] = None,
        **kwargs,
    ) -> PostResult:
        """Submit to HackerNews."""
        if not self._authenticated:
            return PostResult(success=False, platform="hackernews", error="Not authenticated")

        # Ensure title has "Show HN:" or "Ask HN:" prefix
        if title and not title.startswith(("Show HN:", "Ask HN:")):
            if url:
                title = f"Show HN: {title}"
            else:
                title = f"Ask HN: {title}"

        try:
            page = self.browser_manager.page

            # Go to submit page
            await page.goto(f"{self.base_url}/submit")
            await self.browser_manager.wait_for_navigation()

            # Fill title
            await page.wait_for_selector('input[name="title"]')
            await self.browser_manager.human_type('input[name="title"]', title)
            await self.browser_manager.human_delay(1000, 2000)

            # Fill URL or text
            if url:
                await page.wait_for_selector('input[name="url"]')
                await self.browser_manager.human_type('input[name="url"]', url)
            else:
                # Switch to text mode
                text_link = await page.query_selector('a:has-text("text")')
                if text_link:
                    await text_link.click()
                    await self.browser_manager.human_delay(1000, 2000)

                text_area = await page.wait_for_selector('textarea[name="text"]')
                await text_area.click()
                await page.keyboard.type(content)

            await self.browser_manager.human_delay(2000, 3000)

            # Submit
            submit_button = await page.wait_for_selector('input[type="submit"]')
            await submit_button.click()

            await self.browser_manager.human_delay(3000, 5000)

            self.logger.info("✅ Posted to HackerNews successfully")
            return PostResult(
                success=True, platform="hackernews", metadata={"title": title, "url": url}
            )

        except Exception as e:
            self.logger.error(f"❌ HN posting failed: {e}")
            return PostResult(success=False, platform="hackernews", error=str(e))

    def get_capabilities(self) -> List[PlatformCapability]:
        """Get HN capabilities."""
        return [
            PlatformCapability.POST,
            PlatformCapability.COMMENT,
        ]

    async def cleanup(self):
        """Cleanup resources."""
        if self.browser_manager:
            await self.browser_manager.close()
