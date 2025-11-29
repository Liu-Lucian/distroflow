"""
Platform modules for DistroFlow

Each platform implements the BasePlatform interface for consistent usage.
"""

from distroflow.platforms.base import BasePlatform, PlatformCapability
from distroflow.platforms.twitter import TwitterPlatform
from distroflow.platforms.reddit import RedditPlatform
from distroflow.platforms.hackernews import HackerNewsPlatform
from distroflow.platforms.instagram import InstagramPlatform

__all__ = [
    "BasePlatform",
    "PlatformCapability",
    "TwitterPlatform",
    "RedditPlatform",
    "HackerNewsPlatform",
    "InstagramPlatform",
]
