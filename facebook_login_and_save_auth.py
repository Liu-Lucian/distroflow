#!/usr/bin/env python3
"""
Facebook登录 - 保存cookies
简单版：手动登录 → 自动保存cookies到platforms_auth.json
"""

import json
import time
from playwright.sync_api import sync_playwright

print("\n" + "="*70)
print("🔐 Facebook登录 & Cookie保存")
print("="*70)

print("\n📝 说明:")
print("1. 浏览器会自动打开Facebook")
print("2. 请手动登录你的Facebook账号")
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

# 访问Facebook
print("\n🌐 正在打开Facebook...")
page.goto('https://www.facebook.com/', timeout=60000)

print("\n⏳ 请在浏览器中登录Facebook...")
print("   登录成功后，此脚本会自动检测")

# 等待登录完成（检测URL变化）
max_wait = 300  # 最多等待5分钟
start_time = time.time()

while time.time() - start_time < max_wait:
    current_url = page.url

    # 检查是否已登录（URL不再是login页面）
    if 'login' not in current_url.lower() and 'facebook.com' in current_url:
        # 尝试查找只有登录后才有的元素
        try:
            # 查找通知按钮或个人资料按钮
            profile_elements = page.query_selector_all('a[aria-label*="Profile"], a[href*="/profile"]')
            if len(profile_elements) > 0:
                print("\n✅ 检测到登录成功!")
                break
        except:
            pass

    time.sleep(2)

if time.time() - start_time >= max_wait:
    print("\n❌ 超时！请重新运行脚本")
    browser.close()
    playwright.stop()
    exit(1)

# 等待一下确保cookies完全加载
time.sleep(3)

# 获取cookies
print("\n📦 正在提取cookies...")
cookies = context.cookies()

# 转换为简单的 name: value 字典
cookies_dict = {}
for cookie in cookies:
    name = cookie['name']
    value = cookie['value']
    cookies_dict[name] = value

print(f"   找到 {len(cookies_dict)} 个cookies")

# 读取现有配置
auth_file = 'platforms_auth.json'

try:
    with open(auth_file, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# 更新Facebook配置
config['facebook'] = {
    'cookies': cookies_dict
}

# 保存
with open(auth_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"\n✅ Cookies已保存到: {auth_file}")
print("\n💡 现在可以运行 run_facebook_campaign.py 了!")

print("\n" + "="*70)
print("✅ 完成!")
print("="*70)

print("\n你可以关闭浏览器窗口了")
input("\n按Enter退出...")

browser.close()
playwright.stop()
