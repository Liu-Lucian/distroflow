"""
Product Brain - 产品知识库
使用 AI 分析产品文档，提取关键信息、目标用户画像、关键词等
"""

import os
import re
import json
import logging
from typing import List, Dict, Optional
from anthropic import Anthropic
import openai
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductBrain:
    """AI-powered product knowledge extraction"""

    def __init__(self, api_provider: str = "anthropic"):
        """
        Initialize ProductBrain

        Args:
            api_provider: "anthropic" or "openai"
        """
        self.api_provider = api_provider

        if api_provider == "anthropic":
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in .env")
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            openai.api_key = api_key
            self.model = "gpt-4"

    def analyze_product(self, product_text: str) -> Dict:
        """
        Analyze product document and extract key information

        Args:
            product_text: Product description text

        Returns:
            Dictionary with extracted information
        """
        prompt = f"""分析以下产品描述，提取关键信息。请以JSON格式返回结果。

产品描述：
{product_text}

请提取以下信息（用JSON格式返回）：
1. keywords: 10-15个关键词（产品特点、技术栈、行业术语）
2. target_personas: 3-5类目标用户画像（角色、职位）
3. industries: 相关行业（2-5个）
4. pain_points: 产品解决的痛点（3-5个）
5. use_cases: 使用场景（3-5个）
6. competitor_keywords: 竞争对手可能使用的关键词（5-10个）
7. twitter_hashtags: 相关的Twitter话题标签（10-15个）
8. target_account_types: 应该爬取的账号类型（如：行业媒体、技术博主、公司账号等）

返回格式：
{{
  "keywords": ["keyword1", "keyword2", ...],
  "target_personas": ["persona1", "persona2", ...],
  "industries": ["industry1", "industry2", ...],
  "pain_points": ["pain1", "pain2", ...],
  "use_cases": ["use_case1", "use_case2", ...],
  "competitor_keywords": ["comp1", "comp2", ...],
  "twitter_hashtags": ["#tag1", "#tag2", ...],
  "target_account_types": ["type1", "type2", ...]
}}

只返回JSON，不要其他解释。"""

        try:
            if self.api_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                content = response.choices[0].message.content

            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)

            analysis = json.loads(content)
            logger.info("✓ Product analysis completed")

            # Log key analysis results
            if analysis.get('keywords'):
                logger.info(f"🔑 Keywords: {', '.join(analysis['keywords'][:5])}")
                if len(analysis['keywords']) > 5:
                    logger.info(f"   ... and {len(analysis['keywords']) - 5} more")

            if analysis.get('target_personas'):
                logger.info(f"👥 Target personas: {', '.join(analysis['target_personas'][:3])}")

            if analysis.get('industries'):
                logger.info(f"🏢 Industries: {', '.join(analysis['industries'])}")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing product: {e}")
            # Return default structure
            return {
                "keywords": [],
                "target_personas": [],
                "industries": [],
                "pain_points": [],
                "use_cases": [],
                "competitor_keywords": [],
                "twitter_hashtags": [],
                "target_account_types": []
            }

    def generate_twitter_search_queries(self, analysis: Dict) -> List[str]:
        """
        Generate Twitter search queries based on analysis

        Args:
            analysis: Product analysis dictionary

        Returns:
            List of search queries
        """
        queries = []

        # Combine keywords with personas
        keywords = analysis.get('keywords', [])[:5]
        personas = analysis.get('target_personas', [])[:3]

        for keyword in keywords:
            queries.append(keyword)

        for persona in personas:
            queries.append(persona)

        # Add hashtags
        hashtags = analysis.get('twitter_hashtags', [])[:10]
        queries.extend(hashtags)

        # Add competitor keywords
        comp_keywords = analysis.get('competitor_keywords', [])[:5]
        queries.extend(comp_keywords)

        logger.info(f"✓ Generated {len(queries)} search queries")
        return queries

    def find_seed_accounts(self, analysis: Dict) -> List[str]:
        """
        Find seed Twitter accounts to scrape based on analysis

        Args:
            analysis: Product analysis dictionary

        Returns:
            List of seed account usernames
        """
        prompt = f"""基于以下产品分析，推荐20-30个Twitter账号（只要用户名，不要@符号）。

产品信息：
- 关键词: {', '.join(analysis.get('keywords', [])[:10])}
- 目标用户: {', '.join(analysis.get('target_personas', []))}
- 行业: {', '.join(analysis.get('industries', []))}
- 话题标签: {', '.join(analysis.get('twitter_hashtags', [])[:10])}

请推荐以下类型的账号：
1. 行业媒体和新闻账号
2. 技术博主和意见领袖
3. 相关公司官方账号
4. 行业组织和社区
5. 活跃的从业者

返回格式（只返回用户名列表，每行一个，不要@符号，不要其他文字）：
techcrunch
producthunt
ycombinator
..."""

        try:
            if self.api_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                content = response.choices[0].message.content

            # Extract usernames
            lines = content.strip().split('\n')
            accounts = []

            for line in lines:
                line = line.strip()
                # Remove @ symbol if present
                line = line.replace('@', '')
                # Remove markdown, numbers, etc
                line = re.sub(r'^[\d\-\*\.\s]+', '', line)
                line = line.strip()

                # Valid Twitter username
                if line and len(line) > 2 and len(line) < 16 and re.match(r'^[a-zA-Z0-9_]+$', line):
                    accounts.append(line)

            logger.info(f"✓ Found {len(accounts)} seed accounts")

            # Log the seed accounts for visibility
            if accounts:
                logger.info(f"📍 Seed accounts: {', '.join(['@' + acc for acc in accounts[:10]])}")
                if len(accounts) > 10:
                    logger.info(f"   ... and {len(accounts) - 10} more")

            return accounts[:30]  # Limit to 30

        except Exception as e:
            logger.error(f"Error finding seed accounts: {e}")
            # Return some default tech accounts
            return [
                "techcrunch", "producthunt", "ycombinator",
                "stripe", "github", "vercel"
            ]

    def score_account(self, account_bio: str, analysis: Dict) -> float:
        """
        Score an account based on relevance to product

        Args:
            account_bio: Account bio text
            analysis: Product analysis

        Returns:
            Relevance score (0-100)
        """
        score = 0.0

        # Check keywords
        keywords = analysis.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in account_bio.lower():
                score += 10

        # Check personas
        personas = analysis.get('target_personas', [])
        for persona in personas:
            if persona.lower() in account_bio.lower():
                score += 15

        # Check industries
        industries = analysis.get('industries', [])
        for industry in industries:
            if industry.lower() in account_bio.lower():
                score += 12

        # Normalize to 0-100
        score = min(score, 100)

        return score


