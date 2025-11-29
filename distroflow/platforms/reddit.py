"""
Reddit Platform Integration
"""

from typing import List, Optional
from distroflow.platforms.base import BasePlatform, PlatformCapability, AuthConfig, PostResult
from distroflow.core.browser_manager import BrowserManager


class RedditPlatform(BasePlatform):
    """Reddit platform implementation using browser automation."""

    def __init__(self):
        super().__init__("reddit")
        self.base_url = "https://www.reddit.com"
        self.browser_manager: Optional[BrowserManager] = None

    async def setup_auth(self, auth_config: AuthConfig) -> bool:
        """Setup Reddit authentication using cookies."""
        try:
            self.browser_manager = BrowserManager(headless=False)
            await self.browser_manager.start()

            # Load cookies
            if auth_config.auth_type == "cookies":
                await self.browser_manager.load_cookies(
                    auth_config.credentials.get("cookie_path", "reddit_auth.json")
                )

            # Verify authentication
            await self.browser_manager.page.goto(self.base_url)
            await self.browser_manager.wait_for_navigation()

            # Check for user menu (indicates logged in)
            user_menu = await self.browser_manager.page.query_selector(
                '[id*="user-menu"], button[id*="user"]'
            )

            if user_menu:
                self._authenticated = True
                self.logger.info("✅ Reddit authentication successful")
                return True
            else:
                self.logger.error("❌ Reddit authentication failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Reddit auth error: {e}")
            return False

    async def post(
        self,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        media: Optional[List[str]] = None,
        subreddit: str = "test",
        **kwargs,
    ) -> PostResult:
        """Post to a subreddit."""
        if not self._authenticated:
            return PostResult(success=False, platform="reddit", error="Not authenticated")

        if not title:
            # Extract title from first line
            lines = content.split("\n")
            title = lines[0][:300]
            content = "\n".join(lines[1:])

        try:
            page = self.browser_manager.page

            # Go to submit page
            submit_url = f"{self.base_url}/r/{subreddit}/submit"
            await page.goto(submit_url)
            await self.browser_manager.wait_for_navigation()

            # Fill title
            await page.wait_for_selector('textarea[name="title"]')
            await self.browser_manager.human_type('textarea[name="title"]', title)
            await self.browser_manager.human_delay(1000, 2000)

            # Fill content
            content_area = await page.wait_for_selector('div[contenteditable="true"]')
            await content_area.click()
            await self.browser_manager.human_delay(500, 1000)
            await page.keyboard.type(content)

            await self.browser_manager.human_delay(2000, 3000)

            # Submit post
            submit_button = await page.wait_for_selector('button:has-text("Post")')
            await submit_button.click()

            await self.browser_manager.human_delay(3000, 5000)

            self.logger.info(f"✅ Posted to r/{subreddit} successfully")
            return PostResult(
                success=True, platform="reddit", metadata={"subreddit": subreddit, "title": title}
            )

        except Exception as e:
            self.logger.error(f"❌ Reddit posting failed: {e}")
            return PostResult(success=False, platform="reddit", error=str(e))

    def get_capabilities(self) -> List[PlatformCapability]:
        """Get Reddit capabilities."""
        return [
            PlatformCapability.POST,
            PlatformCapability.COMMENT,
            PlatformCapability.SEARCH,
        ]

    async def cleanup(self):
        """Cleanup resources."""
        if self.browser_manager:
            await self.browser_manager.close()
