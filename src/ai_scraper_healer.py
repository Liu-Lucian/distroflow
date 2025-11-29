"""
AI Scraper Healer - 自动诊断和修复爬虫问题
使用GPT-4 Vision分析页面，自动生成修复方案
"""

import os
import json
import base64
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from playwright.sync_api import Page
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIScraperHealer:
    """AI驱动的爬虫自愈系统"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化AI Healer

        Args:
            api_key: OpenAI API key，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        logger.info("✅ AI Scraper Healer initialized")

    def analyze_page_with_vision(
        self,
        page: Page,
        task_description: str,
        current_url: str,
        error_message: Optional[str] = None
    ) -> Dict:
        """
        使用GPT-4 Vision分析页面截图，提供解决方案

        Args:
            page: Playwright page对象
            task_description: 当前尝试完成的任务（如"找到Message按钮"）
            current_url: 当前页面URL
            error_message: 错误信息（如果有）

        Returns:
            包含分析结果和建议的字典
        """
        logger.info(f"🔍 Analyzing page with AI Vision...")
        logger.info(f"   Task: {task_description}")
        logger.info(f"   URL: {current_url}")

        # 截图
        screenshot_bytes = page.screenshot(full_page=False)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        # 构建prompt
        prompt = f"""You are an expert web scraping assistant. Analyze this Instagram page screenshot and help solve the problem.

**Current Task**: {task_description}
**Current URL**: {current_url}
**Error**: {error_message or 'No specific error, but task failed'}

Please analyze the screenshot and provide:

1. **What you see**: Describe the current page state and visible elements
2. **The problem**: Why the task might be failing
3. **Suggested CSS selectors**: Provide 3-5 CSS selectors that might work for the target element, ordered by priority
4. **Alternative approach**: If direct selection won't work, suggest an alternative strategy (e.g., navigate to different URL, click different element first)
5. **Human-like actions needed**: Any specific delays, scrolling, or interaction patterns needed

