"""
LLM辅助联系方式发现 - LLM-Assisted Contact Discovery
Use AI to infer contact information from context
"""

import os
import json
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMContactFinder:
    """Use LLM to discover and infer contact information"""

    def __init__(self, api_provider: str = "anthropic"):
        """
        Initialize LLM Contact Finder

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
            raise ValueError("Only Anthropic supported for now")

    def analyze_profile_for_contacts(self, profile_data: Dict) -> Dict:
        """
        Use LLM to analyze profile and suggest where to find contacts

        Args:
            profile_data: User profile information

        Returns:
            Dictionary with AI suggestions
        """
        prompt = f"""分析以下Twitter用户资料，找出所有可能的联系方式线索。

用户资料:
- 用户名: {profile_data.get('username', 'N/A')}
- 姓名: {profile_data.get('name', 'N/A')}
- Bio: {profile_data.get('bio', 'N/A')}
- 位置: {profile_data.get('location', 'N/A')}
- 网站: {profile_data.get('website', 'N/A')}
- 置顶推文: {profile_data.get('pinned_tweet', 'N/A')[:200]}
- 最近推文: {' | '.join(profile_data.get('recent_tweets', [])[:3])[:500]}

请分析并返回JSON格式:
{{
  "likely_has_email": true/false,
  "confidence_score": 0-100,
  "contact_clues": [
    "线索1", "线索2"...
  ],
  "suggested_sources": [
    {{"source": "个人网站", "url": "https://...", "priority": "high/medium/low"}},
    {{"source": "LinkedIn", "url": "https://...", "priority": "high/medium/low"}}
  ],
  "inferred_role": "职位/角色",
  "company_name": "公司名称 (如果能推断)",
  "company_domain": "公司域名 (如果能推断)",
  "possible_emails": [
    {{"email": "推测的邮箱", "confidence": 0-100, "reasoning": "推理依据"}}
  ],
  "contact_strategy": "建议的联系策略"
}}

关键任务:
1. 识别所有提到的外部链接 (个人网站、Linktree、GitHub等)
2. 从bio和推文中推断职位、公司
3. 如果有公司网站，推测可能的邮箱格式
4. 评估找到邮箱的可能性
5. 建议最有可能找到联系方式的来源

只返回JSON，不要其他解释。"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Extract JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)

            analysis = json.loads(content)
            logger.info(f"✓ LLM analyzed profile for @{profile_data.get('username')}")

            return analysis

        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return {
                'likely_has_email': False,
                'confidence_score': 0,
                'contact_clues': [],
                'suggested_sources': [],
                'error': str(e)
            }

    def infer_company_from_bio(self, bio: str, name: str) -> Optional[Dict]:
        """
        Use LLM to infer company information from bio

        Args:
            bio: User bio text
            name: User name

        Returns:
            Company information
        """
        prompt = f"""从以下Twitter bio中推断用户的公司信息。

姓名: {name}
Bio: {bio}

请返回JSON格式:
{{
  "company_name": "公司名称",
  "company_domain": "公司域名 (如果能推断)",
  "role_title": "职位",
  "confidence": 0-100,
  "reasoning": "推理依据"
}}

如果无法推断，返回null值。只返回JSON。"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)

            company_info = json.loads(content)
            return company_info

        except Exception as e:
            logger.error(f"Error inferring company: {e}")
            return None

    def suggest_search_queries(self, profile_data: Dict) -> List[str]:
        """
        Use LLM to suggest Google/Bing search queries to find contact info

        Args:
            profile_data: User profile information

        Returns:
            List of search queries
        """
        prompt = f"""为以下用户生成5-10个Google搜索查询，用于查找他们的联系邮箱。

用户信息:
- 姓名: {profile_data.get('name')}
- Bio: {profile_data.get('bio')}
- 网站: {profile_data.get('website')}

返回JSON格式:
{{
  "search_queries": [
    "搜索查询1",
    "搜索查询2",
    ...
  ]
}}

搜索查询应该包括:
1. 姓名 + email
2. 姓名 + contact
3. 姓名 + 公司名
4. 网站域名 + team/about
5. 专业的搜索运算符 (site:, inurl:, etc.)

