"""
Smart User Finder - AI驱动的潜在客户识别系统
分析帖子评论，使用GPT识别有需求的用户
"""

import os
import json
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from playwright.sync_api import Page, sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartUserFinder:
    """AI驱动的用户识别器 - 从评论中找到潜在客户"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Smart User Finder

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        # Strip whitespace and newlines from API key
        self.api_key = self.api_key.strip()

        self.client = OpenAI(api_key=self.api_key)
        logger.info("✅ Smart User Finder initialized")

    def analyze_comments_for_intent(
        self,
        comments: List[Dict],
        product_description: str
    ) -> List[Dict]:
        """
        使用AI分析评论，识别有购买意图的用户

        Args:
            comments: 评论列表 [{"username": "...", "text": "...", "url": "..."}, ...]
            product_description: 产品描述

        Returns:
            有意图的用户列表，带有意图分数和原因
        """
        if not comments:
            return []

        logger.info(f"🧠 Analyzing {len(comments)} comments with AI...")

        # 构建prompt
        comments_text = "\n".join([
            f"- @{c['username']}: {c['text']}"
            for c in comments[:50]  # 限制在50条以内避免token过多
        ])

        prompt = f"""You are a sales intelligence AI. Analyze these social media comments and identify users who might be interested in our product.

**Our Product**: {product_description}

**Comments to Analyze**:
{comments_text}

**Task**: For each comment, determine if the user shows:
1. Pain points our product solves
2. Interest in the topic
3. Buying intent or need for solution
4. Decision-making authority (e.g., founder, CEO, hiring manager)

**Output Format** (JSON array):
[
    {{
        "username": "username without @",
        "intent_score": 0.0-1.0,
        "reasons": ["reason 1", "reason 2"],
        "pain_points": ["pain point 1", "pain point 2"],
        "priority": "high" | "medium" | "low"
    }},
    ...
]

