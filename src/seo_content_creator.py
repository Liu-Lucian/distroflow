"""
SEO内容创作模块 - AI驱动
功能：大纲生成 → AI初稿 → 内容优化 → 元数据生成
"""

import os
import json
import re
from typing import Dict, List
from openai import OpenAI

class SEOContentCreator:
    """AI驱动的SEO内容创作工具"""

    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)

    def generate_outline(self, topic: Dict, target_keywords: List[str], website_info: Dict) -> Dict:
        """
        生成SEO优化的文章大纲

        输入：主题、目标关键词、网站信息
        输出：结构化大纲（H1/H2/H3）
        """
        prompt = f"""You are an expert SEO content strategist. Create a detailed article outline for this topic:

**Topic**: {topic['title']}
**Primary Keyword**: {topic['primary_keyword']}
**Target Keywords**: {', '.join(target_keywords)}
**Intent**: {topic['intent']}
**Funnel Stage**: {topic['funnel_stage']}
**Content Type**: {topic['content_type']}

**Website Context**:
- Name: {website_info['name']}
- Description: {website_info['description']}
- Brand Voice: {website_info['brand_voice']}

**Requirements**:
1. Create an engaging H1 title (include primary keyword naturally)
2. Write 5-8 H2 sections covering different angles
3. Each H2 should have 2-4 H3 subsections
4. Include these elements:
   - Introduction (hook + what readers will learn)
   - Main content sections (detailed, actionable)
   - FAQ section (5-7 questions)
   - Conclusion with CTA
5. Suggest semantic keywords for each section
6. Note internal link opportunities

**Output Format**: Return ONLY valid JSON, nothing else.

Example structure:
{{
  "h1": "How to Ace Your Technical Interview in 2024",
  "meta_description": "...",
  "introduction": {{
    "hook": "...",
    "promise": "..."
  }},
  "sections": [
    {{
      "h2": "Understanding Technical Interview Formats",
      "semantic_keywords": ["coding interview", "system design"],
      "subsections": [
        {{
          "h3": "Coding Challenges",
          "key_points": ["...", "..."]
        }},
        ...
      ]
    }},
    ...
  ],
  "faq": [
    {{"question": "...", "answer": "..."}},
    ...
  ],
  "conclusion": {{
    "summary": "...",
    "cta": "..."
  }},
  "internal_links": ["topic1", "topic2"],
  "word_count_target": 2500
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO content strategist. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        response_text = response.choices[0].message.content.strip()

        # 提取JSON
        response_text = self._extract_json(response_text)
        outline = json.loads(response_text)

        return outline

    def generate_draft(self, outline: Dict, brand_voice: str) -> str:
        """
        生成AI初稿

        输入：大纲、品牌调性
        输出：完整文章初稿（Markdown格式）
        """
        # 将大纲转换为提示词
        outline_text = self._outline_to_text(outline)

        prompt = f"""You are a professional content writer. Write a complete, high-quality SEO article based on this outline:

{outline_text}

**Brand Voice**: {brand_voice}

**Writing Guidelines**:
1. Natural, conversational tone (avoid robotic AI writing)
2. Use short paragraphs (2-3 sentences max)
3. Include actionable tips and examples
4. Add transition words for flow
5. Write for 8th-grade reading level (Flesch score 60-70)
6. Use active voice
7. Include statistics and data where appropriate (you can make them realistic)
8. Add bullet points and numbered lists
9. Include clear H2/H3 structure
10. Target word count: {outline.get('word_count_target', 2000)} words

**Output Format**: Markdown format with proper headers (##, ###)

Write the complete article now:
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional SEO content writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000  # 长文章需要更多tokens
        )

        draft = response.choices[0].message.content.strip()
        return draft

    def optimize_content(self, draft: str, target_keywords: List[str]) -> str:
        """
        优化内容（关键词密度、可读性、SEO最佳实践）

        输入：初稿、目标关键词
        输出：优化后的内容
        """
        prompt = f"""You are an SEO optimization expert. Review and optimize this content:

**Content**:
{draft[:3000]}  # 限制输入长度

**Target Keywords**: {', '.join(target_keywords[:10])}

**Optimization Tasks**:
1. Check keyword density (aim for 1-2% for primary keyword)
2. Add semantic keywords naturally
3. Improve readability:
   - Shorten long sentences
   - Add transition words
   - Use active voice
4. Enhance engagement:
   - Add rhetorical questions
   - Include power words
   - Improve hook in introduction
5. Add structured elements:
   - Numbered lists where appropriate
   - Bullet points for key takeaways
   - Bold important phrases
6. Ensure proper keyword placement:
   - In first 100 words
   - In H2/H3 headings
   - In conclusion

**Output**: Return the optimized content in Markdown format.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO content optimizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=4000
        )

        optimized = response.choices[0].message.content.strip()
        return optimized

    def generate_metadata(self, content: str, target_keyword: str) -> Dict:
        """
        生成SEO元数据

        输出：
        - Title标签（5个变体）
        - Meta描述（3个变体）
        - URL slug
        - Open Graph标签
        """
        # 提取文章前500字作为上下文
        content_preview = content[:500]

        prompt = f"""You are an SEO metadata expert. Generate optimized metadata for this content:

**Content Preview**:
{content_preview}

**Primary Keyword**: {target_keyword}

