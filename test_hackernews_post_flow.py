#!/usr/bin/env python3
"""
HN 发帖流程测试脚本
==================

测试完整的发帖流程：
1. 生成内容（Ask HN 或 Show HN）
2. 打开浏览器，登录 HN
3. 填写发帖表单
4. 暂停，等待用户确认
5. 用户可以选择提交或取消

Usage:
    python3 test_hackernews_post_flow.py --type ask    # 测试 Ask HN
    python3 test_hackernews_post_flow.py --type show   # 测试 Show HN
"""

import sys
sys.path.insert(0, 'src')

from hackernews_poster import HackerNewsPoster
import os
import json
import time
from datetime import datetime
from typing import Dict
from anthropic import Anthropic

# ==================== Configuration ====================

PRODUCT_URL = "https://interviewassistant.com"
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'sk-ant-YOUR_ANTHROPIC_API_KEY_HERE')

# ==================== Content Generation ====================

def generate_ask_hn_content() -> Dict:
    """生成 Ask HN 内容"""
    print("📝 生成 Ask HN 内容...")

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a technical founder building an AI interview assistant.

Generate an "Ask HN" post about a real technical challenge you're facing.

REQUIREMENTS:
1. Tone: Casual, curious (use lol, tbh, ngl naturally)
2. Purpose: REAL technical question
3. Share specific metrics/context
4. Ask genuine questions

Example structure:
"I'm building a real-time interview assistant, tbh sub-1s latency is hard.\\n\\nCurrent stack:\\n- GPT-4o\\n- Azure Speech\\n- ChromaDB\\n\\nWe've gotten from 2.7s → 1.0s through caching, but 1s still feels slow.\\n\\nAnyone hit sub-500ms with GPT-4o? Any advice appreciated!"

Output valid JSON (use \\n for line breaks):
{{
  "title": "Ask HN: ...",
  "text": "Body text here..."
}}

CRITICAL: Output ONLY valid JSON. Use \\n for paragraph breaks, not actual newlines."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=600,
        temperature=0.9,
        messages=[{"role": "user", "content": prompt}]
    )

    response = message.content[0].text.strip()

    # Clean markdown fences
    if '```' in response:
        response = response.split('```')[1] if '```json' in response else response.split('```')[1]
        response = response.replace('json', '').strip()

    # Parse JSON
    try:
        post_data = json.loads(response)
    except json.JSONDecodeError:
        # Fix unescaped newlines
        import re
        start = response.find('{')
        end = response.rfind('}') + 1
        json_str = response[start:end]

        def fix_string_value(match):
            key = match.group(1)
            value = match.group(2)
            value = value.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{key}": "{value}"'

        json_str = re.sub(r'"([^"]+)":\s*"([^"]*(?:\n[^"]*)*)"', fix_string_value, json_str, flags=re.MULTILINE)
        post_data = json.loads(json_str)

    return post_data

def generate_show_hn_content() -> Dict:
    """生成 Show HN 内容"""
    print("📝 生成 Show HN 内容...")

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are a technical founder sharing your AI interview assistant on HN.

Generate a "Show HN" post that sounds authentic, not promotional.

REQUIREMENTS:
1. Tone: Casual tech founder (use lol, tbh, ngl naturally)
2. Focus: Share technical challenges, not features
3. Be humble and ask for feedback

Example structure:
"Been working on this for 3 months tbh. An AI interview assistant.\\n\\nHardest part was latency - started at 2.7s, got it to 1s through dual-level caching.\\n\\nStack: GPT-4o, Azure Speech, Picovoice Eagle (95% accuracy).\\n\\nngl still not happy with 1s. Anyone built real-time AI stuff? Advice appreciated!"

Output valid JSON (use \\n for line breaks):
{{
  "title": "Show HN: ...",
  "url": "{PRODUCT_URL}",
  "text": "Body text here..."
}}

CRITICAL: Output ONLY valid JSON. Use \\n for paragraph breaks, not actual newlines."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=800,
        temperature=0.9,
        messages=[{"role": "user", "content": prompt}]
    )

    response = message.content[0].text.strip()

    # Clean markdown fences
    if '```' in response:
        response = response.split('```')[1] if '```json' in response else response.split('```')[1]
        response = response.replace('json', '').strip()

    # Parse JSON
    try:
        post_data = json.loads(response)
    except json.JSONDecodeError:
        # Fix unescaped newlines
        import re
        start = response.find('{')
        end = response.rfind('}') + 1
        json_str = response[start:end]

        def fix_string_value(match):
            key = match.group(1)
            value = match.group(2)
            value = value.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{key}": "{value}"'

        json_str = re.sub(r'"([^"]+)":\s*"([^"]*(?:\n[^"]*)*)"', fix_string_value, json_str, flags=re.MULTILINE)
        post_data = json.loads(json_str)

    return post_data

# ==================== Post Flow Testing ====================

