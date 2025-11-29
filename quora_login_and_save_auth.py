#!/usr/bin/env python3
"""
Quora登录 - 保存cookies
简单版：手动登录 → 自动保存cookies到quora_auth.json
"""

import json
import time
from playwright.sync_api import sync_playwright

print("\n" + "="*70)
print("🔐 Quora登录 & Cookie保存")
print("="*70)

print("\n📝 说明:")
print("1. 浏览器会自动打开Quora")
print("2. 请手动登录你的Quora账号")
print("3. 登录成功后，脚本会自动保存cookies")
print("4. 完成后请关闭浏览器窗口")

input("\n按Enter开始...")

# 启动浏览器
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)

context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
)

page = context.new_page()

# 访问Quora
print("\n🌐 正在打开Quora...")
page.goto('https://www.quora.com/', timeout=60000)

print("\n⏳ 请在浏览器中登录Quora...")
print("   登录成功后，此脚本会自动检测")

# 等待登录完成（检测特定元素）
max_wait = 300  # 最多等待5分钟
start_time = time.time()
logged_in = False

while time.time() - start_time < max_wait:
    try:
        # 检查登录后的元素（用户头像、通知图标等）
        login_indicators = [
            'button[aria-label*="profile"]',
            'div[class*="Avatar"]',
            'button[class*="NotificationIcon"]',
            'a[href*="/profile/"]'
        ]

        for selector in login_indicators:
            elem = page.query_selector(selector)
            if elem:
                print(f"\n✅ 检测到登录成功！")
                logged_in = True
                break

        if logged_in:
            break

    except Exception as e:
        pass

    time.sleep(2)

if not logged_in:
    print("\n⚠️  超时：未检测到登录")
    print("   如果你已经登录，可以继续...")
    input("\n如果已登录，按Enter继续...")

# 等待一下确保cookies完整
print("\n⏳ 等待cookies完整加载...")
time.sleep(3)

# 保存cookies
print("\n💾 保存cookies...")
cookies = context.cookies()

# 保存到quora_auth.json
auth_data = {
    'cookies': cookies,
    'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    'note': 'Quora authentication cookies'
}

with open('quora_auth.json', 'w', encoding='utf-8') as f:
    json.dump(auth_data, f, indent=2)

print(f"   ✅ 已保存 {len(cookies)} 个cookies到 quora_auth.json")

# 同时保存到platforms_auth.json（统一管理）
try:
    with open('platforms_auth.json', 'r', encoding='utf-8') as f:
        platforms_auth = json.load(f)
except FileNotFoundError:
    platforms_auth = {}

platforms_auth['quora'] = {
    'cookies': cookies,
    'saved_at': time.strftime('%Y-%m-%d %H:%M:%S')
}

with open('platforms_auth.json', 'w', encoding='utf-8') as f:
    json.dump(platforms_auth, f, indent=2)

print(f"   ✅ 已更新 platforms_auth.json")

print("\n✅ 完成！现在可以运行 auto_quora_forever.py")
print("\n提示：如果将来登录失效，重新运行此脚本即可")

input("\n按Enter关闭浏览器...")
browser.close()
playwright.stop()
