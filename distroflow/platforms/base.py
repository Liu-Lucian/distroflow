"""
Base Platform Interface

All platform implementations must inherit from BasePlatform.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class PlatformCapability(Enum):
    """Platform capabilities."""

    POST = "post"  # Can post content
    COMMENT = "comment"  # Can comment on posts
    DM = "dm"  # Can send direct messages
    SEARCH = "search"  # Can search for content
    SCHEDULE = "schedule"  # Supports native scheduling
    MEDIA = "media"  # Supports media upload


@dataclass
class AuthConfig:
    """Authentication configuration."""

    auth_type: str  # "cookies", "api_key", "oauth"
    credentials: Dict[str, Any]
    expires_at: Optional[str] = None


@dataclass
class PostResult:
    """Result of a posting operation."""

    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class BasePlatform(ABC):
    """
    Abstract base class for all platform integrations.

    Each platform must implement:
    - setup_auth(): Authentication setup
    - post(): Post content
    - get_capabilities(): List supported features
    """

    def __init__(self, name: str):
        """
        Initialize platform.

        Args:
            name: Platform name (e.g., "twitter", "reddit")
        """
        self.name = name
        self._authenticated = False
        self.logger = logging.getLogger(f"distroflow.platforms.{name}")

    @abstractmethod
    async def setup_auth(self, auth_config: AuthConfig) -> bool:
        """
        Setup authentication for the platform.

        Args:
            auth_config: Authentication configuration

        Returns:
            True if authentication successful
        """
        pass

    @abstractmethod
    async def post(
        self,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        media: Optional[List[str]] = None,
        **kwargs,
    ) -> PostResult:
        """
        Post content to the platform.

        Args:
            content: Main content text
            title: Post title (if platform supports it)
            url: URL to include
            media: List of media file paths
            **kwargs: Platform-specific parameters

        Returns:
            PostResult with success status and details
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[PlatformCapability]:
        """
        Get list of capabilities this platform supports.

        Returns:
            List of PlatformCapability enums
        """
        pass

    async def comment(self, post_id: str, content: str, **kwargs) -> PostResult:
        """
        Comment on a post (if platform supports it).

        Args:
            post_id: ID of post to comment on
            content: Comment text
            **kwargs: Platform-specific parameters

        Returns:
            PostResult with success status
        """
        raise NotImplementedError(f"{self.name} does not support commenting")

    async def send_dm(self, user_id: str, message: str, **kwargs) -> PostResult:
        """
        Send direct message (if platform supports it).

        Args:
            user_id: User ID to message
            message: Message text
            **kwargs: Platform-specific parameters

        Returns:
            PostResult with success status
        """
        raise NotImplementedError(f"{self.name} does not support DMs")

    async def search(self, query: str, limit: int = 10, **kwargs) -> List[Dict]:
        """
        Search for content (if platform supports it).

        Args:
            query: Search query
            limit: Maximum number of results
            **kwargs: Platform-specific parameters

        Returns:
            List of search results
        """
        raise NotImplementedError(f"{self.name} does not support search")

    def is_authenticated(self) -> bool:
        """Check if platform is authenticated."""
        return self._authenticated

    async def test_connection(self) -> bool:
        """
        Test if authentication is working.

        Returns:
            True if connection successful
        """
        try:
            # Attempt a simple operation to verify auth
            # Each platform should override this with a real test
            return self._authenticated
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def __repr__(self) -> str:
        """String representation."""
        auth_status = "authenticated" if self._authenticated else "not authenticated"
        return f"<{self.__class__.__name__} ({auth_status})>"
