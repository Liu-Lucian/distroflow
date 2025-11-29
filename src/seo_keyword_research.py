"""
SEO关键词研究模块 - AI驱动
功能：种子关键词生成 → 关键词扩展 → 竞争分析 → 内容地图
"""

import os
import json
import time
from typing import List, Dict
from openai import OpenAI

class SEOKeywordResearcher:
    """AI驱动的SEO关键词研究工具"""

    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)

    def generate_seed_keywords(self, website_info: Dict, target_audience: str, industry: str, count: int = 50) -> List[str]:
        """
        AI生成种子关键词

        输入：网站信息、目标受众、行业
        输出：50-100个种子关键词
        """
        prompt = f"""You are an SEO keyword research expert. Generate {count} seed keywords for this business:

**Website**: {website_info['name']} ({website_info['url']})
**Description**: {website_info['description']}
**Target Audience**: {target_audience}
**Industry**: {industry}

**Requirements**:
1. Mix of:
   - Core product/service terms
   - Problem-solving keywords (how to, what is, best way to)
   - Long-tail keywords (3-5 words)
   - Question keywords (who, what, where, when, why, how)
   - Comparison keywords (vs, versus, alternative, compare)
   - Intent-based keywords (buy, learn, find, get)

2. Cover the entire funnel:
   - Top of funnel (TOFU): Educational, awareness
   - Middle of funnel (MOFU): Consideration, comparison
   - Bottom of funnel (BOFU): Decision, purchase

3. Include semantic variations and synonyms

**Output Format**: Return ONLY a JSON array of {count} keyword strings, nothing else.

Example:
["ai interview prep", "how to prepare for technical interview", "mock interview platform", ...]
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO keyword research expert. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        response_text = response.choices[0].message.content.strip()

        # 提取JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        keywords = json.loads(response_text)
        return keywords

    def expand_keywords(self, seed_keywords: List[str]) -> List[Dict]:
        """
        扩展关键词（添加难度、流量、CPC等元数据）

        实际应用中可以集成：
        - Ahrefs API
        - SEMrush API
        - Google Keyword Planner API
        """
        expanded = []

        for keyword in seed_keywords:
            # 模拟API数据（实际应替换为真实API调用）
            expanded.append({
                'keyword': keyword,
                'search_volume': self._estimate_search_volume(keyword),
                'difficulty': self._estimate_difficulty(keyword),
                'cpc': self._estimate_cpc(keyword),
                'intent': self._classify_intent(keyword),
                'funnel_stage': self._classify_funnel_stage(keyword)
            })

        return expanded

    def _estimate_search_volume(self, keyword: str) -> int:
        """估算搜索量（简化版，实际应用API）"""
        # 基于关键词长度估算
        word_count = len(keyword.split())
        if word_count <= 2:
            return 10000  # 短尾词
        elif word_count <= 4:
            return 2000   # 中尾词
        else:
            return 500    # 长尾词

    def _estimate_difficulty(self, keyword: str) -> int:
        """估算SEO难度（0-100）"""
        word_count = len(keyword.split())
        if word_count <= 2:
            return 75  # 短尾词难度高
        elif word_count <= 4:
            return 45  # 中尾词中等难度
        else:
            return 25  # 长尾词难度低

    def _estimate_cpc(self, keyword: str) -> float:
        """估算每次点击成本"""
        if any(word in keyword.lower() for word in ['buy', 'purchase', 'price', 'cost']):
            return 5.0  # 购买意图CPC高
        elif any(word in keyword.lower() for word in ['best', 'top', 'review']):
            return 2.5  # 比较意图中等CPC
        else:
            return 0.5  # 信息意图CPC低

    def _classify_intent(self, keyword: str) -> str:
        """分类搜索意图"""
        keyword_lower = keyword.lower()

        if any(word in keyword_lower for word in ['buy', 'purchase', 'price', 'order', 'hire']):
            return 'transactional'
        elif any(word in keyword_lower for word in ['best', 'top', 'vs', 'versus', 'compare', 'review']):
            return 'commercial'
        elif any(word in keyword_lower for word in ['how to', 'what is', 'guide', 'tutorial', 'learn']):
            return 'informational'
        else:
            return 'navigational'

    def _classify_funnel_stage(self, keyword: str) -> str:
        """分类漏斗阶段"""
        intent = self._classify_intent(keyword)

        if intent == 'informational':
            return 'TOFU'  # Top of funnel
        elif intent == 'commercial':
            return 'MOFU'  # Middle of funnel
        elif intent == 'transactional':
            return 'BOFU'  # Bottom of funnel
        else:
            return 'TOFU'

    def cluster_by_intent(self, keywords: List[Dict]) -> Dict[str, List[Dict]]:
        """按意图聚类关键词"""
        clusters = {
            'informational': [],
            'commercial': [],
            'transactional': [],
            'navigational': []
        }

        for kw in keywords:
            intent = kw.get('intent', 'informational')
            clusters[intent].append(kw)

        return clusters

    def analyze_competitors(self, industry: str, count: int = 5) -> List[Dict]:
        """
        AI分析竞争对手

        实际应用中可以：
        1. 爬取竞争对手网站
        2. 使用Ahrefs/SEMrush API获取竞品关键词
        3. AI分析竞品内容策略
        """
        prompt = f"""You are an SEO competitive analyst. Identify the top {count} competitors in the {industry} industry.

For each competitor, provide:
1. Company name
2. Website URL
3. Their main SEO focus (keywords, content strategy)
4. What they do well
5. Content gaps we can exploit

