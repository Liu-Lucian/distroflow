"""
DistroFlow: Open-source Cross-Platform Distribution Infrastructure

Automate content distribution and audience engagement across 10+ platforms
using AI-powered browser automation.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from distroflow.core.browser_manager import BrowserManager
from distroflow.core.scheduler import Scheduler
from distroflow.core.ai_healer import AIHealer
from distroflow.core.content_transformer import ContentTransformer

__all__ = [
    "BrowserManager",
    "Scheduler",
    "AIHealer",
    "ContentTransformer",
]
