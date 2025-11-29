#!/usr/bin/env python3
"""
社交媒体内容转换器
将SEO文章智能转换为各平台适合的格式
"""

import re
import json
from typing import Dict, List
from openai import OpenAI
import os

class SocialContentTransformer:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # 各平台内容策略
        self.platform_strategies = {
            'tiktok': {
                'format': '短视频文案',
                'length': '50-150字',
                'style': '娱乐性强、Hook前3秒、带emoji',
                'cta': '评论区见👇 / Link in bio'
            },
            'github': {
                'format': 'README.md',
                'length': '500-2000字',
                'style': '技术详细、代码示例、架构说明',
                'cta': 'Star ⭐ if helpful'
            },
            'instagram': {
                'format': '图片配文 + Carousel描述',
                'length': '100-300字 + hashtags',
                'style': '视觉化、故事性、品牌调性',
                'cta': 'Link in bio 🔗'
            },
            'twitter': {
                'format': 'Thread (线程)',
                'length': '每条≤280字，3-8条thread',
                'style': '简洁、技术圈、带数据',
                'cta': '完整文章见👇'
            },
            'reddit': {
                'format': '长文帖 + 讨论',
                'length': '500-1500字',
                'style': '深度、透明、非广告感',
                'cta': 'Happy to answer questions'
            },
            'linkedin': {
                'format': '专业长文',
                'length': '300-1000字',
                'style': 'B2B、案例研究、行业洞察',
                'cta': 'Learn more / DM for details'
            }
        }

    def html_to_plain_text(self, html_content: str) -> str:
        """HTML转纯文本"""
        # 移除HTML标签
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '\n', text)

        # 清理空行和空格
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&[a-z]+;', '', text)

        return text.strip()

    def transform_for_tiktok(self, content: str, title: str) -> Dict:
        """转换为TikTok短视频文案"""
        prompt = f"""Convert this article into TikTok video script format:

Title: {title}
Content: {content[:1000]}

CRITICAL BRANDING:
- Product: HireMeAI
- Official Website: https://interviewasssistant.com
- Focus: AI-powered interview preparation platform
- MUST mention in CTA

Requirements:
1. Hook (前3秒吸引): 开头用问题或震撼事实
2. Body (30-45秒): 3个核心要点，简洁有力
3. CTA: Link in bio → https://interviewasssistant.com
4. Add emojis naturally
5. Length: 50-150 characters
6. Tone: 娱乐性+教育性
7. Mention HireMeAI naturally in script

Output format:
[HOOK] ...
[POINT 1] ...
[POINT 2] ...
[POINT 3] ...
[CTA] Link in bio: https://interviewasssistant.com 👆

Hashtags: #HireMeAI #AI #interviews #tech (5-8个)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        script = response.choices[0].message.content

        # 提取hashtags
        hashtags_match = re.search(r'Hashtags?: (.+)', script)
        hashtags = hashtags_match.group(1) if hashtags_match else "#AI #tech #career"

        return {
            'platform': 'tiktok',
            'format': 'video_script',
            'content': script,
            'hashtags': hashtags,
            'duration': '15-60s',
            'posting_time': '晚上18:00-22:00'
        }

    def transform_for_github(self, content: str, title: str, html_file_path: str) -> Dict:
        """转换为GitHub README格式"""
        prompt = f"""Convert this article into a GitHub README.md for an open-source project:

Title: {title}
Content: {content[:2000]}

CRITICAL BRANDING:
- Product: HireMeAI
- Official Website: https://interviewasssistant.com
- Project Description: AI-powered interview preparation platform
- Use this as the main project URL and homepage

Requirements:
1. Project title: HireMeAI with badges
2. Overview: Link to https://interviewasssistant.com
3. Key Features (bullet points)
4. Quick Start / Installation
5. Usage Example (code snippet)
6. Technical Architecture
7. Contributing guidelines
8. Website: https://interviewasssistant.com
9. License

