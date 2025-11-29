"""
Content Transformer - Platform-specific content formatting

Automatically adapts content for each platform's:
- Character limits
- Hashtag conventions
- Mention formats
- Link handling
- Media requirements
"""

import re
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms."""

    TWITTER = "twitter"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    PRODUCTHUNT = "producthunt"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    GITHUB = "github"
    QUORA = "quora"


class ContentTransformer:
    """
    Transform content for platform-specific requirements.

    Features:
    - Character limit enforcement
    - Hashtag formatting
    - Link shortening/handling
    - Emoji support
    - Language detection
    """

    # Platform character limits
    CHAR_LIMITS = {
        Platform.TWITTER: 280,
        Platform.REDDIT: 40000,  # Title: 300, body: 40000
        Platform.HACKERNEWS: None,  # No limit
        Platform.PRODUCTHUNT: 260,  # Tagline
        Platform.LINKEDIN: 3000,
        Platform.INSTAGRAM: 2200,
        Platform.TIKTOK: 2200,
        Platform.FACEBOOK: 63206,
        Platform.MEDIUM: None,
        Platform.SUBSTACK: None,
        Platform.GITHUB: None,
        Platform.QUORA: None,
    }

    # Platform hashtag conventions
    HASHTAG_STYLES = {
        Platform.TWITTER: "inline",  # #BuildInPublic works mid-sentence
        Platform.INSTAGRAM: "end",  # Hashtags at end of post
        Platform.TIKTOK: "end",
        Platform.LINKEDIN: "inline",
        Platform.FACEBOOK: "inline",
        Platform.REDDIT: "none",  # No hashtags
        Platform.HACKERNEWS: "none",
        Platform.PRODUCTHUNT: "tags",  # Separate tag field
        Platform.MEDIUM: "none",
        Platform.SUBSTACK: "none",
        Platform.GITHUB: "none",
        Platform.QUORA: "none",
    }

    def __init__(self):
        """Initialize content transformer."""
        logger.info("✨ Content Transformer initialized")

    def transform(
        self,
        content: str,
        platform: Platform,
        title: Optional[str] = None,
        url: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Transform content for a specific platform.

        Args:
            content: Raw content
            platform: Target platform
            title: Post title (for platforms that need it)
            url: URL to include
            hashtags: List of hashtags (without #)

        Returns:
            Dict with platform-specific fields:
            - content: Transformed content
            - title: Transformed title (if applicable)
            - hashtags: Platform-formatted hashtags
            - truncated: Whether content was truncated
        """
        result = {
            "content": content,
            "title": title or "",
            "hashtags": hashtags or [],
            "truncated": False,
        }

        # Apply platform-specific transformations
        if platform == Platform.TWITTER:
            result = self._transform_twitter(content, url, hashtags)
        elif platform == Platform.REDDIT:
            result = self._transform_reddit(content, title, url)
        elif platform == Platform.HACKERNEWS:
            result = self._transform_hackernews(title, url, content)
        elif platform == Platform.INSTAGRAM:
            result = self._transform_instagram(content, hashtags)
        elif platform == Platform.LINKEDIN:
            result = self._transform_linkedin(content, hashtags)
        elif platform in [Platform.MEDIUM, Platform.SUBSTACK]:
            result = self._transform_longform(content, title)
        else:
            # Generic transformation
            result = self._transform_generic(content, platform, hashtags)

        logger.debug(f"📝 Transformed content for {platform.value}")
        return result

    def _transform_twitter(
        self, content: str, url: Optional[str], hashtags: Optional[List[str]]
    ) -> Dict:
        """Transform for Twitter."""
        # Add hashtags inline
        if hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in hashtags[:3])  # Max 3 hashtags
            content = f"{content}\n\n{hashtag_str}"

        # Add URL
        if url:
            content = f"{content}\n\n{url}"

        # Enforce character limit
        limit = self.CHAR_LIMITS[Platform.TWITTER]
        if len(content) > limit:
            # Truncate with ellipsis
            content = content[: limit - 3] + "..."
            truncated = True
        else:
            truncated = False

        return {"content": content, "title": "", "hashtags": hashtags or [], "truncated": truncated}

    def _transform_reddit(self, content: str, title: Optional[str], url: Optional[str]) -> Dict:
        """Transform for Reddit."""
        # Reddit has title + body structure
        if not title:
            # Extract first line as title
            lines = content.split("\n")
            title = lines[0][:300]  # Reddit title limit
            content = "\n".join(lines[1:])

        # Add URL at the end if provided
        if url:
            content = f"{content}\n\n{url}"

        return {
            "content": content,
            "title": title,
            "hashtags": [],  # Reddit doesn't use hashtags
            "truncated": False,
        }

    def _transform_hackernews(
        self, title: Optional[str], url: Optional[str], content: Optional[str]
    ) -> Dict:
        """Transform for HackerNews."""
        # HN needs "Show HN:" or "Ask HN:" prefix
        if title and not title.startswith(("Show HN:", "Ask HN:")):
            if url:
                title = f"Show HN: {title}"
            else:
                title = f"Ask HN: {title}"

        return {
            "content": content or "",
            "title": title or "",
            "url": url or "",
            "hashtags": [],
            "truncated": False,
        }

    def _transform_instagram(self, content: str, hashtags: Optional[List[str]]) -> Dict:
        """Transform for Instagram."""
        # Add hashtags at the end
        if hashtags:
            # Instagram allows up to 30 hashtags
            hashtag_str = "\n\n" + " ".join(f"#{tag}" for tag in hashtags[:30])
            content = content + hashtag_str

        # Enforce character limit
        limit = self.CHAR_LIMITS[Platform.INSTAGRAM]
        if len(content) > limit:
            content = content[: limit - 3] + "..."
            truncated = True
        else:
            truncated = False

        return {"content": content, "title": "", "hashtags": hashtags or [], "truncated": truncated}

    def _transform_linkedin(self, content: str, hashtags: Optional[List[str]]) -> Dict:
        """Transform for LinkedIn."""
        # Add hashtags inline (LinkedIn style)
        if hashtags:
            hashtag_str = "\n\n" + " ".join(f"#{tag}" for tag in hashtags[:5])
            content = content + hashtag_str

        # Enforce character limit
        limit = self.CHAR_LIMITS[Platform.LINKEDIN]
        if len(content) > limit:
            content = content[: limit - 3] + "..."
            truncated = True
        else:
            truncated = False

        return {"content": content, "title": "", "hashtags": hashtags or [], "truncated": truncated}

    def _transform_longform(self, content: str, title: Optional[str]) -> Dict:
        """Transform for Medium/Substack."""
        # These platforms support full articles
        return {
            "content": content,
            "title": title or "Untitled",
            "hashtags": [],
            "truncated": False,
        }

    def _transform_generic(
        self, content: str, platform: Platform, hashtags: Optional[List[str]]
    ) -> Dict:
        """Generic transformation for other platforms."""
        limit = self.CHAR_LIMITS.get(platform)
        truncated = False

        if limit and len(content) > limit:
            content = content[: limit - 3] + "..."
            truncated = True

        return {"content": content, "title": "", "hashtags": hashtags or [], "truncated": truncated}

    def extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content."""
        # Find all hashtags (#word)
        hashtags = re.findall(r"#(\w+)", content)
        return hashtags

    def remove_hashtags(self, content: str) -> str:
        """Remove hashtags from content."""
        return re.sub(r"#\w+", "", content).strip()

    def add_call_to_action(self, content: str, platform: Platform, cta_type: str = "github") -> str:
        """
        Add platform-appropriate call-to-action.

        Args:
            content: Original content
            platform: Target platform
            cta_type: Type of CTA ("github", "website", "email", etc.)

        Returns:
            Content with CTA appended
        """
        ctas = {
            "github": "⭐ Star on GitHub: [link]",
            "website": "🔗 Learn more: [link]",
            "email": "📧 Subscribe: [link]",
            "demo": "🎬 Watch demo: [link]",
        }

        cta = ctas.get(cta_type, "")

        # Add CTA with platform-appropriate formatting
        if platform in [Platform.TWITTER, Platform.LINKEDIN]:
            return f"{content}\n\n{cta}"
        elif platform == Platform.REDDIT:
            return f"{content}\n\n---\n\n{cta}"
        else:
            return f"{content}\n\n{cta}"

    def optimize_for_seo(self, content: str, keywords: List[str]) -> str:
        """
        Optimize content for search engines.

        Args:
            content: Original content
            keywords: Keywords to emphasize

        Returns:
            SEO-optimized content
        """
        # This is a simple implementation
        # In production, you'd want more sophisticated SEO optimization
        return content
