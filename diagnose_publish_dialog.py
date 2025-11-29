#!/usr/bin/env python3
"""
诊断Substack发布对话框
详细查看所有按钮，找到真正的发布按钮
"""

import sys
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright
from openai import OpenAI
import json
import time
import os

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def diagnose_publish():
    # Load auth
    with open('substack_auth.json', 'r') as f:
        auth_data = json.load(f)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    context.add_cookies(auth_data['cookies'])
    page = context.new_page()

    print("\n" + "="*80)
    print("🔍 Diagnosing Substack Publish Dialog")
    print("="*80)

    try:
        # Navigate to home
        print("\n1. Going to Substack home...")
        page.goto("https://substack.com/home", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Click Create
        print("\n2. Clicking Create button...")
        create_btn = page.wait_for_selector('button:has-text("Create")', timeout=5000)
        create_btn.click()
        time.sleep(2)

        # Click Post from menu
        print("\n3. Clicking Post from menu...")
        post_item = page.wait_for_selector('text="Post"', timeout=5000)
        post_item.click()
        time.sleep(5)

        # Fill in quick content
        print("\n4. Filling minimal content...")
        title_input = page.wait_for_selector('textarea[placeholder*="Title" i]', timeout=5000)
        title_input.fill("Test Publish Diagnosis - DELETE ME")
        time.sleep(1)

        page.keyboard.press('Enter')
        time.sleep(1)
        page.keyboard.type("This is a test to diagnose publishing. Please delete.")
        time.sleep(2)

        # Click Continue button (not Publish)
        print("\n5. Clicking Continue button...")
        continue_selectors = [
            'button:has-text("Continue")',
            'button:has-text("Next")',
            'a:has-text("Continue")'
        ]

        clicked_continue = False
        for selector in continue_selectors:
            try:
                btn = page.wait_for_selector(selector, timeout=2000)
                if btn and btn.is_visible():
                    print(f"   ✅ Found: {selector}")
                    btn.click()
                    clicked_continue = True
                    break
            except:
                pass

        if not clicked_continue:
            print("   ❌ Could not find Continue button")
            page.screenshot(path="diagnose_no_continue.png")
            return

        time.sleep(5)

        page.screenshot(path="diagnose_publish_01_dialog.png")
        print("   📸 Screenshot: diagnose_publish_01_dialog.png")

        # Now analyze the dialog
        print("\n6. Analyzing publish dialog...")
        print("\n   ALL BUTTONS on this page:")
        buttons = page.query_selector_all('button')
        print(f"   Found {len(buttons)} buttons total:\n")

        for i, btn in enumerate(buttons):
            try:
                text = btn.inner_text().strip()
                visible = btn.is_visible()
                enabled = btn.is_enabled()
                btn_type = btn.get_attribute('type') or 'none'
                data_testid = btn.get_attribute('data-testid') or 'none'
                aria_label = btn.get_attribute('aria-label') or 'none'

                if visible:  # Only show visible buttons
                    print(f"   Button {i+1}:")
                    print(f"      Text: '{text}'")
                    print(f"      Type: {btn_type}")
                    print(f"      Enabled: {enabled}")
                    print(f"      data-testid: {data_testid}")
                    print(f"      aria-label: {aria_label}")
                    print()
            except:
                pass

        # Scroll down
        print("\n7. Scrolling down...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)

        page.screenshot(path="diagnose_publish_02_scrolled.png")
        print("   📸 Screenshot: diagnose_publish_02_scrolled.png")

        print("\n   BUTTONS after scrolling:")
        buttons = page.query_selector_all('button')

        for i, btn in enumerate(buttons):
            try:
                text = btn.inner_text().strip()
                visible = btn.is_visible()
                enabled = btn.is_enabled()

                if visible and text:  # Only show visible buttons with text
                    print(f"   Button {i+1}: '{text}' (enabled: {enabled})")
            except:
                pass

        # Check for specific publish-related text
        print("\n8. Looking for publish-related elements...")

        publish_keywords = ['publish', 'send', 'post', 'confirm', 'schedule']
        for keyword in publish_keywords:
            elems = page.query_selector_all(f'text=/{keyword}/i')
            if elems:
                print(f"\n   Elements containing '{keyword}': {len(elems)}")
                for i, elem in enumerate(elems[:5]):  # Show first 5
                    try:
                        text = elem.inner_text()[:100]
                        visible = elem.is_visible()
                        tag = elem.evaluate('el => el.tagName')
                        if visible:
                            print(f"      {i+1}. <{tag}> '{text}' (visible)")
                    except:
                        pass

        print("\n" + "="*80)
        print("📸 Check screenshots:")
        print("   1. diagnose_publish_01_dialog.png - Initial dialog")
        print("   2. diagnose_publish_02_scrolled.png - After scrolling")
        print("="*80)

        input("\n👉 Press Enter to close (browser will stay open for you to inspect)...")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="diagnose_publish_error.png")

    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    if not os.environ.get('OPENAI_API_KEY'):
        print("Setting OPENAI_API_KEY...")
        os.environ['OPENAI_API_KEY'] = 'sk-proj-YOUR_OPENAI_API_KEY_HERE'

    diagnose_publish()
