#!/usr/bin/env python3
"""
检查Instagram页面元素 - 帮助找到正确的选择器
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Element Inspector")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

print("✅ Found Instagram sessionid")

with sync_playwright() as p:
    print("\n🚀 Launching browser...")
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 900}
    )

    # 添加sessionid cookie
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/'
    }])

    page = context.new_page()

    # 访问主页
    print("\n📱 Visiting Instagram homepage...")
    page.goto('https://www.instagram.com/', timeout=60000)
    time.sleep(3)

    if 'login' in page.url:
        print("❌ Not logged in")
        browser.close()
        exit(1)

    print("✅ Logged in successfully")
    print(f"Current URL: {page.url}")

    # 检查所有svg元素（图标通常是svg）
    print("\n🔎 Scanning for SVG icons (potential search icon)...")
    svgs = page.query_selector_all('svg')
    print(f"Found {len(svgs)} SVG elements")

    for i, svg in enumerate(svgs[:20]):  # 只看前20个
        try:
            aria_label = svg.get_attribute('aria-label')
            if aria_label:
                print(f"   SVG {i}: aria-label='{aria_label}'")
        except:
            pass

    # 检查所有带有搜索相关文本的元素
    print("\n🔎 Looking for elements with 'Search' text...")
    search_elements = [
        ('svg[aria-label*="Search"]', 'SVG with Search in aria-label'),
        ('svg[aria-label*="搜索"]', 'SVG with 搜索 in aria-label'),
        ('a[href*="explore"]', 'Explore link'),
        ('span:has-text("Search")', 'Span with Search text'),
        ('span:has-text("搜索")', 'Span with 搜索 text'),
        ('input[type="text"]', 'Text input'),
    ]

    for selector, description in search_elements:
        elements = page.query_selector_all(selector)
        count = len(elements)
        print(f"   {description}: {count} found")

        if count > 0:
            elem = elements[0]
            try:
                # 获取父元素
                parent = elem.evaluate('el => el.parentElement.outerHTML')
                print(f"      First match parent HTML (first 200 chars):")
                print(f"      {parent[:200]}")
            except:
                pass

    # 检查nav和侧边栏
    print("\n🔎 Checking navigation elements...")
    nav_selectors = [
        'nav',
        'div[role="navigation"]',
        'aside',
        'div[class*="nav"]',
        'div[class*="sidebar"]',
    ]

    for selector in nav_selectors:
        elements = page.query_selector_all(selector)
        print(f"   {selector}: {len(elements)} found")

    print("\n" + "=" * 60)
    print("⏸️  Browser will stay open for 90 seconds")
    print("   Please inspect the page manually if needed")
    print("=" * 60)

    time.sleep(90)

    browser.close()
    print("\n✅ Done")