def test_post_flow(post_type: str = 'ask', actually_submit: bool = False):
    """
    测试发帖流程

    Args:
        post_type: 'ask' 或 'show'
        actually_submit: 是否真的提交（默认 False，会暂停让用户确认）
    """

    print("=" * 80)
    print("🧪 HN 发帖流程测试")
    print("=" * 80)
    print(f"类型: {post_type.upper()} HN")
    print(f"自动提交: {'是' if actually_submit else '否（会暂停确认）'}")
    print("=" * 80)
    print()

    # 1. 生成内容
    if post_type == 'ask':
        post_data = generate_ask_hn_content()
    else:
        post_data = generate_show_hn_content()

    print("\n✅ 内容生成成功！")
    print("\n" + "-" * 80)
    print(f"标题: {post_data['title']}")
    print("-" * 80)
    if post_data.get('url'):
        print(f"URL: {post_data['url']}")
        print("-" * 80)
    print("正文:")
    # Convert \n to actual newlines for display
    display_text = post_data['text'].replace('\\n', '\n')
    for line in display_text.split('\n'):
        print(f"  {line}")
    print("-" * 80)
    print()

    # 2. 询问是否继续
    input("按 Enter 继续打开浏览器并填写表单...")

    # 3. 初始化 Poster
    print("\n🌐 初始化浏览器...")
    poster = HackerNewsPoster(auth_file='hackernews_auth.json')

    try:
        # 4. 设置浏览器并加载 cookies
        poster.setup_browser(headless=False)

        # 5. 验证登录
        print("🔐 验证登录状态...")
        if not poster.verify_login():
            print("❌ 登录验证失败！")
            print("   请先运行: python3 hackernews_login_and_save_auth.py")
            poster.close_browser()
            return

        print("✅ 登录成功！")
        time.sleep(2)

        # 6. 导航到提交页面
        print("📄 导航到提交页面...")
        poster.page.goto(f"{poster.base_url}/submit", wait_until="domcontentloaded")
        time.sleep(2)

        # 6. 填写表单
        print("✍️  填写表单...")

        # 填写标题
        title_input = poster.page.query_selector('input[name="title"]')
        if title_input:
            title_input.fill(post_data['title'])
            print(f"  ✓ 标题已填写")
        else:
            print("  ⚠️  找不到标题输入框")

        time.sleep(1)

        # 填写 URL（如果是 Show HN）
        if post_data.get('url'):
            url_input = poster.page.query_selector('input[name="url"]')
            if url_input:
                url_input.fill(post_data['url'])
                print(f"  ✓ URL 已填写")
            else:
                print("  ⚠️  找不到 URL 输入框")
            time.sleep(1)

        # 填写正文
        text_area = poster.page.query_selector('textarea[name="text"]')
        if text_area:
            # Convert \n to actual newlines for submission
            actual_text = post_data['text'].replace('\\n', '\n')
            text_area.fill(actual_text)
            print(f"  ✓ 正文已填写 ({len(actual_text)} 字符)")
        else:
            print("  ⚠️  找不到正文输入框")

        time.sleep(2)

        print("\n✅ 表单填写完成！")
        print("\n" + "=" * 80)
        print("📋 预览（浏览器中可见）")
        print("=" * 80)
        print("现在你可以在浏览器中查看填写的内容")
        print()

        # 7. 提交确认
        if not actually_submit:
            print("⚠️  测试模式：不会自动提交")
            print()
            choice = input("是否要提交这个帖子到 HN？[y/N]: ").strip().lower()

            if choice != 'y':
                print("\n❌ 已取消提交（浏览器保持打开，你可以手动修改/提交）")
                input("\n按 Enter 关闭浏览器...")
                poster.close_browser()
                return

        # 8. 提交
        print("\n🚀 提交帖子...")
        submit_button = poster.page.query_selector('input[type="submit"][value="submit"]')

        if submit_button:
            submit_button.click()
            print("  ✓ 已点击提交按钮")

            # 等待页面跳转
            time.sleep(3)

            # 检查是否成功（URL 会变成 /item?id=xxx）
            if 'item?id=' in poster.page.url:
                post_id = poster.page.url.split('item?id=')[1].split('&')[0]
                print(f"\n🎉 发帖成功！")
                print(f"帖子 ID: {post_id}")
                print(f"帖子链接: {poster.base_url}/item?id={post_id}")
            else:
                print(f"\n⚠️  提交后 URL: {poster.page.url}")
                print("请手动检查是否成功")

            input("\n按 Enter 关闭浏览器...")
        else:
            print("  ❌ 找不到提交按钮")
            input("\n按 Enter 关闭浏览器...")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        poster.close_browser()
        print("\n✅ 浏览器已关闭")

# ==================== Main ====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试 HN 发帖流程")
    parser.add_argument('--type', choices=['ask', 'show'], default='ask',
                        help='帖子类型：ask (Ask HN) 或 show (Show HN)')
    parser.add_argument('--submit', action='store_true',
                        help='自动提交（不暂停确认）')

    args = parser.parse_args()

    test_post_flow(post_type=args.type, actually_submit=args.submit)