只返回JSON。"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)

            result = json.loads(content)
            return result.get('search_queries', [])

        except Exception as e:
            logger.error(f"Error generating search queries: {e}")
            return []

    def analyze_website_for_contacts(self, website_html: str, user_name: str) -> Dict:
        """
        Use LLM to analyze website HTML and find contact info

        Args:
            website_html: HTML content of website
            user_name: User name to match

        Returns:
            Extracted contact information
        """
        # Truncate HTML if too long
        if len(website_html) > 8000:
            website_html = website_html[:8000] + "... [truncated]"

        prompt = f"""分析以下网站HTML，为 {user_name} 查找联系信息。

HTML内容:
{website_html}

请提取:
1. 所有邮箱地址
2. 所有电话号码
3. 联系表单链接
4. 团队成员页面链接
5. 任何可能相关的联系方式

返回JSON格式:
{{
  "emails": ["email1", "email2"],
  "phones": ["phone1", "phone2"],
  "contact_forms": ["url1", "url2"],
  "team_pages": ["url1", "url2"],
  "likely_owner_email": "最可能是该用户的邮箱",
  "confidence": 0-100
}}

只返回JSON。"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)

            contacts = json.loads(content)
            return contacts

        except Exception as e:
            logger.error(f"Error analyzing website: {e}")
            return {'emails': [], 'phones': [], 'error': str(e)}

    def prioritize_external_resources(self, external_links: List[Dict]) -> List[Dict]:
        """
        Use LLM to prioritize which external resources to scrape

        Args:
            external_links: List of external links found

        Returns:
            Prioritized list with reasoning
        """
        links_str = '\n'.join([f"- {link.get('platform', 'unknown')}: {link.get('url')}" for link in external_links])

        prompt = f"""对以下外部资源进行优先级排序，判断哪些最可能包含联系邮箱。

外部链接:
{links_str}

返回JSON格式:
{{
  "prioritized_links": [
    {{
      "url": "链接",
      "priority": "high/medium/low",
      "expected_contact_types": ["email", "phone", "social"],
      "reasoning": "为什么优先级高/低"
    }}
  ]
}}

优先级判断标准:
- High: 个人网站、Linktree、个人博客
- Medium: GitHub profile、Medium profile
- Low: 社交媒体链接

只返回JSON。"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)

            result = json.loads(content)
            return result.get('prioritized_links', [])

        except Exception as e:
            logger.error(f"Error prioritizing links: {e}")
            return []


# Example usage
if __name__ == "__main__":
    finder = LLMContactFinder()

    # Test profile analysis
    test_profile = {
        'username': 'johndoe',
        'name': 'John Doe',
        'bio': 'Founder @TechStartup | Building AI tools for developers | Previously @Google | Reach out: https://johndoe.com',
        'website': 'https://johndoe.com',
        'location': 'San Francisco, CA',
        'pinned_tweet': 'Excited to announce our new product launch! Check it out at https://techstartup.io',
        'recent_tweets': [
            'Working on some exciting AI projects...',
            'Great meeting with the team today',
            'Check out my latest blog post'
        ]
    }

    print("=" * 60)
    print("LLM Contact Analysis")
    print("=" * 60)

    analysis = finder.analyze_profile_for_contacts(test_profile)

    print(f"\nProfile Analysis for @{test_profile['username']}:")
    print(f"  Likely has email: {analysis.get('likely_has_email')}")
    print(f"  Confidence: {analysis.get('confidence_score')}%")
    print(f"  Inferred role: {analysis.get('inferred_role')}")
    print(f"  Company: {analysis.get('company_name')}")
    print(f"  Company domain: {analysis.get('company_domain')}")

    print(f"\nContact Clues:")
    for clue in analysis.get('contact_clues', []):
        print(f"  - {clue}")

    print(f"\nSuggested Sources:")
    for source in analysis.get('suggested_sources', []):
        print(f"  - {source['source']} ({source['priority']}): {source.get('url', 'N/A')}")

    print(f"\nPossible Emails:")
    for email_guess in analysis.get('possible_emails', []):
        print(f"  - {email_guess['email']} ({email_guess['confidence']}%)")
        print(f"    Reasoning: {email_guess['reasoning']}")

    print(f"\nContact Strategy:")
    print(f"  {analysis.get('contact_strategy')}")
