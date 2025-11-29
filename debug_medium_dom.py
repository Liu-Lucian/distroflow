#!/usr/bin/env python3
"""
调试脚本：查看 Medium 写作页面的实际 DOM 结构
"""
import sys
sys.path.insert(0, 'src')

from medium_poster import MediumPoster
import logging
import time

logging.basicConfig(level=logging.INFO)

poster = MediumPoster()

try:
    poster.setup_browser(headless=False)

    print("=" * 80)
    print("访问 Medium 首页...")
    poster.page.goto("https://medium.com/", wait_until="domcontentloaded")
    time.sleep(2)

    print("点击 Write 按钮...")
    write_btn = poster.page.wait_for_selector('a[href*="/new-story"]', timeout=10000)
    write_btn.click()
    print(f"当前 URL: {poster.page.url}")
    time.sleep(5)

    print("=" * 80)
    print("保存页面 HTML 到 medium_dom.html...")
    html = poster.page.content()
    with open('medium_dom.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ HTML 已保存")

    print("=" * 80)
    print("查找所有 h1, h3 和 contenteditable 元素...")

    # 查找所有可能的标题字段
    elements = poster.page.query_selector_all('h1, h3, [contenteditable="true"], [data-slate-editor="true"]')
    print(f"找到 {len(elements)} 个元素")

    for i, elem in enumerate(elements):
        try:
            tag_name = elem.evaluate('el => el.tagName')
            text = elem.text_content()[:50] if elem.text_content() else ""
            attrs = elem.evaluate('el => ({id: el.id, class: el.className, placeholder: el.placeholder, contenteditable: el.contentEditable})')
            print(f"\n元素 {i+1}:")
            print(f"  标签: {tag_name}")
            print(f"  文本: {text}")
            print(f"  属性: {attrs}")
        except Exception as e:
            print(f"  错误: {e}")

    print("=" * 80)
    print("\n等待 60 秒以便手动检查页面...")
    print("请在浏览器中手动检查编辑器状态")
    time.sleep(60)

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    poster.close_browser()
