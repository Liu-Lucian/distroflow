"""
AI Healer - Automatic debugging and CAPTCHA solving using GPT-4 Vision

This module provides:
1. Auto-diagnosis of scraping failures
2. CAPTCHA solving (slider puzzles, etc.)
3. Selector recommendations when DOM changes
4. Alternative strategy suggestions
"""

import os
import json
import base64
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class AIHealer:
    """
    AI-powered auto-healing for browser automation.

    Uses GPT-4 Vision to:
    - Analyze page screenshots when tasks fail
    - Suggest working CSS selectors
    - Solve CAPTCHAs automatically
    - Provide alternative strategies
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Healer.

        Args:
            api_key: OpenAI API key (default: from OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        logger.info("✅ AI Healer initialized")

    async def analyze_failure(
        self, page: Page, task_description: str, error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a scraping failure using GPT-4 Vision.

        Args:
            page: Playwright page object
            task_description: What you were trying to do (e.g., "Click Message button")
            error_message: Error message if any

        Returns:
            Analysis dict with:
            - page_state: Description of visible elements
            - problem_analysis: Why task failed
            - suggested_selectors: List of CSS selectors to try
            - alternative_approach: Alternative strategy
            - recommended_actions: Step-by-step actions
            - confidence: AI confidence (0.0-1.0)
        """
        logger.info(f"🔍 AI analyzing failure: {task_description}")

        # Take screenshot
        screenshot_bytes = await page.screenshot(full_page=False)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        # Build prompt
        error_msg = error_message or "Task failed without specific error"
        prompt = f"""You are an expert web scraping assistant. \
Analyze this page screenshot and solve the problem.

**Task**: {task_description}
**URL**: {page.url}
**Error**: {error_msg}

Analyze the screenshot and provide:

1. **What you see**: Current page state and visible elements
2. **Problem**: Why the task failed
3. **Suggested selectors**: 3-5 CSS selectors for the target element (ordered by priority)
4. **Alternative approach**: If selectors won't work, suggest alternative strategy
5. **Actions needed**: Human-like actions (delays, scrolling, etc.)

Response as JSON:
{{
    "page_state": "description",
    "problem_analysis": "why it failed",
    "suggested_selectors": [
        {{"selector": "css", "priority": 1, "reason": "why this works"}},
        ...
    ],
    "alternative_approach": "alternative strategy",
    "recommended_actions": ["action 1", "action 2"],
    "confidence": 0.0-1.0
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4 with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse JSON response
            content = response.choices[0].message.content
            analysis = json.loads(content.strip().strip("```json").strip("```"))

            logger.info(f"✅ AI analysis complete (confidence: {analysis.get('confidence', 0)})")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response: {e}")
            logger.error(f"Raw response: {content}")
            return {
                "page_state": "unknown",
                "problem_analysis": "AI response parsing failed",
                "suggested_selectors": [],
                "alternative_approach": "Manual intervention required",
                "recommended_actions": [],
                "confidence": 0.0,
            }
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return {
                "page_state": "error",
                "problem_analysis": str(e),
                "suggested_selectors": [],
                "alternative_approach": "Retry or manual fix",
                "recommended_actions": [],
                "confidence": 0.0,
            }

    async def solve_captcha(
        self, page: Page, captcha_type: str = "slider"
    ) -> Optional[Dict[str, Any]]:
        """
        Solve CAPTCHA using GPT-4 Vision.

        Args:
            page: Playwright page with CAPTCHA
            captcha_type: Type of CAPTCHA ("slider", "select_images", etc.)

        Returns:
            Solution dict with:
            - captcha_type: Detected type
            - solution: Solution data (e.g., slider position, image indices)
            - instructions: How to apply the solution
            - confidence: AI confidence
        """
        logger.info(f"🤖 Solving {captcha_type} CAPTCHA...")

        screenshot_bytes = await page.screenshot(full_page=False)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        prompts = {
            "slider": """Analyze this slider CAPTCHA screenshot.

**Task**: Identify the correct slider position to solve the CAPTCHA.

Provide:
1. **Slider position**: X coordinate (0-100 scale, where 0=left, 100=right)
2. **Confidence**: How confident you are (0.0-1.0)
3. **Instructions**: Step-by-step actions to solve

Response as JSON:
{{
    "captcha_type": "slider",
    "solution": {{"slider_position": 0-100}},
    "instructions": ["step 1", "step 2"],
    "confidence": 0.0-1.0
}}
""",
            "select_images": """Analyze this image selection CAPTCHA.

**Task**: Identify which images contain [object].

Provide indices of images that match (0-indexed).

Response as JSON:
{{
    "captcha_type": "select_images",
    "solution": {{"image_indices": [0, 3, 5]}},
    "instructions": ["Click image 0", "Click image 3", "Click image 5"],
    "confidence": 0.0-1.0
}}
""",
        }

        prompt = prompts.get(captcha_type, prompts["slider"])

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
                temperature=0.1,  # Low temperature for deterministic answers
            )

            content = response.choices[0].message.content
            solution = json.loads(content.strip().strip("```json").strip("```"))

            logger.info(f"✅ CAPTCHA solved (confidence: {solution.get('confidence', 0)})")
            return solution

        except Exception as e:
            logger.error(f"❌ CAPTCHA solving failed: {e}")
            return None

    async def find_element_with_vision(self, page: Page, element_description: str) -> List[str]:
        """
        Find element selectors by describing what you want.

        Args:
            page: Playwright page
            element_description: Natural language description (e.g., "blue login button")

        Returns:
            List of suggested CSS selectors (ordered by priority)
        """
        logger.info(f"🔍 Finding element: {element_description}")

        screenshot_bytes = await page.screenshot(full_page=False)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        prompt = f"""Find the element matching this description: "{element_description}"

Analyze the screenshot and provide CSS selectors for this element.

Response as JSON:
{{
    "selectors": [
        {{"selector": "css", "priority": 1, "reason": "why"}},
        {{"selector": "css", "priority": 2, "reason": "why"}},
        ...
    ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            result = json.loads(content.strip().strip("```json").strip("```"))

            selectors = [item["selector"] for item in result["selectors"]]
            logger.info(f"✅ Found {len(selectors)} possible selectors")
            return selectors

        except Exception as e:
            logger.error(f"❌ Element finding failed: {e}")
            return []

    def estimate_cost(self, num_screenshots: int, detail: str = "high") -> float:
        """
        Estimate GPT-4 Vision API cost.

        Args:
            num_screenshots: Number of screenshots to analyze
            detail: Image detail level ("low" or "high")

        Returns:
            Estimated cost in USD
        """
        # GPT-4 Vision pricing (as of 2024)
        # High detail: ~$0.01 per image
        # Low detail: ~$0.003 per image
        cost_per_image = 0.01 if detail == "high" else 0.003
        return num_screenshots * cost_per_image
