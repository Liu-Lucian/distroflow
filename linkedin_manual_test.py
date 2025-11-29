#!/usr/bin/env python3
"""
LinkedIn手动测试 - 让浏览器保持打开，用户手动操作
然后脚本尝试提取数据
"""

import sys
sys.path.append('src')

from playwright.sync_api import sync_playwright
import time

print("=" * 70)
print("💼 LinkedIn Manual Test - YOU control the browser")
print("=" * 70)

print("""
📝 Instructions:
1. The script will open LinkedIn in Firefox
2. You manually navigate and search for users
3. When you see the search results, press Enter in this terminal
4. The script will try to extract the users
""")

input("\nPress Enter to start...")

playwright = sync_playwright().start()
browser = playwright.firefox.launch(headless=False, slow_mo=500)

context = browser.new_context(
    storage_state="linkedin_auth.json",
    viewport={'width': 1920, 'height': 1080}
)

page = context.new_page()

print("\n🌐 Opening LinkedIn...")
page.goto("https://www.linkedin.com/feed/", timeout=60000)

print("\n" + "=" * 70)
print("✋ YOUR TURN!")
print("=" * 70)
print("""
Please do the following:
1. Use the search box to search for "hiring manager"
2. Click on the "People" tab
3. Wait until you see user results
4. Then press Enter in this terminal

The browser will stay open. Take your time!
""")

input("Press Enter when you're ready for the script to extract users...")

print("\n🔍 Attempting to extract users from current page...")

# Try multiple selectors
user_cards_selectors = [
    'li.reusable-search__result-container',
    '.search-results-container li',
    '[data-chameleon-result-urn]',
    'ul.reusable-search__entity-result-list > li'
]

found_users = []

for selector in user_cards_selectors:
    user_cards = page.query_selector_all(selector)
    print(f"   Selector '{selector}': {len(user_cards)} elements")

    if user_cards:
        print(f"   ✅ Using this selector!")

        for card in user_cards[:5]:  # Just first 5 for testing
            try:
                # Try to extract name
                name_elem = card.query_selector('.entity-result__title-text a')
                if not name_elem:
                    name_elem = card.query_selector('a.app-aware-link')
                if not name_elem:
                    name_elem = card.query_selector('.entity-result__title-line a')

                if name_elem:
                    name = name_elem.inner_text().strip()
                    profile_url = name_elem.get_attribute('href')

                    # Clean URL
                    if profile_url and '?' in profile_url:
                        profile_url = profile_url.split('?')[0]

                    # Extract headline
                    headline_elem = card.query_selector('.entity-result__primary-subtitle')
                    headline = headline_elem.inner_text().strip() if headline_elem else 'N/A'

                    found_users.append({
                        'name': name,
                        'profile_url': profile_url,
                        'headline': headline
                    })

            except Exception as e:
                print(f"      Error extracting card: {e}")
                continue

        break  # Found working selector

print("\n" + "=" * 70)
print(f"📊 Results: Found {len(found_users)} users")
print("=" * 70)

if found_users:
    for i, user in enumerate(found_users, 1):
        print(f"\n[{i}] {user['name']}")
        print(f"    职位: {user['headline']}")
        print(f"    链接: {user['profile_url'][:80]}...")

    print("\n✅ SUCCESS! The selectors work when LinkedIn shows results.")
    print("💡 The issue is LinkedIn's anti-bot protection triggering the error page.")
    print("\n🎯 Solutions:")
    print("   1. Add longer delays between actions (already done)")
    print("   2. Wait a few minutes between searches (rate limiting)")
    print("   3. Use the search less frequently")
    print("   4. Consider using LinkedIn Sales Navigator API")
else:
    print("\n⚠️  No users found")
    print("💡 Possible reasons:")
    print("   1. Not on the search results page")
    print("   2. Still on error page")
    print("   3. DOM selectors changed")

# Take screenshot
print("\n📸 Taking screenshot...")
page.screenshot(path='linkedin_manual_test.png')

print("\n⏸  Browser will stay open for 30 seconds...")
time.sleep(30)

browser.close()
playwright.stop()

print("\n✅ Test complete")
