"""
Browser Manager - Unified Playwright browser lifecycle management
"""

import asyncio
import random
from typing import Optional, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from pathlib import Path


class BrowserManager:
    """
    Manages Playwright browser instances with persistent authentication.

    Features:
    - Context manager support for automatic cleanup
    - Persistent authentication via browser contexts
    - Human-like behavior simulation
    - Automatic retry on failures
    """

    def __init__(
        self,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize browser manager.

        Args:
            headless: Run browser in headless mode
            user_data_dir: Directory for persistent browser data
            viewport: Custom viewport size (default: 1920x1080)
        """
        self.headless = headless
        self.user_data_dir = user_data_dir or str(Path.home() / ".distroflow" / "browser_data")
        self.viewport = viewport or {"width": 1920, "height": 1080}

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the browser instance."""
        self._playwright = await async_playwright().start()

        # Launch browser with human-like settings
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        # Create persistent context for authentication
        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)

        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self._context = await self._browser.new_context(
            viewport=self.viewport,
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )

        # Anti-detection: Remove webdriver flag
        await self._context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
        )

        # Create initial page
        self._page = await self._context.new_page()

    async def close(self):
        """Close browser and cleanup resources."""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def new_page(self) -> Page:
        """Create a new page in the current context."""
        if not self._context:
            await self.start()
        return await self._context.new_page()

    @property
    def page(self) -> Page:
        """Get the current page."""
        if not self._page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Get the browser context."""
        if not self._context:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._context

    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """
        Simulate human-like delay.

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)

    async def human_type(self, selector: str, text: str, delay_ms: int = 100):
        """
        Type text with human-like delays between keystrokes.

        Args:
            selector: Element selector
            text: Text to type
            delay_ms: Average delay between keystrokes
        """
        element = await self.page.wait_for_selector(selector)
        for char in text:
            await element.type(char, delay=delay_ms + random.randint(-30, 30))

    async def screenshot(self, path: str, full_page: bool = False):
        """
        Take a screenshot.

        Args:
            path: Path to save screenshot
            full_page: Capture full scrollable page
        """
        await self.page.screenshot(path=path, full_page=full_page)

    async def save_cookies(self, path: str):
        """Save current cookies to file."""
        import json

        cookies = await self._context.cookies()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(cookies, f, indent=2)

    async def load_cookies(self, path: str):
        """Load cookies from file."""
        import json

        if not Path(path).exists():
            return
        with open(path, "r") as f:
            cookies = json.load(f)
        await self._context.add_cookies(cookies)

    async def wait_for_navigation(self, timeout: int = 30000):
        """Wait for navigation to complete."""
        await self.page.wait_for_load_state("networkidle", timeout=timeout)

    async def retry_on_failure(self, func, max_retries: int = 3, *args, **kwargs):
        """
        Retry a function on failure.

        Args:
            func: Async function to retry
            max_retries: Maximum number of retries
            *args, **kwargs: Arguments to pass to func
        """
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff
