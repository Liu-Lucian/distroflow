"""
技术SEO优化模块
功能：Schema标记 → 内链优化 → 图片优化 → URL优化
"""

import os
import json
import re
from typing import Dict, List
from openai import OpenAI
from datetime import datetime

class SEOTechnicalOptimizer:
    """技术SEO优化工具"""

    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)

    def generate_schema(self, content: str, content_type: str, website_info: Dict) -> Dict:
        """
        生成Schema.org结构化数据（JSON-LD）

        支持类型：Article, FAQ, HowTo, Product, Organization
        """
        if content_type == 'Article':
            return self._generate_article_schema(content, website_info)
        elif content_type == 'FAQ':
            return self._generate_faq_schema(content)
        elif content_type == 'HowTo':
            return self._generate_howto_schema(content)
        else:
            return {}

    def _generate_article_schema(self, content: str, website_info: Dict) -> Dict:
        """生成Article Schema"""
        # 提取标题和描述
        lines = content.split('\n')
        headline = lines[0].replace('#', '').strip() if lines else 'Article'

        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": headline,
            "author": {
                "@type": "Organization",
                "name": website_info.get('name', ''),
                "url": website_info.get('url', '')
            },
            "publisher": {
                "@type": "Organization",
                "name": website_info.get('name', ''),
                "url": website_info.get('url', ''),
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{website_info.get('url', '')}/logo.png"
                }
            },
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat(),
            "description": website_info.get('description', '')[:200],
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": website_info.get('url', '')
            }
        }

        return schema

    def _generate_faq_schema(self, content: str) -> Dict:
        """生成FAQ Schema"""
        # 使用AI提取FAQ
        prompt = f"""Extract FAQ questions and answers from this content:

{content[:1500]}

Return ONLY valid JSON array:
[
  {{"question": "...", "answer": "..."}},
  ...
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract FAQ data. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            faqs = json.loads(response_text)

            # 生成Schema
            schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq['question'],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq['answer']
                        }
                    }
                    for faq in faqs
                ]
            }

            return schema

        except Exception as e:
            print(f"   ⚠️  FAQ Schema generation failed: {e}")
            return {}

    def _generate_howto_schema(self, content: str) -> Dict:
        """生成HowTo Schema"""
        # 简化版：从内容提取步骤
        steps = re.findall(r'(?:Step \d+|^\d+[\.\)])\s*(.+)', content, re.MULTILINE)

        if not steps:
            return {}

        schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "How to Guide",
            "step": [
                {
                    "@type": "HowToStep",
                    "position": i + 1,
                    "text": step
                }
                for i, step in enumerate(steps[:10])  # 最多10步
            ]
        }

        return schema

    def suggest_internal_links(self, content: str, existing_content: List[Dict]) -> List[Dict]:
        """
        建议内链（简化版）

        实际应用中可以：
        1. 分析内容语义相似度
        2. 使用NLP匹配相关主题
        3. 考虑页面权重和链接结构
        """
        suggestions = []

        # 提取内容中的关键主题
        topics = self._extract_topics(content)

        # 匹配现有内容
        for existing in existing_content[:20]:
            existing_topics = existing.get('topics', [])
            overlap = len(set(topics) & set(existing_topics))

            if overlap > 0:
                suggestions.append({
                    'target_url': existing.get('url', ''),
                    'target_title': existing.get('title', ''),
                    'anchor_text': self._suggest_anchor(existing_topics),
                    'relevance_score': overlap,
                    'recommended_position': 'in relevant section'
                })

        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        return suggestions[:5]

    def generate_image_alt_texts(self, content: str, topic: str) -> List[Dict]:
        """
        生成图片优化建议（alt文本、文件名）
        """
        # 分析内容需要的图片
        prompt = f"""Based on this content topic and preview, suggest 5-7 images needed:

**Topic**: {topic}
**Content Preview**: {content[:500]}

For each image, provide:
1. Image description
2. SEO-optimized alt text (include keywords naturally)
3. Suggested filename (lowercase, hyphens, descriptive)
4. Where to place it in the article

Return ONLY valid JSON array:
[
  {{
    "description": "Featured image showing...",
    "alt_text": "technical interview preparation guide 2024",
    "filename": "technical-interview-prep-guide.jpg",
    "placement": "After introduction",
    "image_type": "featured | inline | infographic"
  }},
  ...
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an image SEO expert. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            images = json.loads(response_text)

            return images

        except Exception as e:
            print(f"   ⚠️  Image optimization failed: {e}")
            return []

    def generate_seo_url(self, title: str) -> str:
        """
        生成SEO友好的URL slug

        规则：
        - 小写
        - 用连字符分隔
        - 移除停用词
        - 限制长度
        """
        # 转小写
        slug = title.lower()

        # 移除特殊字符
        slug = re.sub(r'[^\w\s-]', '', slug)

        # 空格替换为连字符
        slug = re.sub(r'[\s_]+', '-', slug)

        # 移除常见停用词
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = slug.split('-')
        words = [w for w in words if w not in stop_words]

        slug = '-'.join(words)

        # 限制长度（最多60字符）
        if len(slug) > 60:
            slug = '-'.join(slug[:60].split('-')[:-1])

        # 移除首尾连字符
        slug = slug.strip('-')

        return slug

    def _extract_topics(self, content: str) -> List[str]:
        """提取内容主题（简化版）"""
        # 提取标题
        headings = re.findall(r'#{1,3}\s+(.+)', content)

        topics = []
        for heading in headings:
            words = re.findall(r'\b\w{4,}\b', heading.lower())
            topics.extend(words)

        return list(set(topics))

    def _suggest_anchor(self, topics: List[str]) -> str:
        """建议锚文本"""
        if not topics:
            return "read more"

        # 选择前2-3个主题词组成锚文本
        anchor_words = topics[:min(3, len(topics))]
        return ' '.join(anchor_words)

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


# 测试
if __name__ == "__main__":
    optimizer = SEOTechnicalOptimizer()

    website_info = {
        'name': 'HireMeAI',
        'url': 'https://interviewasssistant.com',
        'description': 'AI interview prep platform'
    }

    sample_content = """
# How to Prepare for Technical Interviews

Technical interviews can be challenging...

## Step 1: Understand the Format
Research the company's interview process...

## Step 2: Practice Coding
Solve problems on LeetCode...

## FAQ

### What should I study for a technical interview?
Focus on data structures, algorithms...

### How long should I prepare?
Typically 2-3 months for comprehensive prep...
"""

    print("🏗️  Generating Article Schema...")
    schema = optimizer.generate_schema(sample_content, 'Article', website_info)
    print(f"✅ Schema generated: {schema.get('@type', '')}\n")

    print("🖼️  Generating image optimization...")
    images = optimizer.generate_image_alt_texts(sample_content, "technical interview prep")
    print(f"✅ {len(images)} image suggestions created\n")

    print("🔗 Generating SEO URL...")
    slug = optimizer.generate_seo_url("How to Prepare for Technical Interviews in 2024")
    print(f"✅ URL slug: {slug}\n")