**Output Format**: Return ONLY a JSON array, nothing else.

Example:
[
  {{
    "name": "Competitor A",
    "url": "https://example.com",
    "seo_focus": ["keyword1", "keyword2"],
    "strengths": ["Strong blog content", "High domain authority"],
    "gaps": ["No video content", "Weak social media presence"]
  }},
  ...
]
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO competitive analyst. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        response_text = response.choices[0].message.content.strip()

        # 提取JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        competitors = json.loads(response_text)
        return competitors

    def create_content_map(self, clustered_keywords: Dict[str, List[Dict]]) -> List[Dict]:
        """
        创建内容地图（主题聚类）

        将关键词组织成内容主题，每个主题包含：
        - 主关键词
        - 支持关键词
        - 内容类型（博客、着陆页、视频等）
        - 优先级
        """
        content_map = []

        # 为每个意图类别创建主题
        for intent, keywords in clustered_keywords.items():
            if not keywords:
                continue

            # 按搜索量排序
            sorted_kw = sorted(keywords, key=lambda x: x.get('search_volume', 0), reverse=True)

            # 每5个关键词创建一个主题
            for i in range(0, len(sorted_kw), 5):
                keyword_group = sorted_kw[i:i+5]

                primary_kw = keyword_group[0]
                supporting_kw = [kw['keyword'] for kw in keyword_group[1:]]

                # 生成主题标题
                title = self._generate_topic_title(primary_kw['keyword'], intent)

                content_map.append({
                    'title': title,
                    'primary_keyword': primary_kw['keyword'],
                    'keywords': [kw['keyword'] for kw in keyword_group],
                    'intent': intent,
                    'funnel_stage': primary_kw.get('funnel_stage', 'TOFU'),
                    'content_type': self._suggest_content_type(intent),
                    'priority': self._calculate_priority(primary_kw),
                    'estimated_traffic': sum(kw.get('search_volume', 0) for kw in keyword_group),
                    'difficulty': primary_kw.get('difficulty', 50),
                })

        # 按优先级排序
        content_map.sort(key=lambda x: x['priority'], reverse=True)

        return content_map

    def _generate_topic_title(self, keyword: str, intent: str) -> str:
        """生成主题标题"""
        if intent == 'informational':
            if keyword.startswith('how '):
                return keyword.title()
            elif keyword.startswith('what '):
                return keyword.title()
            else:
                return f"The Ultimate Guide to {keyword.title()}"
        elif intent == 'commercial':
            return f"Best {keyword.title()}: Complete Comparison Guide"
        elif intent == 'transactional':
            return f"Get Started with {keyword.title()}"
        else:
            return keyword.title()

    def _suggest_content_type(self, intent: str) -> str:
        """建议内容类型"""
        if intent == 'informational':
            return 'blog_post'
        elif intent == 'commercial':
            return 'comparison_page'
        elif intent == 'transactional':
            return 'landing_page'
        else:
            return 'blog_post'

    def _calculate_priority(self, keyword: Dict) -> int:
        """
        计算优先级（0-100）

        考虑因素：
        - 搜索量
        - 难度（越低越好）
        - 商业价值（CPC）
        """
        search_volume = keyword.get('search_volume', 0)
        difficulty = keyword.get('difficulty', 50)
        cpc = keyword.get('cpc', 0)

        # 归一化分数
        volume_score = min(search_volume / 1000, 100)  # 最高100分
        difficulty_score = 100 - difficulty  # 难度越低分数越高
        commercial_score = min(cpc * 10, 100)  # CPC越高分数越高

        # 加权平均
        priority = (volume_score * 0.4 + difficulty_score * 0.4 + commercial_score * 0.2)

        return int(priority)


# 测试代码
if __name__ == "__main__":
    researcher = SEOKeywordResearcher()

    # 测试生成种子关键词
    website_info = {
        'name': 'HireMeAI',
        'url': 'https://interviewasssistant.com',
        'description': 'AI-powered interview preparation platform'
    }

    print("🌱 Generating seed keywords...\n")
    seed_keywords = researcher.generate_seed_keywords(
        website_info=website_info,
        target_audience='Job seekers, developers',
        industry='EdTech',
        count=20
    )

    print(f"✅ Generated {len(seed_keywords)} seed keywords:\n")
    for i, kw in enumerate(seed_keywords[:10], 1):
        print(f"  {i}. {kw}")
    print(f"  ... and {len(seed_keywords) - 10} more\n")

    # 测试扩展关键词
    print("🔍 Expanding keywords...\n")
    expanded = researcher.expand_keywords(seed_keywords)

    print(f"✅ Expanded with metadata:\n")
    for kw in expanded[:5]:
        print(f"  '{kw['keyword']}'")
        print(f"    Volume: {kw['search_volume']}, Difficulty: {kw['difficulty']}, Intent: {kw['intent']}")

    # 测试聚类
    print("\n📊 Clustering by intent...\n")
    clustered = researcher.cluster_by_intent(expanded)
    for intent, keywords in clustered.items():
        print(f"  {intent.upper()}: {len(keywords)} keywords")

    # 测试内容地图
    print("\n🗺️  Creating content map...\n")
    content_map = researcher.create_content_map(clustered)
    print(f"✅ Created {len(content_map)} content topics:\n")
    for topic in content_map[:5]:
        print(f"  • {topic['title']}")
        print(f"    Priority: {topic['priority']}, Traffic: {topic['estimated_traffic']}")
