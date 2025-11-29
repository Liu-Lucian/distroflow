#!/usr/bin/env python3
"""
修复SEO内容 - 重新生成高质量HTML文件
修复问题：
1. Markdown格式问题
2. HireMeAI品牌关联
3. HTML结构
"""

import json
import os
import re

def clean_markdown(content):
    """清理Markdown内容"""
    # 移除code block markers
    content = re.sub(r'```markdown\n?', '', content)
    content = re.sub(r'```\n?', '', content)
    content = content.strip()
    return content

def markdown_to_html(markdown_text):
    """改进的Markdown到HTML转换"""
    html = markdown_text

    # 标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # 段落（处理多行）
    paragraphs = html.split('\n\n')
    processed_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<'):
            # 不是HTML标签，包装成段落
            para = f'<p>{para}</p>'
        processed_paragraphs.append(para)
    html = '\n'.join(processed_paragraphs)

    # 列表
    html = re.sub(r'^\s*[-*]\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # 将连续的<li>包装在<ul>中
    html = re.sub(r'(<li>.*?</li>(?:\n<li>.*?</li>)*)', r'<ul>\n\1\n</ul>', html, flags=re.DOTALL)

    # 加粗
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # 斜体
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # 链接
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    return html

def add_hiremeai_branding(content):
    """在内容中添加HireMeAI品牌元素"""
    # 在文章开头添加品牌介绍
    intro_cta = """
<div class="brand-intro" style="background: #f0f8ff; padding: 20px; margin: 20px 0; border-left: 4px solid #0066cc;">
    <p><strong>🚀 Try HireMeAI (即答侠)</strong> - Our AI-powered interview assistance platform helps you practice interview questions with real-time feedback, personalized Q&A templates, and voice-assisted coaching. <a href="https://interviewasssistant.com" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">Start Your Free Trial →</a></p>
</div>
"""

    # 在结尾添加CTA
    footer_cta = """
<div class="cta-section" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; margin: 30px 0; border-radius: 8px; text-align: center;">
    <h3 style="color: white; margin-top: 0;">Ready to Ace Your Next Interview?</h3>
    <p style="font-size: 18px; margin: 20px 0;">Join thousands of job seekers who've improved their interview skills with <strong>HireMeAI (即答侠)</strong></p>
    <ul style="list-style: none; padding: 0; margin: 20px 0; text-align: left; max-width: 500px; margin: 20px auto;">
        <li style="margin: 10px 0;">✅ AI-powered interview practice with 95%+ accuracy</li>
        <li style="margin: 10px 0;">✅ Real-time voice assistance and feedback</li>
        <li style="margin: 10px 0;">✅ Personalized Q&A templates with STAR framework</li>
        <li style="margin: 10px 0;">✅ Resume optimization with ATS scoring</li>
    </ul>
    <a href="https://interviewasssistant.com" target="_blank" style="display: inline-block; background: white; color: #667eea; padding: 15px 40px; margin-top: 20px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 18px;">Get Started Free →</a>
    <p style="margin-top: 15px; font-size: 14px; opacity: 0.9;">No credit card required | 80% performance improvement</p>
</div>
"""

    # 在第一个</h1>后插入intro
    content = re.sub(r'(</h1>)', r'\1' + intro_cta, content, count=1)

    # 在文章结尾添加CTA
    if '</article>' in content:
        content = content.replace('</article>', footer_cta + '\n</article>')
    else:
        content += footer_cta

    # 在正文中自然插入品牌提及
    content = content.replace('AI-powered tools', '<a href="https://interviewasssistant.com" style="color: #0066cc; text-decoration: none;">AI-powered tools like HireMeAI</a>')
    content = content.replace('interview preparation platform', '<a href="https://interviewasssistant.com" style="color: #0066cc; text-decoration: none;">interview preparation platforms like HireMeAI (即答侠)</a>')

    return content

def regenerate_html_files():
    """重新生成所有HTML文件"""
    print("🔧 修复SEO内容...")

    # 读取已发布内容
    with open('seo_data/published_content.json', 'r') as f:
        published_content = json.load(f)

    for i, item in enumerate(published_content, 1):
        title = item['topic']['title']
        slug = item['url_slug']
        print(f"\n[{i}/{len(published_content)}] 重新生成: {title}")

        # 清理content
        content = item['content']
        content = clean_markdown(content)

        # 转换为HTML
        html_content = markdown_to_html(content)

        # 添加品牌元素
        html_content = add_hiremeai_branding(html_content)

        # 获取metadata
        metadata = item['metadata']
        schema = item['schema']

        # 生成完整HTML
        full_html = f"""<!DOCTYPE html>
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
    <meta property="og:url" content="https://interviewasssistant.com/{slug}">
    <meta property="og:image" content="https://interviewasssistant.com/images/hiremeai-og.jpg">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{metadata.get('title_tags', [title])[0]}">
    <meta name="twitter:description" content="{metadata.get('meta_descriptions', [''])[0]}">

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
{json.dumps(schema, indent=2)}
    </script>

    <!-- Styles -->
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f9f9f9;
        }}
        article {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 20px;
            line-height: 1.2;
        }}
        h2 {{
            color: #34495e;
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h3 {{
            color: #546479;
            font-size: 1.3em;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        p {{
            margin: 15px 0;
            font-size: 1.05em;
        }}
        ul, ol {{
            margin: 20px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 10px 0;
        }}
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            border-bottom: 1px solid #3498db;
        }}
        a:hover {{
            color: #2980b9;
            border-bottom-color: #2980b9;
        }}
        .brand-intro {{
            animation: fadeIn 1s ease-in;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <article>
{html_content}
    </article>

    <!-- HireMeAI Branding Footer -->
    <footer style="text-align: center; padding: 40px 20px; color: #666;">
        <p>Powered by <a href="https://interviewasssistant.com" style="color: #667eea; font-weight: bold;">HireMeAI (即答侠)</a></p>
        <p style="font-size: 14px;">AI-Powered Interview Preparation Platform | 95%+ Accuracy | Real-Time Assistance</p>
        <p style="font-size: 12px;">Contact: liu.lucian6@gmail.com | +1 (424) 439-1736</p>
    </footer>
</body>
</html>"""

        # 保存文件
        filepath = f"seo_data/content/{slug}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)

        print(f"   ✅ 已保存: {filepath}")

    print("\n🎉 所有HTML文件已成功重新生成！")
    print(f"✅ 修复了{len(published_content)}个文件")
    print("\n📊 改进内容：")
    print("   ✅ 移除了Markdown代码块标记")
    print("   ✅ 修复了HTML结构")
    print("   ✅ 添加了HireMeAI品牌元素")
    print("   ✅ 插入了指向 https://interviewasssistant.com 的CTA")
    print("   ✅ 添加了专业CSS样式")
    print("   ✅ 优化了Schema.org标记")

if __name__ == "__main__":
    os.chdir("/Users/l.u.c/my-app/MarketingMind AI")
    regenerate_html_files()
