"""Configuration management for MarketingMind AI"""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Central configuration class"""

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Twitter API
    TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")

    # Email Finder APIs
    CLEARBIT_API_KEY: str = os.getenv("CLEARBIT_API_KEY", "")
    HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY", "")

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "15"))
    MAX_FOLLOWERS_TO_SCRAPE: int = int(os.getenv("MAX_FOLLOWERS_TO_SCRAPE", "500"))

    # Directories
    EXPORTS_DIR: str = "exports"
    LOGS_DIR: str = "logs"

    @classmethod
    def validate(cls) -> bool:
        """Validate that required API keys are present"""
        required = [
            cls.ANTHROPIC_API_KEY or cls.OPENAI_API_KEY,  # At least one LLM API
            cls.TWITTER_ACCESS_TOKEN,
            cls.TWITTER_ACCESS_TOKEN_SECRET,
        ]
        return all(required)

    @classmethod
    def get_llm_provider(cls) -> str:
        """Determine which LLM provider to use"""
        if cls.ANTHROPIC_API_KEY:
            return "anthropic"
        elif cls.OPENAI_API_KEY:
            return "openai"
        return "none"


config = Config()
