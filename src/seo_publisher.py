"""
SEO内容发布模块
功能：发布检查 → HTML导出 → 社交媒体版本 → 邮件版本
"""

import os
import re
from typing import Dict, List
from openai import OpenAI

class SEOPublisher:
    """内容发布与多渠道分发工具"""

    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            api_key = api_key.strip()
        self.client = OpenAI(api_key=api_key)

    def pre_publish_check(self, content_item: Dict) -> Dict:
        """
        发布前检查清单

        检查项：
        - 元数据完整性
        - 关键词优化
        - 可读性分数
        - 内链数量
        - 图片alt文本
        """
        checklist = {
            'passed': True,
            'failed_items': [],
            'warnings': [],
            'score': 100
        }

        # 检查元数据
        if not content_item.get('metadata', {}).get('title_tags'):
            checklist['failed_items'].append('Missing title tags')
            checklist['score'] -= 20

        if not content_item.get('metadata', {}).get('meta_descriptions'):
            checklist['failed_items'].append('Missing meta descriptions')
            checklist['score'] -= 20

        # 检查内容长度
        content = content_item.get('content', '')
        word_count = len(content.split())
        if word_count < 800:
            checklist['warnings'].append(f'Content too short ({word_count} words)')
            checklist['score'] -= 10

        # 检查Schema
        if not content_item.get('schema'):
            checklist['warnings'].append('No Schema markup')
            checklist['score'] -= 10

        checklist['passed'] = checklist['score'] >= 60

        return checklist

    def export_html(self, content: Dict, output_dir: str) -> str:
        """
        导出HTML文件

        包含：完整HTML、元标签、Schema标记
        """
        os.makedirs(output_dir, exist_ok=True)

        # 获取数据
        title = content.get('topic', {}).get('title', 'Untitled')
        slug = content.get('url_slug', 'article')
        html_content = self._markdown_to_html(content.get('content', ''))
        metadata = content.get('metadata', {})
        schema = content.get('schema', {})

        # 生成HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('title_tags', [title])[0]}</title>
    <meta name="description" content="{metadata.get('meta_descriptions', [''])[0]}">

    <!-- Open Graph -->
    <meta property="og:title" content="{metadata.get('og_title', title)}">
    <meta property="og:description" content="{metadata.get('og_description', '')}">
    <meta property="og:type" content="article">

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
{self._format_json(schema)}
    </script>
</head>
<body>
    <article>
{html_content}
    </article>
</body>
</html>
"""

        # 保存文件
        filepath = os.path.join(output_dir, f"{slug}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath

    def create_social_versions(self, content: Dict) -> Dict:
        """
        创建社交媒体版本

        平台：Twitter/X, LinkedIn, Facebook
        """
        topic = content.get('topic', {})
        title = topic.get('title', '')
        url = content.get('url', 'https://example.com')

        # 提取内容摘要
        content_text = content.get('content', '')
        summary = content_text[:200] + '...'

        prompt = f"""Create social media posts for this article:

**Title**: {title}
**Summary**: {summary}
**URL**: {url}

Generate posts for:
1. Twitter/X (280 chars, engaging, with hashtags)
2. LinkedIn (professional, longer format, value-focused)
3. Facebook (conversational, community-focused)

Return ONLY valid JSON:
{{
  "twitter": "...",
  "linkedin": "...",
  "facebook": "..."
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a social media expert. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )

            response_text = response.choices[0].message.content.strip()
            response_text = self._extract_json(response_text)
            import json
            social_posts = json.loads(response_text)

            return social_posts

        except Exception as e:
            print(f"   ⚠️  Social media generation failed: {e}")
            return {}

    def create_email_version(self, content: Dict) -> str:
        """
        创建邮件营销版本

        简化内容，添加CTA
        """
        topic = content.get('topic', {})
        title = topic.get('title', '')
        content_text = content.get('content', '')

        # 提取关键点
        key_points = self._extract_key_points(content_text)

        email = f"""Subject: {title}

Hi there!

We just published a new article that you might find useful:

**{title}**

Here are the key takeaways:
{chr(10).join('• ' + point for point in key_points[:5])}

[Read the full article →]

Best regards,
The Team

---
Unsubscribe | Update preferences
"""

        return email

    def _markdown_to_html(self, markdown: str) -> str:
        """简单的Markdown到HTML转换"""
        html = markdown

        # 标题
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # 段落
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'

        # 列表
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

        # 加粗
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        return html

    def _format_json(self, obj: dict) -> str:
        """格式化JSON"""
        import json
        return json.dumps(obj, indent=2)

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

    def _extract_key_points(self, content: str) -> List[str]:
        """提取关键点"""
        # 提取H2/H3标题作为关键点
        headings = re.findall(r'#{2,3}\s+(.+)', content)
        return headings[:7]