Output in proper Markdown format with code blocks, tables, and emojis.
Target audience: Developers & AI enthusiasts
Tone: Technical, clear, professional
Include https://interviewasssistant.com in header and footer
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        readme = response.choices[0].message.content

        return {
            'platform': 'github',
            'format': 'README.md',
            'content': readme,
            'files': {
                'README.md': readme,
                'docs/GUIDE.md': f"Full guide: {html_file_path}"
            },
            'repo_topics': ['ai', 'interview', 'automation', 'seo', 'hiremeai']
        }

    def transform_for_instagram(self, content: str, title: str) -> Dict:
        """转换为Instagram帖子"""
        prompt = f"""Convert this article into Instagram post content:

Title: {title}
Content: {content[:1000]}

CRITICAL BRANDING:
- Product: HireMeAI
- Official Website: https://interviewasssistant.com
- Focus: AI-powered interview preparation platform
- Mention "Link in bio" pointing to this URL

Requirements:
1. Caption (100-200 words): 故事性开头，3个要点，CTA with Link in bio
2. Carousel slides (5-8张卡片):
   - Slide 1: Title + Hook
   - Slides 2-6: 核心要点（每张1个）
   - Last slide: CTA → Link in bio: https://interviewasssistant.com
3. Hashtags: Include #HireMeAI plus 20-30个相关标签
4. Tone: 专业但易懂，鼓励性
5. Add line breaks for readability
6. Mention HireMeAI naturally in caption

Output format:
[CAPTION]
...mention HireMeAI...
Link in bio 🔗

[SLIDE 1 - Title]
...

[SLIDE 2 - Point 1]
...

[HASHTAGS]
#HireMeAI #AI #JobSearch ...
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        post_content = response.choices[0].message.content

        # 提取caption和slides
        caption_match = re.search(r'\[CAPTION\](.*?)(?=\[SLIDE|\[HASHTAGS|$)', post_content, re.DOTALL)
        caption = caption_match.group(1).strip() if caption_match else post_content[:200]

        slides = re.findall(r'\[SLIDE \d+[^\]]*\](.*?)(?=\[SLIDE|\[HASHTAGS|$)', post_content, re.DOTALL)

        hashtags_match = re.search(r'\[HASHTAGS\](.*)', post_content, re.DOTALL)
        hashtags = hashtags_match.group(1).strip() if hashtags_match else "#AI #CareerTips"

        return {
            'platform': 'instagram',
            'format': 'carousel_post',
            'caption': caption,
            'slides': [s.strip() for s in slides] if slides else [caption],
            'hashtags': hashtags,
            'posting_time': '中午12:00或晚上19:00'
        }

    def transform_for_twitter(self, content: str, title: str) -> Dict:
        """转换为Twitter线程"""
        prompt = f"""Convert this article into a Twitter thread (5-8 tweets):

Title: {title}
Content: {content[:1500]}

CRITICAL BRANDING:
- Product: HireMeAI
- Official Website: https://interviewasssistant.com
- ALWAYS use this exact URL in CTAs
- Focus: AI-powered interview preparation platform

Requirements:
1. Tweet 1 (Hook): 问题或惊人数据 + HireMeAI介绍 + thread预告 👇
2. Tweets 2-6: 核心要点（每条≤280字）
3. Last tweet: Strong CTA with https://interviewasssistant.com
4. Each tweet stands alone
5. Use numbers (1/, 2/, etc)
6. Add emojis naturally
7. Technical but accessible tone
8. Mention HireMeAI by name
9. MUST include https://interviewasssistant.com in final tweet

Output each tweet separately:
[TWEET 1]
...

