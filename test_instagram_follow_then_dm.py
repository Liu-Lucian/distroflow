#!/usr/bin/env python3
"""
Instagram智能营销 - Follow后自动DM
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright
from ai_scraper_healer import AIScraperHealer

print("=" * 70)
print("🤖 Instagram Follow + DM Test")
print("=" * 70)

# 初始化AI Healer
healer = AIScraperHealer()

# 测试用户
TEST_USER = "uciantrepreneur"

TEST_MESSAGE = """Hey, I saw your comment about entrepreneurship — really insightful!

I'm building HireMeAI (https://interviewasssistant.com), an AI-powered interview prep platform.

Would love to get your thoughts if you're open to it!"""

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)

        # 加载Instagram cookies
        with open('platforms_auth.json', 'r') as f:
            auth = json.load(f)
            sessionid = auth['instagram']['sessionid']

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        context.add_cookies([{
            'name': 'sessionid',
            'value': sessionid,
            'domain': '.instagram.com',
            'path': '/'
        }])

        page = context.new_page()

        print(f"\n🎯 Target: @{TEST_USER}")
        print()

        # 步骤1: 访问用户profile
        print("📱 Step 1: Going to user profile...")
        page.goto(f'https://www.instagram.com/{TEST_USER}/', timeout=30000)
        time.sleep(3)

        print(f"   Current URL: {page.url}")

        # 步骤2: 查找Follow按钮
        print("\n👥 Step 2: Looking for Follow button...")

        follow_selectors = [
            'button:has-text("Follow")',
            'button:has-text("关注")',
            'div[role="button"]:has-text("Follow")',
            'div[role="button"]:has-text("关注")',
        ]

        followed = False
        for selector in follow_selectors:
            try:
                follow_btn = page.wait_for_selector(selector, timeout=3000)
                if follow_btn and follow_btn.is_visible():
                    print(f"   ✅ Found Follow button: {selector}")
                    page.evaluate('(el) => el.click()', follow_btn)
                    print("   ✅ Clicked Follow")
                    time.sleep(2)
                    followed = True
                    break
            except:
                continue

        if not followed:
            print("   ℹ️  Already following or Follow button not found")

        # 步骤3: 查找Message按钮
        print("\n💬 Step 3: Looking for Message button...")

        message_selectors = [
            'button:has-text("Message")',
            'button:has-text("发消息")',  # 正确的中文！
            'button:has-text("消息")',
            'div[role="button"]:has-text("Message")',
            'div[role="button"]:has-text("发消息")',
            'div[role="button"]:has-text("消息")',
        ]

        message_btn_found = False
        for selector in message_selectors:
            try:
                message_btn = page.wait_for_selector(selector, timeout=3000)
                if message_btn and message_btn.is_visible():
                    print(f"   ✅ Found Message button: {selector}")
                    page.evaluate('(el) => el.click()', message_btn)
                    print("   ✅ Clicked Message")
                    time.sleep(3)
                    message_btn_found = True
                    break
            except:
                continue

        if not message_btn_found:
            print("   ⚠️  Message button not found")
            print("\n🤖 Asking AI how to proceed...")

            # 让AI分析页面
            analysis = healer.analyze_page_with_vision(
                page=page,
                task_description=f"I want to send a DM to user {TEST_USER}. I'm on their profile page. How do I open the message interface?",
                current_url=page.url,
                error_message="Could not find Message button"
            )

            print(f"\n📊 AI Analysis:")
            print(f"   Problem: {analysis.get('problem_analysis', '')[:200]}...")
            print(f"   Confidence: {analysis.get('confidence', 0)}")
            print(f"\n💡 AI Alternative Approach:")
            print(f"   {analysis.get('alternative_approach', '')[:300]}...")

            # 尝试AI建议的选择器
            print(f"\n🧪 Trying AI-suggested selectors...")
            success, selector = healer.try_selectors_with_ai_guidance(
                page=page,
                ai_analysis=analysis,
                action="click"
            )

            if success:
                print(f"   ✅ AI found working selector: {selector}")
                time.sleep(3)
            else:
                print("   ❌ AI suggestions didn't work")
                print("\n   Let me try direct /direct/new/ approach...")
                page.goto('https://www.instagram.com/direct/new/', timeout=30000)
                time.sleep(2)

                # 搜索用户
                search_input = page.wait_for_selector('input[placeholder*="Search"], input[placeholder*="搜索"]', timeout=5000)
                if search_input:
                    search_input.fill(TEST_USER)
                    time.sleep(2)

                    # 点击结果
                    results = page.query_selector_all('div[role="button"]')
                    if results:
                        page.evaluate('(el) => el.click()', results[0])
                        time.sleep(2)

                        # 点击Chat
                        try:
                            chat_btn = page.wait_for_selector('button:has-text("Chat"), button:has-text("聊天")', timeout=3000)
                            if chat_btn:
                                page.evaluate('(el) => el.click()', chat_btn)
                                time.sleep(3)
                        except:
                            pass

        # 步骤4: 查找消息输入框
        print("\n✏️  Step 4: Looking for message input...")

        current_url = page.url
        print(f"   Current URL: {current_url}")

        input_selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="消息"]',
        ]

        message_input = None
        for selector in input_selectors:
            try:
                message_input = page.wait_for_selector(selector, timeout=5000)
                if message_input and message_input.is_visible():
                    print(f"   ✅ Found input: {selector}")
                    break
            except:
                continue

        if not message_input:
            print("   ⚠️  Input not found, asking AI...")

            # 再次让AI分析
            analysis = healer.analyze_page_with_vision(
                page=page,
                task_description=f"I need to find the message input box to type a DM to {TEST_USER}",
                current_url=page.url,
                error_message="Could not find message input after clicking Message button"
            )

            print(f"\n📊 AI Analysis:")
            print(f"   Problem: {analysis.get('problem_analysis', '')[:200]}...")
            print(f"   Alternative: {analysis.get('alternative_approach', '')[:200]}...")

            # 尝试AI建议
            success, selector = healer.try_selectors_with_ai_guidance(
                page=page,
                ai_analysis=analysis,
                action="fill"
            )

            if success:
                message_input = page.wait_for_selector(selector, timeout=3000)

        if message_input:
            # 输入消息
            print("\n📝 Step 5: Typing message...")
            message_input.fill(TEST_MESSAGE)
            print("   ✅ Message typed")
            time.sleep(1)

            # 发送
            print("\n📤 Step 6: Sending...")

            # 尝试多种Send按钮选择器
            send_selectors = [
                'button:has-text("Send")',
                'button:has-text("发送")',
                'div[role="button"]:has-text("Send")',
                'div[role="button"]:has-text("发送")',
                'button[type="button"]',  # 通用按钮
            ]

            sent = False
            for selector in send_selectors:
                try:
                    send_btns = page.query_selector_all(selector)
                    for btn in send_btns:
                        if btn.is_visible() and not btn.is_disabled():
                            print(f"   ✅ Found Send button: {selector}")
                            page.evaluate('(el) => el.click()', btn)
                            print("   ✅ Sent!")
                            time.sleep(2)
                            sent = True
                            break
                    if sent:
                        break
                except:
                    continue

            if sent:
                print("\n" + "=" * 70)
                print("✅ SUCCESS - Message sent!")
                print("=" * 70)
            else:
                print("   ⚠️  Send button not found, trying Enter key...")
                # 尝试按Enter键发送
                try:
                    message_input.press('Enter')
                    print("   ✅ Pressed Enter to send")
                    time.sleep(2)

                    print("\n" + "=" * 70)
                    print("✅ SUCCESS - Message sent via Enter!")
                    print("=" * 70)
                except:
                    print("   ❌ Enter key didn't work either")
        else:
            print("\n❌ Could not find message input even with AI help")

        print("\n⏸️  Browser will stay open for 10 seconds...")
        time.sleep(10)

        browser.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed")