**Generate**:
1. 5 title tag variants (50-60 characters each)
   - Include primary keyword
   - Compelling and click-worthy
   - Use numbers, power words, current year
2. 3 meta description variants (150-160 characters each)
   - Include primary keyword and CTA
   - Compelling value proposition
3. URL slug (SEO-friendly, lowercase, hyphens)
4. Open Graph title and description
5. 5-7 focus keyphrases

**Output Format**: Return ONLY valid JSON, nothing else.

Example:
{{
  "title_tags": [
    "{target_keyword.title()}: Complete Guide (2024)",
    ...
  ],
  "meta_descriptions": [
    "Learn {target_keyword} with our complete guide. Discover expert tips, strategies, and best practices. Get started today!",
    ...
  ],
  "url_slug": "complete-guide-to-{target_keyword.lower().replace(' ', '-')}",
  "og_title": "...",
  "og_description": "...",
  "focus_keyphrases": ["phrase1", "phrase2", ...]
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an SEO metadata expert. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        response_text = response.choices[0].message.content.strip()
        response_text = self._extract_json(response_text)
        metadata = json.loads(response_text)

        return metadata

    def generate_internal_links(self, content: str, existing_content: List[Dict]) -> List[Dict]:
        """
        生成内链建议

        分析内容，推荐相关内链锚文本和目标页面
        """
        if not existing_content:
            return []

        # 简化：提取内容中的关键主题词
        topics = self._extract_topics(content)

        # 匹配现有内容
        link_suggestions = []
        for existing in existing_content[:10]:  # 限制前10个
            existing_topics = existing.get('topics', [])

            # 计算主题重叠度
            overlap = len(set(topics) & set(existing_topics))

            if overlap > 0:
                link_suggestions.append({
                    'target_url': existing.get('url', ''),
                    'target_title': existing.get('title', ''),
                    'anchor_text': self._suggest_anchor_text(existing),
                    'relevance': overlap,
                    'position': 'naturally in content'  # AI可以指定具体位置
                })

        # 按相关度排序
        link_suggestions.sort(key=lambda x: x['relevance'], reverse=True)

        return link_suggestions[:5]  # 最多5个内链

    def _outline_to_text(self, outline: Dict) -> str:
        """将大纲JSON转换为文本格式"""
        text = f"# {outline.get('h1', '')}\n\n"

        if 'introduction' in outline:
            text += f"**Introduction**\n{outline['introduction']}\n\n"

        if 'sections' in outline:
            for section in outline['sections']:
                text += f"## {section.get('h2', '')}\n"
                if 'subsections' in section:
                    for sub in section['subsections']:
                        text += f"### {sub.get('h3', '')}\n"
                text += "\n"

        if 'faq' in outline:
            text += "## FAQ\n"
            for faq in outline['faq']:
                text += f"Q: {faq.get('question', '')}\n"
                text += f"A: {faq.get('answer', '')}\n\n"

        return text

    def _extract_json(self, text: str) -> str:
        """从响应中提取JSON"""
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()

        return text

    def _extract_topics(self, content: str) -> List[str]:
        """简单提取主题词（实际应用中可以用NLP）"""
        # 提取H2/H3标题
        headings = re.findall(r'#{2,3}\s+(.+)', content)

        # 提取关键词（简化版）
        topics = []
        for heading in headings:
            # 移除特殊字符，分割单词
            words = re.findall(r'\b\w{4,}\b', heading.lower())
            topics.extend(words)

        return list(set(topics))

    def _suggest_anchor_text(self, existing_content: Dict) -> str:
        """建议锚文本"""
        title = existing_content.get('title', '')

        # 移除数字、年份、特殊符号
        anchor = re.sub(r'\d{4}', '', title)
        anchor = re.sub(r'[^\w\s]', '', anchor)
        anchor = anchor.strip()

        # 限制长度
        words = anchor.split()
        if len(words) > 5:
            anchor = ' '.join(words[:5])

        return anchor


# 测试代码
if __name__ == "__main__":
    creator = SEOContentCreator()

    # 测试数据
    topic = {
        'title': 'How to Prepare for Technical Interviews',
        'primary_keyword': 'technical interview preparation',
        'keywords': ['technical interview', 'coding interview', 'interview prep', 'mock interview'],
        'intent': 'informational',
        'funnel_stage': 'TOFU',
        'content_type': 'blog_post'
    }

    website_info = {
        'name': 'HireMeAI',
        'description': 'AI-powered interview prep platform',
        'brand_voice': 'Professional, helpful, innovative'
    }

    print("📋 Generating outline...\n")
    outline = creator.generate_outline(topic, topic['keywords'], website_info)
    print(f"✅ Outline created:")
    print(f"   H1: {outline.get('h1', '')}")
    print(f"   Sections: {len(outline.get('sections', []))}")
    print(f"   FAQ: {len(outline.get('faq', []))}")

    print("\n🤖 Generating draft...\n")
    draft = creator.generate_draft(outline, website_info['brand_voice'])
    print(f"✅ Draft created: {len(draft)} characters\n")
    print(draft[:500] + "...\n")

    print("🏷️  Generating metadata...\n")
    metadata = creator.generate_metadata(draft, topic['primary_keyword'])
    print(f"✅ Metadata created:")
    print(f"   Title variants: {len(metadata.get('title_tags', []))}")
    print(f"   First title: {metadata.get('title_tags', [''])[0]}")
    print(f"   URL slug: {metadata.get('url_slug', '')}")
