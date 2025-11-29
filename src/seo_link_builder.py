"""
SEO链接建设模块
功能：外链机会挖掘 → 邮件外推 → 关系管理
"""

import os
import json
from typing import Dict, List
from openai import OpenAI

class SEOLinkBuilder:
    """AI驱动的链接建设工具"""

    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)

    def analyze_competitor_backlinks(self, competitors: List[str]) -> List[Dict]:
        """
        分析竞争对手外链（模拟）

        实际应用中应使用：
        - Ahrefs API
        - SEMrush API
        - Moz Link Explorer API
        """
        backlinks = []

        # 模拟数据（实际应调用API）
        for competitor in competitors[:3]:
            backlinks.extend([
                {
                    'source_domain': f'techblog-{i}.com',
                    'source_url': f'https://techblog-{i}.com/article',
                    'target_competitor': competitor,
                    'anchor_text': 'great resource',
                    'domain_authority': 50 + i * 5,
                    'link_type': 'editorial'
                }
                for i in range(1, 4)
            ])

        return backlinks

    def find_link_opportunities(self, published_content: List[Dict], competitor_backlinks: List[Dict]) -> List[Dict]:
        """
        找出链接机会

        策略：
        1. 竞争对手外链来源
        2. 相关行业网站
        3. 资源页面
        4. 破损链接机会
        """
        opportunities = []

        # 从竞争对手外链提取机会
        seen_domains = set()
        for backlink in competitor_backlinks:
            domain = backlink['source_domain']

            if domain not in seen_domains:
                opportunities.append({
                    'domain': domain,
                    'url': backlink['source_url'],
                    'authority': backlink.get('domain_authority', 50),
                    'reason': f"Links to competitor {backlink['target_competitor']}",
                    'strategy': 'Competitor backlink',
                    'priority': self._calculate_priority(backlink)
                })
                seen_domains.add(domain)

        # 按优先级排序
        opportunities.sort(key=lambda x: x['priority'], reverse=True)

        return opportunities

    def generate_outreach_emails(self, opportunity: Dict, content: Dict, website_info: Dict) -> List[Dict]:
        """
        生成外推邮件（3个变体 + 跟进邮件）

        风格：
        - 个性化
        - 价值导向
        - 简短有力
        """
        domain = opportunity['domain']
        target_url = opportunity['url']
        content_title = content.get('topic', {}).get('title', 'Our Content') if content else 'Our Content'
        content_url = content.get('url', website_info.get('url', '')) if content else website_info.get('url', '')

        prompt = f"""You are an outreach email expert. Generate personalized outreach emails for link building.

**Target Website**: {domain}
**Their Content**: {target_url}
**Our Content**: {content_title} ({content_url})
**Our Website**: {website_info['name']} - {website_info['description']}

**Generate 4 emails**:
1. Initial outreach (subject + body, 150 words max)
2. Alternative initial (different angle, 150 words max)
3. Follow-up email 1 (if no response after 5 days, 100 words)
4. Final follow-up (if no response after 10 days, 80 words)

**Guidelines**:
- Personal and specific (mention their content)
- Lead with value (what's in it for them)
- Clear, specific ask
- Professional but friendly
- Include subject line for each

Return ONLY valid JSON:
[
  {{
    "type": "initial",
    "variant": 1,
    "subject": "...",
    "body": "..."
  }},
  ...
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an outreach email expert. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )

            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            emails = json.loads(response_text)

            # 添加元数据
            for email in emails:
                email['target_domain'] = domain
                email['target_url'] = target_url
                email['content_url'] = content_url

            return emails

        except Exception as e:
            print(f"   ⚠️  Outreach email generation failed: {e}")
            return []

    def _calculate_priority(self, backlink: Dict) -> int:
        """计算链接机会优先级"""
        authority = backlink.get('domain_authority', 50)
        link_type = backlink.get('link_type', 'other')

        priority = authority

        # 编辑链接加分
        if link_type == 'editorial':
            priority += 20

        return min(priority, 100)

    def _extract_json(self, text: str) -> str:
        """提取JSON"""
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        return text
