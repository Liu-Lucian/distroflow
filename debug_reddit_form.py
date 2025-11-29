#!/usr/bin/env python3
"""
调试Reddit消息表单 - 查看所有输入框和按钮
"""

from playwright.sync_api import sync_playwright
import json
import time

print("🔍 Debugging Reddit message form...")

# 加载认证
with open('reddit_auth.json', 'r') as f:
    storage_state = json.load(f)

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context(
    storage_state=storage_state,
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
)
page = context.new_page()

# 访问compose页面
username = 'Gari_305'
compose_url = f'https://www.reddit.com/message/compose/?to={username}'
print(f'📱 Opening: {compose_url}')
page.goto(compose_url, wait_until='domcontentloaded')

time.sleep(3)

print(f'\n📄 Current URL: {page.url}')
print(f'📄 Page title: {page.title()}')

# 查找所有input
print('\n🔎 All text inputs:')
all_inputs = page.query_selector_all('input[type="text"]')
for i, inp in enumerate(all_inputs):
    try:
        visible = inp.is_visible()
        enabled = inp.is_enabled()
        placeholder = inp.get_attribute('placeholder')
        name = inp.get_attribute('name')
        print(f'  [{i}] visible={visible}, enabled={enabled}, placeholder={placeholder}, name={name}')
    except:
        pass

# 查找所有textarea
print('\n🔎 All textareas:')
all_textareas = page.query_selector_all('textarea')
for i, ta in enumerate(all_textareas):
    try:
        visible = ta.is_visible()
        enabled = ta.is_enabled()
        placeholder = ta.get_attribute('placeholder')
        name = ta.get_attribute('name')
        print(f'  [{i}] visible={visible}, enabled={enabled}, placeholder={placeholder}, name={name}')
    except:
        pass

# 查找所有button
print('\n🔎 All buttons:')
all_buttons = page.query_selector_all('button')
for i, btn in enumerate(all_buttons[:10]):  # 只看前10个
    try:
        visible = btn.is_visible()
        enabled = btn.is_enabled()
        text = btn.text_content()
        btn_type = btn.get_attribute('type')
        print(f'  [{i}] visible={visible}, enabled={enabled}, type={btn_type}, text="{text}"')
    except:
        pass

# 尝试填写表单
print('\n✏️  Trying to fill the form...')

# 填写第一个可见的input
visible_input = None
for inp in all_inputs:
    if inp.is_visible():
        visible_input = inp
        break

if visible_input:
    print('  ✅ Filling subject input...')
    visible_input.fill('Test Subject')
    time.sleep(1)

# 填写第一个可见的textarea
visible_textarea = None
for ta in all_textareas:
    if ta.is_visible():
        visible_textarea = ta
        break

if visible_textarea:
    print('  ✅ Filling message textarea...')
    visible_textarea.fill('This is a test message from HireMeAI.')
    time.sleep(2)

# 检查按钮状态
print('\n🔎 Button states after filling:')
for i, btn in enumerate(all_buttons[:10]):
    try:
        visible = btn.is_visible()
        enabled = btn.is_enabled()
        text = btn.text_content()
        btn_type = btn.get_attribute('type')
        if visible and (btn_type == 'submit' or 'send' in text.lower() or '发送' in text.lower()):
            print(f'  [{i}] SEND BUTTON: visible={visible}, enabled={enabled}, type={btn_type}, text="{text}"')
    except:
        pass

# 等待60秒让你查看
print('\n⏸️  Browser will stay open for 60 seconds...')
print('   Check if the send button is now enabled')
print('   (After filling both subject and message)')
time.sleep(60)

browser.close()
playwright.stop()
