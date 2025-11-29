#!/usr/bin/env python3
"""
使用AI Vision分析TikTok DM界面并生成正确的发送代码
"""

import sys
sys.path.append('src')

import json
import time
import base64
import os
from playwright.sync_api import sync_playwright
from openai import OpenAI

print("=" * 70)
print("🤖 TikTok DM Sender - AI Vision Fix")
print("=" * 70)

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not set!")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
    sessionid = auth['tiktok']['sessionid']

# 加载qualified users
with open('tiktok_qualified_users.json', 'r') as f:
    users = json.load(f)
    if not users:
        print("\n❌ No qualified users found!")
        sys.exit(1)
    test_user = users[0]['username']

print(f"\n👤 测试用户: @{test_user}")
print(f"🎯 使用AI Vision分析DM界面并生成发送代码\n")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=500,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.tiktok.com',
        'path': '/'
    }])

    page = context.new_page()

    # 访问用户主页
    username_clean = test_user.replace('@', '').strip()
    profile_url = f"https://www.tiktok.com/@{username_clean}"

    print(f"📱 访问主页: {profile_url}")
    page.goto(profile_url, timeout=30000)
    time.sleep(3)

    # 点击Message按钮
    print("💬 点击Message按钮...")
    message_selectors = [
        'button:has-text("消息")',
        'button:has-text("Message")',
        'button[data-e2e="message-button"]',
    ]

    message_button = None
    for selector in message_selectors:
        try:
            btn = page.wait_for_selector(selector, timeout=2000)
            if btn:
                message_button = btn
                print(f"   ✅ 找到: {selector}")
                break
        except:
            continue

    if not message_button:
        print("❌ 未找到Message按钮")
        browser.close()
        sys.exit(1)

    message_button.click()
    print("   ✅ 已点击")
    time.sleep(5)  # 等待消息界面加载

    # 截图分析
    print("\n📸 截图DM界面...")
    screenshot_bytes = page.screenshot()
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    print("🤖 AI分析DM界面...\n")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """分析这个TikTok DM（私信）界面。

我需要发送消息，但找不到输入框。

请：
1. 找到消息输入框（可能是 textarea, div[contenteditable], input等）
2. 生成Python代码（使用已存在的'page'变量）来:
   - 找到输入框
   - 输入文本 "Hello, I saw your comment!"
   - 点击发送按钮

要求：
- 使用多个可能的CSS选择器（避免依赖动态class名）
- 代码应该健壮（try多个选择器）
- 只使用'page'变量（不要创建新的browser或playwright实例）

返回可执行的Python代码（不要markdown格式）。
代码应该包含：
```python
# Find input
input_element = None
for selector in [...]:
    try:
        elem = page.wait_for_selector(selector, timeout=2000)
        if elem and elem.is_visible():
            input_element = elem
            break
    except:
        continue

if input_element:
    # Type message
    input_element.fill("Hello, I saw your comment!")
    time.sleep(1)

    # Find and click send button
    send_button = None
    for selector in [...]:
        ...

    if send_button:
        send_button.click()
        print("✅ Message sent!")
```
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
            ]
        }],
        max_tokens=2000,
        temperature=0.3
    )

    response_text = response.choices[0].message.content

    # 提取代码
    if "```python" in response_text:
        code_start = response_text.find("```python") + 9
        code_end = response_text.find("```", code_start)
        code = response_text[code_start:code_end].strip()
    elif "```" in response_text:
        code_start = response_text.find("```") + 3
        code_end = response_text.find("```", code_start)
        code = response_text[code_start:code_end].strip()
    else:
        code = response_text.strip()

    print("=" * 70)
    print("📝 AI生成的代码:")
    print("=" * 70)
    print(code)
    print("=" * 70)

    print("\n▶️  执行代码...\n")

    try:
        # 执行AI生成的代码
        exec_globals = {
            'page': page,
            'time': time,
            'print': print
        }
        exec(code, exec_globals)

        print("\n✅ 代码执行成功!")
        print("\n💾 保存代码到 tiktok_dm_send_code.py...")

        with open('tiktok_dm_send_code.py', 'w') as f:
            f.write("# AI-Generated TikTok DM Sending Code\n")
            f.write("# " + "=" * 68 + "\n\n")
            f.write(code)
            f.write("\n\n# Usage:\n")
            f.write("# This code expects 'page' to be a Playwright page object\n")
            f.write("# with TikTok DM interface already open.\n")

        print("✅ 代码已保存")
        print("\n🎯 下一步:")
        print("   1. 检查浏览器中消息是否发送成功")
        print("   2. 将工作的选择器更新到 tiktok_dm_sender_optimized.py")
        print("   3. 重新运行: ./start_tiktok_campaign.sh")

    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n⏸  浏览器保持打开30秒...")
    time.sleep(30)

    browser.close()

print("\n✅ 完成")
