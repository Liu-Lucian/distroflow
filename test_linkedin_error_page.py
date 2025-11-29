#!/usr/bin/env python3
"""
测试LinkedIn错误页面检测和重试逻辑
"""

import sys
sys.path.append('src')

from playwright.sync_api import sync_playwright
import time

print("=" * 70)
print("🧪 Testing LinkedIn Error Page Detection")
print("=" * 70)

playwright = sync_playwright().start()
browser = playwright.firefox.launch(headless=False)

context = browser.new_context(
    storage_state="linkedin_auth.json",
    viewport={'width': 1920, 'height': 1080}
)

page = context.new_page()

print("\n🔍 Opening LinkedIn search page...")
page.goto("https://www.linkedin.com/feed/", timeout=60000)
time.sleep(2)

# Search
search_box = page.query_selector('input[placeholder*="Search"]')
if search_box:
    search_box.click()
    time.sleep(1)
    search_box.fill("hiring manager")
    time.sleep(1)
    search_box.press('Enter')
    time.sleep(3)

    # Click People tab
    people_btn = page.query_selector('button:has-text("People")')
    if people_btn:
        people_btn.click()
        time.sleep(3)

print("\n🔍 Checking for error page...")
max_retries = 3
for retry in range(max_retries):
    # Get page text
    try:
        page_text = page.inner_text('body')
        print(f"\n   Attempt {retry + 1}/{max_retries}")
        print(f"   Page text length: {len(page_text)}")

        # Check for error
        if "This one's our fault" in page_text or "We're looking into it" in page_text:
            print(f"   ⚠️  ERROR PAGE DETECTED!")

            # Try clicking Retry button
            retry_button = page.query_selector('button:has-text("Retry search")')
            if retry_button:
                print(f"   ✅ Found 'Retry search' button")
                print(f"   🔄 Clicking button...")
                retry_button.click()
                time.sleep(5)

                # Check again
                continue
            else:
                print(f"   ❌ Could not find 'Retry search' button")
                print(f"   🔄 Refreshing page...")
                page.reload()
                time.sleep(5)
                continue
        else:
            print(f"   ✅ No error page detected")
            print(f"   First 200 chars of page: {page_text[:200]}")
            break

    except Exception as e:
        print(f"   ❌ Error: {e}")
        break

# Take final screenshot
print("\n📸 Taking final screenshot...")
page.screenshot(path='linkedin_error_test.png')

print("\n⏸  Keeping browser open for 20 seconds...")
time.sleep(20)

browser.close()
playwright.stop()

print("\n✅ Test complete")
