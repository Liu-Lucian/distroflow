#!/usr/bin/env python3
"""
TikTok DM测试 - 修复用户名URL编码
"""

import sys
sys.path.append('src')

import json
import time
import base64
import os
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from openai import OpenAI

print("=" * 70)
print("🤖 TikTok DM Test - Fixed URL Encoding")
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

print(f"\n👤 原始用户名: {test_user}")

# 清理用户名（移除@和多余空格）
username_clean = test_user.replace('@', '').strip()

# 尝试不同的URL格式
print(f"🔧 清理后: {username_clean}")

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

    # 方法1: 先搜索用户，从搜索结果中点击
    search_query = username_clean.replace(' ', '+')
    search_url = f"https://www.tiktok.com/search/user?q={search_query}"

    print(f"\n📱 方法1: 搜索用户")
    print(f"   URL: {search_url}")
    page.goto(search_url, timeout=30000)
    time.sleep(5)

    # 截图看看搜索结果
    print("\n📸 截图搜索结果...")
    screenshot_bytes = page.screenshot()
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    print("🤖 AI分析搜索结果...\n")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": f"""这是TikTok用户搜索结果页面。我在找用户 "{username_clean}"。

请分析:
1. 是否看到这个用户？
2. 如果看到，用户的profile链接是什么？（通常是/@username格式）
3. 生成Python代码（使用已存在的'page'变量）来点击这个用户的链接

要求：
- 使用CSS选择器（如 a[href*="/@{username_clean.split()[0]}"] ）
- 只使用'page'变量
- 健壮的选择器（try多个）

返回JSON格式:
{{
  "user_found": true/false,
  "profile_url": "/@username",
  "code": "Python code to click user link"
}}
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
            ]
        }],
        max_tokens=1500,
        temperature=0.3
    )

    response_text = response.choices[0].message.content

    # 提取JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    try:
        result = json.loads(response_text)

        print("=" * 70)
        print("🧠 AI分析结果:")
        print("=" * 70)
        print(f"  找到用户: {result.get('user_found')}")
        print(f"  Profile URL: {result.get('profile_url')}")
        print("=" * 70)

        if result.get('user_found') and result.get('code'):
            print("\n▶️  执行AI代码点击用户链接...\n")

            code = result.get('code')
            print(code)
            print()

            exec_globals = {'page': page, 'time': time, 'print': print}
            exec(code, exec_globals)

            time.sleep(3)

            print("\n✅ 已进入用户主页")
            print("💬 现在查找Message按钮...")

            # 截图用户主页
            screenshot_profile = page.screenshot()
            screenshot_profile_base64 = base64.b64encode(screenshot_profile).decode('utf-8')

            print("🤖 AI分析用户主页...\n")

            dm_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """这是TikTok用户主页。

生成Python代码（使用已存在的'page'变量）来:
1. 找到并点击 "Message" 或 "消息" 按钮
2. 等待消息界面加载
3. 找到消息输入框
4. 输入文本: "Hi! I saw your comment on the job search video. Would love to connect!"
5. 找到并点击发送按钮

要求：
- 健壮的多选择器方式
- 只使用'page'变量
- 包含充分的等待时间

返回可执行的Python代码。
"""},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_profile_base64}"}}
                    ]
                }],
                max_tokens=2000,
                temperature=0.3
            )

            dm_code_text = dm_response.choices[0].message.content

            # 提取代码
            if "```python" in dm_code_text:
                code_start = dm_code_text.find("```python") + 9
                code_end = dm_code_text.find("```", code_start)
                dm_code = dm_code_text[code_start:code_end].strip()
            elif "```" in dm_code_text:
                code_start = dm_code_text.find("```") + 3
                code_end = dm_code_text.find("```", code_start)
                dm_code = dm_code_text[code_start:code_end].strip()
            else:
                dm_code = dm_code_text.strip()

            print("=" * 70)
            print("📝 AI生成的DM发送代码:")
            print("=" * 70)
            print(dm_code)
            print("=" * 70)

            print("\n▶️  执行DM发送代码...\n")

            try:
                exec(dm_code, exec_globals)

                print("\n✅ DM代码执行完成!")
                print("\n💾 保存成功的代码...")

                with open('tiktok_dm_working_code.py', 'w') as f:
                    f.write("# AI-Generated Working TikTok DM Code\n")
                    f.write("# " + "=" * 68 + "\n\n")
                    f.write("# Step 1: Click user from search\n")
                    f.write(code + "\n\n")
                    f.write("# Step 2: Send DM\n")
                    f.write(dm_code + "\n")

                print("✅ 代码已保存到: tiktok_dm_working_code.py")

            except Exception as e:
                print(f"\n❌ DM发送出错: {e}")
                import traceback
                traceback.print_exc()

        else:
            print("\n❌ AI未找到用户或无法生成代码")
            print("💡 建议: 手动检查浏览器中的搜索结果")

    except Exception as e:
        print(f"\n❌ 解析AI响应失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n⏸  浏览器保持打开60秒...")
    time.sleep(60)

    browser.close()

print("\n✅ 完成")
