"""
Twitter Platform Integration
"""

from typing import List, Optional
from distroflow.platforms.base import BasePlatform, PlatformCapability, AuthConfig, PostResult
from distroflow.core.browser_manager import BrowserManager


class TwitterPlatform(BasePlatform):
    """Twitter platform implementation using browser automation."""

    def __init__(self):
        super().__init__("twitter")
        self.home_url = "https://twitter.com/home"
        self.browser_manager: Optional[BrowserManager] = None

    async def setup_auth(self, auth_config: AuthConfig) -> bool:
        """Setup Twitter authentication using cookies."""
        try:
            self.browser_manager = BrowserManager(headless=False)
            await self.browser_manager.start()

            # Load cookies from auth config
            if auth_config.auth_type == "cookies":
                await self.browser_manager.load_cookies(
                    auth_config.credentials.get("cookie_path", "auth.json")
                )

            # Verify authentication
            await self.browser_manager.page.goto(self.home_url)
            await self.browser_manager.wait_for_navigation()

            # Check if logged in (look for tweet button)
            tweet_button = await self.browser_manager.page.query_selector(
                'a[data-testid="SideNav_NewTweet_Button"]'
            )

            if tweet_button:
                self._authenticated = True
                self.logger.info("✅ Twitter authentication successful")
                return True
            else:
                self.logger.error("❌ Twitter authentication failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Twitter auth error: {e}")
            return False

    async def post(
        self,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        media: Optional[List[str]] = None,
        **kwargs,
    ) -> PostResult:
        """Post a tweet."""
        if not self._authenticated:
            return PostResult(success=False, platform="twitter", error="Not authenticated")

        try:
            page = self.browser_manager.page

            # Click new tweet button
            tweet_button = await page.wait_for_selector('a[data-testid="SideNav_NewTweet_Button"]')
            await tweet_button.click()
            await self.browser_manager.human_delay(1000, 2000)

            # Type tweet
            await page.wait_for_selector('div[data-testid="tweetTextarea_0"]')
            await self.browser_manager.human_type(
                'div[data-testid="tweetTextarea_0"]', content
            )
            await self.browser_manager.human_delay(1000, 2000)

            # Upload media if provided
            if media:
                # Implementation for media upload
                pass

            # Click tweet button
            post_button = await page.wait_for_selector('button[data-testid="tweetButtonInline"]')
            await post_button.click()

            await self.browser_manager.human_delay(2000, 3000)

            self.logger.info("✅ Tweet posted successfully")
            return PostResult(
                success=True, platform="twitter", metadata={"content_length": len(content)}
            )

        except Exception as e:
            self.logger.error(f"❌ Tweet posting failed: {e}")
            return PostResult(success=False, platform="twitter", error=str(e))

    def get_capabilities(self) -> List[PlatformCapability]:
        """Get Twitter capabilities."""
        return [
            PlatformCapability.POST,
            PlatformCapability.COMMENT,
            PlatformCapability.DM,
            PlatformCapability.MEDIA,
        ]

    async def cleanup(self):
        """Cleanup resources."""
        if self.browser_manager:
            await self.browser_manager.close()
