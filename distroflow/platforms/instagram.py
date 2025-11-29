"""
Instagram Platform Integration
"""

from typing import List, Optional
from distroflow.platforms.base import BasePlatform, PlatformCapability, AuthConfig, PostResult
from distroflow.core.browser_manager import BrowserManager


class InstagramPlatform(BasePlatform):
    """Instagram platform implementation."""

    def __init__(self):
        super().__init__("instagram")
        self.base_url = "https://www.instagram.com"
        self.browser_manager: Optional[BrowserManager] = None

    async def setup_auth(self, auth_config: AuthConfig) -> bool:
        """Setup Instagram authentication."""
        try:
            self.browser_manager = BrowserManager(headless=False)
            await self.browser_manager.start()

            # Load cookies (Instagram uses sessionid)
            if auth_config.auth_type == "cookies":
                await self.browser_manager.load_cookies(
                    auth_config.credentials.get("cookie_path", "platforms_auth.json")
                )

            # Verify authentication
            await self.browser_manager.page.goto(self.base_url)
            await self.browser_manager.wait_for_navigation()

            # Check for profile icon (indicates logged in)
            profile_link = await self.browser_manager.page.query_selector(
                'a[href*="/accounts/edit/"]'
            )

            if profile_link:
                self._authenticated = True
                self.logger.info("✅ Instagram authentication successful")
                return True
            else:
                self.logger.error("❌ Instagram authentication failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Instagram auth error: {e}")
            return False

    async def post(
        self,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        media: Optional[List[str]] = None,
        **kwargs,
    ) -> PostResult:
        """Post to Instagram (requires media)."""
        if not self._authenticated:
            return PostResult(success=False, platform="instagram", error="Not authenticated")

        if not media:
            return PostResult(
                success=False, platform="instagram", error="Instagram posts require media"
            )

        try:
            page = self.browser_manager.page

            # Click create button
            create_button = await page.wait_for_selector('svg[aria-label="New post"]')
            await create_button.click()
            await self.browser_manager.human_delay(2000, 3000)

            # Upload media
            file_input = await page.wait_for_selector('input[type="file"]')
            await file_input.set_input_files(media[0])
            await self.browser_manager.human_delay(3000, 5000)

            # Next button
            next_button = await page.wait_for_selector('button:has-text("Next")')
            await next_button.click()
            await self.browser_manager.human_delay(2000, 3000)

            # Next again (filters)
            next_button = await page.wait_for_selector('button:has-text("Next")')
            await next_button.click()
            await self.browser_manager.human_delay(2000, 3000)

            # Add caption
            caption_area = await page.wait_for_selector('textarea[aria-label*="caption"]')
            await caption_area.click()
            await page.keyboard.type(content)
            await self.browser_manager.human_delay(2000, 3000)

            # Share
            share_button = await page.wait_for_selector('button:has-text("Share")')
            await share_button.click()

            await self.browser_manager.human_delay(5000, 7000)

            self.logger.info("✅ Posted to Instagram successfully")
            return PostResult(
                success=True, platform="instagram", metadata={"caption_length": len(content)}
            )

        except Exception as e:
            self.logger.error(f"❌ Instagram posting failed: {e}")
            return PostResult(success=False, platform="instagram", error=str(e))

    async def send_dm(self, user_id: str, message: str, **kwargs) -> PostResult:
        """Send Instagram DM."""
        if not self._authenticated:
            return PostResult(success=False, platform="instagram", error="Not authenticated")

        try:
            page = self.browser_manager.page

            # Go to user profile
            await page.goto(f"{self.base_url}/{user_id}/")
            await self.browser_manager.wait_for_navigation()

            # Click message button
            message_button = await page.wait_for_selector('button:has-text("Message")')
            await message_button.click()
            await self.browser_manager.human_delay(2000, 3000)

            # Type message
            message_input = await page.wait_for_selector('textarea[placeholder*="Message"]')
            await message_input.click()
            await page.keyboard.type(message)
            await self.browser_manager.human_delay(1000, 2000)

            # Send
            send_button = await page.wait_for_selector('button:has-text("Send")')
            await send_button.click()

            await self.browser_manager.human_delay(2000, 3000)

            self.logger.info(f"✅ DM sent to {user_id}")
            return PostResult(success=True, platform="instagram", metadata={"user_id": user_id})

        except Exception as e:
            self.logger.error(f"❌ Instagram DM failed: {e}")
            return PostResult(success=False, platform="instagram", error=str(e))

    def get_capabilities(self) -> List[PlatformCapability]:
        """Get Instagram capabilities."""
        return [
            PlatformCapability.POST,
            PlatformCapability.DM,
            PlatformCapability.COMMENT,
            PlatformCapability.MEDIA,
        ]

    async def cleanup(self):
        """Cleanup resources."""
        if self.browser_manager:
            await self.browser_manager.close()