Only include users with intent_score >= 0.4. Return valid JSON only.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 更便宜的模型用于批量分析
                messages=[
                    {"role": "system", "content": "You are a sales intelligence analyst. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )

            response_text = response.choices[0].message.content

            # 提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            qualified_users = json.loads(response_text)

            logger.info(f"✅ AI identified {len(qualified_users)} qualified users")

            # 合并原始评论信息
            username_to_comment = {c['username'].lstrip('@'): c for c in comments}

            for user in qualified_users:
                username = user['username'].lstrip('@')
                if username in username_to_comment:
                    user.update(username_to_comment[username])

            return qualified_users

        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    def scrape_post_comments(
        self,
        page: Page,
        post_url: str,
        platform: str = "reddit",
        max_comments: int = 50
    ) -> List[Dict]:
        """
        从帖子中抓取评论

        Args:
            page: Playwright page对象
            post_url: 帖子URL
            platform: 平台名称 (reddit, twitter, instagram)
            max_comments: 最多抓取评论数

        Returns:
            评论列表
        """
        logger.info(f"📝 Scraping comments from {post_url}...")

        page.goto(post_url, timeout=60000)

        import time
        time.sleep(3)

        comments = []

        if platform == "reddit":
            # Reddit评论选择器
            comment_selectors = [
                'div[data-testid="comment"]',
                'div.Comment',
                'div[id^="t1_"]'
            ]

            for selector in comment_selectors:
                try:
                    comment_elements = page.query_selector_all(selector)
                    if comment_elements:
                        logger.info(f"   Found {len(comment_elements)} comments with: {selector}")

                        for elem in comment_elements[:max_comments]:
                            try:
                                # 用户名
                                username_elem = elem.query_selector('a[href*="/user/"]')
                                username = username_elem.inner_text() if username_elem else "unknown"

                                # 评论文本
                                text_elem = elem.query_selector('div[data-testid="comment"], p, div')
                                text = text_elem.inner_text() if text_elem else ""

                                if username and text and len(text) > 10:
                                    comments.append({
                                        "username": username.lstrip('u/').lstrip('@'),
                                        "text": text[:500],  # 限制长度
                                        "platform": platform,
                                        "source_url": post_url
                                    })

                            except Exception as e:
                                logger.debug(f"Error parsing comment: {e}")
                                continue

                        if comments:
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

        elif platform == "twitter":
            # Twitter评论选择器
            tweet_selectors = [
                'article[data-testid="tweet"]',
                'div[data-testid="cellInnerDiv"]'
            ]

            # 滚动加载评论
            for i in range(3):
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(1)

            for selector in tweet_selectors:
                try:
                    tweet_elements = page.query_selector_all(selector)
                    if tweet_elements:
                        logger.info(f"   Found {len(tweet_elements)} tweets/replies")

                        for elem in tweet_elements[:max_comments]:
                            try:
                                # 用户名
                                username_elem = elem.query_selector('a[href^="/"][href*="/status/"] span')
                                username = username_elem.inner_text() if username_elem else "unknown"

                                # 推文文本
                                text_elem = elem.query_selector('div[data-testid="tweetText"], div[lang]')
                                text = text_elem.inner_text() if text_elem else ""

                                if username and text and len(text) > 10:
                                    comments.append({
                                        "username": username.lstrip('@'),
                                        "text": text[:500],
                                        "platform": platform,
                                        "source_url": post_url
                                    })

                            except Exception as e:
                                logger.debug(f"Error parsing tweet: {e}")
                                continue

                        if comments:
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

        elif platform == "instagram":
            # Instagram评论选择器
            # 先加载更多评论
            try:
                load_more = page.query_selector('button:has-text("Load more comments")')
                if load_more:
                    load_more.click()
                    time.sleep(2)
            except:
                pass

            comment_selectors = [
                'ul li div span',
                'div[role="button"] span',
            ]

            # Instagram评论结构比较复杂，需要特殊处理
            # 简化版：抓取可见的评论文本
            try:
                all_spans = page.query_selector_all('span')
                for span in all_spans[:max_comments]:
                    text = span.inner_text()
                    # 简单启发式：评论通常长度在10-500字符
                    if 10 < len(text) < 500 and not text.startswith('http'):
                        comments.append({
                            "username": "instagram_user",  # Instagram评论用户名较难提取
                            "text": text,
                            "platform": platform,
                            "source_url": post_url
                        })
            except Exception as e:
                logger.error(f"Instagram comment scraping failed: {e}")

        # 去重
        seen = set()
        unique_comments = []
        for c in comments:
            key = f"{c['username']}:{c['text'][:50]}"
            if key not in seen:
                seen.add(key)
                unique_comments.append(c)

        logger.info(f"✅ Scraped {len(unique_comments)} unique comments")

        return unique_comments

    def find_qualified_users_from_post(
        self,
        page: Page,
        post_url: str,
        product_description: str,
        platform: str = "reddit",
        max_comments: int = 50
    ) -> List[Dict]:
        """
        完整流程：抓取评论 → AI分析 → 返回合格用户

        Args:
            page: Playwright page对象
            post_url: 帖子URL
            product_description: 产品描述
            platform: 平台名称
            max_comments: 最多抓取评论数

        Returns:
            合格用户列表
        """
        # 步骤1: 抓取评论
        comments = self.scrape_post_comments(
            page=page,
            post_url=post_url,
            platform=platform,
            max_comments=max_comments
        )

        if not comments:
            logger.warning("⚠️ No comments found")
            return []

        # 步骤2: AI分析
        qualified_users = self.analyze_comments_for_intent(
            comments=comments,
            product_description=product_description
        )

        return qualified_users


# 便捷函数
def find_users_in_post(
    post_url: str,
    product_description: str,
    platform: str = "reddit"
) -> List[Dict]:
    """
    快速从单个帖子中找到潜在客户

    Args:
        post_url: 帖子URL
        product_description: 产品描述
        platform: 平台名称

    Returns:
        合格用户列表
    """
    finder = SmartUserFinder()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        users = finder.find_qualified_users_from_post(
            page=page,
            post_url=post_url,
            product_description=product_description,
            platform=platform
        )

        browser.close()

    return users


if __name__ == "__main__":
    # 测试代码
    print("Smart User Finder - AI-powered lead generation")
    print("\nExample usage:")
    print("""
from smart_user_finder import SmartUserFinder

finder = SmartUserFinder()

# 找到潜在客户
users = finder.find_qualified_users_from_post(
    page=page,
    post_url="https://reddit.com/r/jobs/comments/...",
    product_description="HireMeAI - AI-powered interview preparation platform",
    platform="reddit"
)

# 结果
for user in users:
    print(f"@{user['username']} - Score: {user['intent_score']}")
    print(f"  Reasons: {user['reasons']}")
    print(f"  Priority: {user['priority']}")
""")
