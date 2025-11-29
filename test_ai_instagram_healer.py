#!/usr/bin/env python3
"""
测试AI驱动的Instagram DM自愈系统
当遇到问题时，自动使用GPT-4 Vision分析页面并提供解决方案
"""

import sys
import os
sys.path.append('src')

import json
from playwright.sync_api import sync_playwright
import time
from ai_scraper_healer import AIScraperHealer

print("=" * 60)
print("🤖 AI-Powered Instagram DM Healer Test")
print("=" * 60)

# 检查API key
if not os.getenv('OPENAI_API_KEY'):
    print("❌ OPENAI_API_KEY not found in environment")
    print("   Please set it with:")
    print("   export OPENAI_API_KEY='your-key-here'")
    exit(1)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

test_username = "startupgrind"

# 初始化AI Healer
healer = AIScraperHealer()

with sync_playwright() as p:
    print(f"\n🚀 启动浏览器...")
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 900}
    )

    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/'
    }])

    page = context.new_page()

    # 步骤1: 访问用户profile
    print(f"\n📱 Step 1: 访问 @{test_username} profile...")
    page.goto(f'https://www.instagram.com/{test_username}/', timeout=60000)
    time.sleep(3)

    # 关闭通知弹窗
    try:
        dismiss_button = page.wait_for_selector('button:has-text("以后再说")', timeout=3000)
        if dismiss_button:
            print("   🔕 关闭通知弹窗...")
            dismiss_button.click()
            time.sleep(1)
    except:
        pass

    print(f"   当前URL: {page.url}")

    # 步骤2: 滚动并点击第一个帖子
    print("\n📸 Step 2: 滚动并点击第一个帖子...")
    page.evaluate("window.scrollTo(0, 500)")
    time.sleep(2)

    posts = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    print(f"   找到 {len(posts)} 个帖子")

    if posts:
        first_post = posts[0]
        href = first_post.get_attribute('href')
        print(f"   点击帖子: {href}")
        page.evaluate('(element) => element.click()', first_post)
        time.sleep(4)

        print(f"   点击后URL: {page.url}")

        # 步骤3: 尝试找到Message按钮（可能会失败）
        print("\n💬 Step 3: 尝试找到Message按钮...")

        message_selectors = [
            'div[role="button"]:has-text("消息")',
            'a:has-text("消息")',
            'button:has-text("消息")',
        ]

        message_button = None
        for selector in message_selectors:
            try:
                message_button = page.wait_for_selector(selector, timeout=2000)
                if message_button and message_button.is_visible():
                    print(f"   ✅ 找到: {selector}")
                    break
            except:
                continue

        if message_button:
            print("   点击Message按钮...")
            page.evaluate('(element) => element.click()', message_button)
            time.sleep(5)

            # 步骤4: 尝试找到消息输入框
            print("\n📝 Step 4: 尝试找到消息输入框...")

            input_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="消息"]',
            ]

            message_input = None
            for selector in input_selectors:
                try:
                    message_input = page.wait_for_selector(selector, timeout=2000)
                    if message_input and message_input.is_visible():
                        print(f"   ✅ 找到: {selector}")
                        break
                except:
                    continue

            if not message_input:
                print("   ❌ 常规方法找不到消息输入框")
                print("\n🤖 激活AI Healer...")
                print("   使用GPT-4 Vision分析页面...")

                # 使用AI分析页面
                analysis = healer.analyze_page_with_vision(
                    page=page,
                    task_description="Find the message input box to type a DM. I clicked the Message button but can't find the input field.",
                    current_url=page.url,
                    error_message="Could not find message input with selectors: div[contenteditable=true], textarea, etc."
                )

                print("\n📊 AI Analysis Results:")
                print("=" * 60)
                print(f"Page State: {analysis.get('page_state', 'N/A')}")
                print(f"\nProblem: {analysis.get('problem_analysis', 'N/A')}")
                print(f"\nConfidence: {analysis.get('confidence', 'N/A')}")

                if analysis.get('suggested_selectors'):
                    print(f"\n🎯 AI-Suggested Selectors:")
                    for i, sel in enumerate(analysis['suggested_selectors'], 1):
                        print(f"   {i}. {sel['selector']}")
                        print(f"      Reason: {sel['reason']}")

                print(f"\n💡 Alternative Approach:")
                print(f"   {analysis.get('alternative_approach', 'N/A')}")

                print(f"\n🤖 Recommended Actions:")
                for action in analysis.get('recommended_actions', []):
                    print(f"   - {action}")

                print("=" * 60)

                # 应用AI建议的操作
                print("\n🔧 Applying AI recommendations...")
                healer.apply_human_like_actions(page, analysis)

                # 尝试AI建议的选择器
                print("\n🧪 Trying AI-suggested selectors...")
                success, working_selector = healer.try_selectors_with_ai_guidance(
                    page=page,
                    ai_analysis=analysis,
                    action="fill"
                )

                if success:
                    print(f"\n✅ SUCCESS! Working selector: {working_selector}")
                    message_input = page.query_selector(working_selector)

                    if message_input:
                        print("   🧪 测试输入消息...")
                        message_input.click()
                        time.sleep(0.5)
                        message_input.fill("Test DM from AI-powered automation")
                        print("   ✅ 输入成功！")
                else:
                    print("\n⚠️  AI-suggested selectors didn't work")
                    print("   Trying alternative approach...")

                    # 尝试替代方案
                    alt_success = healer.execute_alternative_approach(page, analysis)

                    if alt_success:
                        print("   ✅ Alternative approach succeeded")
                    else:
                        print("   ❌ Alternative approach also failed")
                        print("   Manual intervention may be needed")

            else:
                print("   ✅ 常规方法成功找到消息输入框")
                print("   (AI Healer未被调用)")

        else:
            print("   ❌ 常规方法找不到Message按钮")
            print("\n🤖 激活AI Healer...")

            # 使用AI分析为什么找不到Message按钮
            analysis = healer.analyze_page_with_vision(
                page=page,
                task_description="Find and click the Message button to start a DM conversation on Instagram",
                current_url=page.url,
                error_message="Could not find Message button with selectors: div[role=button]:has-text(消息), a:has-text(消息), button:has-text(消息)"
            )

            print("\n📊 AI Analysis Results:")
            print("=" * 60)
            print(f"Page State: {analysis.get('page_state', 'N/A')}")
            print(f"\nProblem: {analysis.get('problem_analysis', 'N/A')}")
            print(f"\nAlternative: {analysis.get('alternative_approach', 'N/A')}")
            print("=" * 60)

    else:
        print("   ❌ 没找到帖子")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开60秒供检查...")
    print("=" * 60)

    time.sleep(60)

    browser.close()
    print("\n✅ Test completed")