# Example usage
if __name__ == "__main__":
    import re

    # Test
    product_text = """
    # FleetEV - Smart Fleet Management for Electric Vehicles

    FleetEV is an AI-powered platform for managing electric vehicle fleets.

    ## Target Customers
    - Fleet managers at logistics companies
    - Car dealerships selling EVs
    - Municipal governments with EV fleets
    - Ride-sharing companies

    ## Key Features
    - Real-time vehicle tracking
    - Charging optimization
    - Predictive maintenance
    - Route planning with charging stops

    ## Pain Points We Solve
    - Expensive downtime due to charging
    - Unpredictable battery life
    - Complex route planning with charging constraints
    """

    brain = ProductBrain(api_provider="anthropic")

    print("Analyzing product...")
    analysis = brain.analyze_product(product_text)

    print("\n" + "="*60)
    print("Product Analysis:")
    print("="*60)
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    print("\n" + "="*60)
    print("Twitter Search Queries:")
    print("="*60)
    queries = brain.generate_twitter_search_queries(analysis)
    for q in queries[:10]:
        print(f"  - {q}")

    print("\n" + "="*60)
    print("Seed Accounts:")
    print("="*60)
    accounts = brain.find_seed_accounts(analysis)
    for acc in accounts[:15]:
        print(f"  - @{acc}")