Format your response as JSON:
{{
    "page_state": "description of what's visible",
    "problem_analysis": "why the task is failing",
    "suggested_selectors": [
        {{"selector": "css selector", "priority": 1, "reason": "why this might work"}},
        ...
    ],
    "alternative_approach": "alternative strategy if selectors won't work",
    "recommended_actions": ["action 1", "action 2", ...],
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
                                    "url": f"data:image/png;base64,{screenshot_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )

            # 解析响应
            response_text = response.choices[0].message.content

            # 尝试提取JSON（可能被包裹在```json```中）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)

            logger.info(f"✅ AI Analysis complete:")
            logger.info(f"   Confidence: {analysis.get('confidence', 'N/A')}")
            logger.info(f"   Problem: {analysis.get('problem_analysis', 'N/A')[:100]}...")

            return analysis

        except Exception as e:
            logger.error(f"❌ AI Vision analysis failed: {e}")
            return {
                "page_state": "Analysis failed",
                "problem_analysis": str(e),
                "suggested_selectors": [],
                "alternative_approach": "Manual debugging needed",
                "recommended_actions": [],
                "confidence": 0.0
            }

    def try_selectors_with_ai_guidance(
        self,
        page: Page,
        ai_analysis: Dict,
        action: str = "click"
    ) -> Tuple[bool, Optional[str]]:
        """
        根据AI建议的选择器尝试执行操作

        Args:
            page: Playwright page对象
            ai_analysis: AI分析结果
            action: 要执行的操作（click, fill, etc.）

        Returns:
            (成功与否, 成功的选择器)
        """
        suggested_selectors = ai_analysis.get('suggested_selectors', [])

        if not suggested_selectors:
            logger.warning("⚠️  No selectors suggested by AI")
            return False, None

        logger.info(f"🧪 Trying {len(suggested_selectors)} AI-suggested selectors...")

        for i, selector_info in enumerate(suggested_selectors, 1):
            selector = selector_info.get('selector')
            reason = selector_info.get('reason', 'No reason provided')

            logger.info(f"   [{i}/{len(suggested_selectors)}] Trying: {selector}")
            logger.info(f"      Reason: {reason}")

            try:
                element = page.wait_for_selector(selector, timeout=3000)
                if element and element.is_visible():
                    logger.info(f"   ✅ Found visible element!")

                    if action == "click":
                        # 使用JavaScript点击避免overlay问题
                        page.evaluate('(element) => element.click()', element)
                        logger.info(f"   ✅ Clicked successfully")
                        return True, selector

                    elif action == "fill":
                        return True, selector  # 返回element供调用者使用

                    return True, selector

            except Exception as e:
                logger.debug(f"      ❌ Failed: {e}")
                continue

        logger.warning("❌ All AI-suggested selectors failed")
        return False, None

    def execute_alternative_approach(
        self,
        page: Page,
        ai_analysis: Dict
    ) -> bool:
        """
        执行AI建议的替代方案

        Args:
            page: Playwright page对象
            ai_analysis: AI分析结果

        Returns:
            是否成功
        """
        alternative = ai_analysis.get('alternative_approach', '')

        if not alternative or alternative == "Manual debugging needed":
            return False

        logger.info(f"🔄 Executing alternative approach:")
        logger.info(f"   {alternative}")

        # 这里可以根据alternative的内容执行不同的策略
        # 比如：导航到新URL、点击其他元素等

        # 示例：如果建议包含URL
        if "navigate to" in alternative.lower() or "go to" in alternative.lower():
            # 提取URL（简单实现）
            import re
            urls = re.findall(r'https?://[^\s]+', alternative)
            if urls:
                url = urls[0]
                logger.info(f"   Navigating to: {url}")
                page.goto(url, timeout=30000)
                return True

        return False

    def apply_human_like_actions(
        self,
        page: Page,
        ai_analysis: Dict
    ):
        """
        应用AI建议的类人操作

        Args:
            page: Playwright page对象
            ai_analysis: AI分析结果
        """
        actions = ai_analysis.get('recommended_actions', [])

        if not actions:
            return

        logger.info(f"🤖 Applying {len(actions)} human-like actions...")

        import time
        import random

        for action in actions:
            action_lower = action.lower()

            if "scroll" in action_lower:
                logger.info(f"   📜 {action}")
                # 提取滚动距离（如果有）
                if "down" in action_lower:
                    page.evaluate("window.scrollBy(0, 300 + Math.random() * 200)")
                elif "up" in action_lower:
                    page.evaluate("window.scrollBy(0, -(300 + Math.random() * 200))")
                time.sleep(random.uniform(0.5, 1.5))

            elif "wait" in action_lower or "delay" in action_lower:
                logger.info(f"   ⏳ {action}")
                # 提取等待时间（简单实现）
                import re
                numbers = re.findall(r'\d+', action)
                if numbers:
                    delay = int(numbers[0])
                else:
                    delay = random.randint(2, 5)
                time.sleep(delay)

            elif "move mouse" in action_lower or "hover" in action_lower:
                logger.info(f"   🖱️  {action}")
                # 随机移动鼠标（模拟真人）
                page.mouse.move(
                    random.randint(100, 1000),
                    random.randint(100, 700)
                )
                time.sleep(random.uniform(0.3, 0.8))


# 便捷函数
def heal_scraper_with_ai(
    page: Page,
    task_description: str,
    error_message: Optional[str] = None
) -> Dict:
    """
    快速使用AI诊断和修复爬虫问题

    Args:
        page: Playwright page对象
        task_description: 任务描述
        error_message: 错误信息

    Returns:
        AI分析结果
    """
    healer = AIScraperHealer()
    analysis = healer.analyze_page_with_vision(
        page=page,
        task_description=task_description,
        current_url=page.url,
        error_message=error_message
    )

    # 自动应用建议的操作
    healer.apply_human_like_actions(page, analysis)

    return analysis


if __name__ == "__main__":
    # 测试代码
    print("AI Scraper Healer - Ready to diagnose and fix scraping issues!")
    print("Usage example:")
    print("""
from ai_scraper_healer import AIScraperHealer

healer = AIScraperHealer()

# 当遇到问题时
analysis = healer.analyze_page_with_vision(
    page=page,
    task_description="Find and click the Message button on Instagram",
    current_url=page.url,
    error_message="Could not find message button with selector 'button:has-text(Message)'"
)

# 尝试AI建议的选择器
success, working_selector = healer.try_selectors_with_ai_guidance(
    page=page,
    ai_analysis=analysis,
    action="click"
)

if not success:
    # 尝试替代方案
    healer.execute_alternative_approach(page, analysis)
""")