[TWEET 2]
...
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        thread = response.choices[0].message.content

        # 提取所有tweets
        tweets = re.findall(r'\[TWEET \d+\](.*?)(?=\[TWEET|$)', thread, re.DOTALL)
        tweets = [t.strip() for t in tweets if t.strip()]

        return {
            'platform': 'twitter',
            'format': 'thread',
            'tweets': tweets,
            'total_tweets': len(tweets),
            'posting_time': '工作日早上9:00-11:00'
        }

    def transform_for_reddit(self, content: str, title: str, subreddit: str = 'Entrepreneur') -> Dict:
        """转换为Reddit帖子"""
        prompt = f"""Convert this article into a Reddit post for r/{subreddit}:

Title: {title}
Content: {content[:2000]}

CRITICAL BRANDING:
- Product: HireMeAI - AI interview preparation platform
- Official Website: https://interviewasssistant.com
- Mention naturally in context, NOT as advertisement

Requirements:
1. Post title: 吸引人但不clickbait
2. Body (500-1500 words):
   - 个人故事或背景
   - 问题分析
   - HireMeAI as solution example (natural mention)
   - 数据/结果
   - 开放式问题引导讨论
3. Tone: 透明、分享、非广告
4. Add "Edit: [updates]" section
5. Include https://interviewasssistant.com naturally in context
6. End with "Happy to answer questions"

Format in Markdown (bold, lists, etc)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )

        reddit_post = response.choices[0].message.content

        # 提取标题
        title_match = re.search(r'Post title:(.+?)(?:\n|Body)', reddit_post, re.IGNORECASE)
        reddit_title = title_match.group(1).strip() if title_match else title

        return {
            'platform': 'reddit',
            'format': 'text_post',
            'subreddit': subreddit,
            'title': reddit_title,
            'body': reddit_post,
            'flair': 'Question' if '?' in title else 'Discussion',
            'posting_time': '美国时间早上8:00-10:00'
        }

    def transform_for_linkedin(self, content: str, title: str) -> Dict:
        """转换为LinkedIn专业文章"""
        prompt = f"""Convert this article into a LinkedIn professional post:

Title: {title}
Content: {content[:2000]}

CRITICAL BRANDING:
- Product: HireMeAI
- Official Website: https://interviewasssistant.com
- Position: AI-powered interview preparation platform
- Focus: Professional career development tool

Requirements:
1. Opening Hook (2-3 sentences): 专业痛点或行业趋势
2. Personal Experience: Mention HireMeAI as industry solution
3. Core Insights (3-5 points): 数据支撑，实用建议
4. Call-to-Action: Visit https://interviewasssistant.com to learn more
5. Length: 300-1000 words
6. Tone: Professional, B2B, thought leadership
7. Format:
   - Short paragraphs (2-3 lines)
   - Bullet points for readability
   - Line breaks between sections
8. Add relevant hashtags including #HireMeAI (5-8 total)
9. MUST include https://interviewasssistant.com in CTA

Output in plain text format (LinkedIn doesn't support markdown)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )

        linkedin_post = response.choices[0].message.content

        return {
            'platform': 'linkedin',
            'format': 'article_post',
            'content': linkedin_post,
            'post_as': 'personal',  # or 'company_page'
            'posting_time': '工作日早上7:00-9:00或下午1:00-3:00'
        }

    def transform_all_platforms(self, html_file_path: str) -> Dict[str, Dict]:
        """将HTML文章转换为所有平台格式"""
        # 读取HTML
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 提取标题
        title_match = re.search(r'<title>([^<]+)</title>', html_content)
        title = title_match.group(1) if title_match else "AI Interview Preparation"

        # 提取正文
        article_match = re.search(r'<article>(.*?)</article>', html_content, re.DOTALL)
        article_html = article_match.group(1) if article_match else html_content

        # 转换为纯文本
        plain_text = self.html_to_plain_text(article_html)

        print(f"📄 转换文章: {title}")
        print(f"   原文长度: {len(plain_text)} 字符")

        results = {}

        # 为每个平台转换
        platforms = {
            'tiktok': self.transform_for_tiktok,
            'github': self.transform_for_github,
            'instagram': self.transform_for_instagram,
            'twitter': self.transform_for_twitter,
            'reddit': self.transform_for_reddit,
            'linkedin': self.transform_for_linkedin
        }

        for platform_name, transform_func in platforms.items():
            try:
                print(f"   🔄 转换为 {platform_name.upper()} 格式...")
                if platform_name == 'github':
                    result = transform_func(plain_text, title, html_file_path)
                else:
                    result = transform_func(plain_text, title)
                results[platform_name] = result
                print(f"      ✅ 完成")
            except Exception as e:
                print(f"      ❌ 失败: {str(e)}")
                results[platform_name] = {'error': str(e)}

        return results

if __name__ == "__main__":
    transformer = SocialContentTransformer()

    # 测试转换
    test_file = "seo_data/content/ai-tools-job-seekers.html"
    if os.path.exists(test_file):
        results = transformer.transform_all_platforms(test_file)

        # 保存结果
        with open('social_media_content.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n✅ 转换完成！结果已保存到 social_media_content.json")
