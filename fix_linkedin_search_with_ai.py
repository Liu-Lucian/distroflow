#!/usr/bin/env python3
"""
使用AI Vision修复LinkedIn搜索
让AI分析实际的LinkedIn搜索页面并生成正确的抓取代码
"""

import sys
sys.path.append('src')

import os
import json
import time
import base64
from playwright.sync_api import sync_playwright
from openai import OpenAI

print("=" * 70)
print("🤖 LinkedIn Search Fix - AI Vision")
print("=" * 70)

# 检查API Key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not set!")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# 测试搜索
TEST_QUERY = "hiring manager"

print(f"\n📝 测试搜索: {TEST_QUERY}")
print(f"🎯 目标: 让AI分析页面并生成正确的抓取代码\n")

# 启动浏览器
playwright = sync_playwright().start()
browser = playwright.firefox.launch(headless=False, slow_mo=500)

context = browser.new_context(
    storage_state="linkedin_auth.json",
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
)

page = context.new_page()

print("🌐 打开LinkedIn主页...")
page.goto("https://www.linkedin.com/feed/", timeout=60000)
time.sleep(3)

print("🔍 搜索用户...")
try:
    # 找到搜索框
    search_box = page.query_selector('input[placeholder*="Search"]')
    if search_box:
        search_box.click()
        time.sleep(1)
        search_box.fill(TEST_QUERY)
        time.sleep(1)
        search_box.press('Enter')
        time.sleep(3)

        # 尝试点击People标签
        print("📱 尝试点击People标签...")
        people_selectors = [
            'button:has-text("People")',
            '[aria-label="People"]',
            'button:has-text("用户")',
        ]

        for selector in people_selectors:
            try:
                btn = page.wait_for_selector(selector, timeout=3000)
                if btn:
                    btn.click()
                    print(f"   ✅ 点击了: {selector}")
                    time.sleep(4)
                    break
            except:
                continue

except Exception as e:
    print(f"⚠️  搜索过程出错: {e}")

# 等待页面稳定
time.sleep(3)

# 截图
print("\n📸 截图当前页面...")
screenshot_bytes = page.screenshot()
screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

# 保存截图
with open('linkedin_ai_analysis.png', 'wb') as f:
    f.write(screenshot_bytes)

print("🤖 AI分析页面结构...\n")

prompt = f"""这是LinkedIn的人员搜索结果页面（搜索关键词: "{TEST_QUERY}"）。

我需要抓取搜索结果中的所有用户信息。

请分析这个页面并生成Python代码（使用已存在的'page'变量，这是Playwright page对象）来：

1. 检测页面状态:
   - 如果显示错误页面（如"This one's our fault"），点击"Retry search"按钮重试
   - 如果需要点击"People"或"用户"标签，找到并点击它

2. 找到所有用户卡片/结果项

3. 对于每个用户，提取：
   - 姓名（name）
   - 职位/标题（headline）
   - profile链接（profile_url）
   - 地点（location，可选）

4. 创建一个列表 `users`，每个元素是字典：
   {{'name': '...', 'headline': '...', 'profile_url': '...', 'location': '...'}}

5. 打印找到的用户数量和前3个示例

要求：
- 只使用'page'变量（不要创建新的browser或playwright）
- 使用多个备选选择器（LinkedIn经常改DOM结构）
- 健壮的错误处理
- 必须创建变量名为 `users` 的列表

返回可执行的Python代码（不要markdown格式，纯Python代码）。
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
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

    print("\n▶️  执行AI代码...\n")

    # 执行
    exec_globals = {'page': page, 'time': time, 'print': print}
    exec(code, exec_globals)

    # 检查结果
    if 'users' in exec_globals:
        users = exec_globals['users']

        print(f"\n✅ 成功! 找到 {len(users)} 个用户")

        if users:
            print("\n前3个用户:")
            for i, user in enumerate(users[:3], 1):
                print(f"  [{i}] {user.get('name')}")
                print(f"      职位: {user.get('headline', 'N/A')}")
                print(f"      链接: {user.get('profile_url', 'N/A')[:80]}...")

            # 保存代码
            with open('linkedin_search_working_code.py', 'w') as f:
                f.write("# AI-Generated Working LinkedIn Search Code\n")
                f.write("# " + "=" * 68 + "\n\n")
                f.write(code)
                f.write("\n\n# Usage:\n")
                f.write("# This code expects 'page' to be a Playwright page object\n")
                f.write("# with LinkedIn search results already loaded.\n")

            print(f"\n💾 代码已保存到: linkedin_search_working_code.py")
            print("\n🎯 下一步:")
            print("   1. 复制工作的选择器到 src/linkedin_scraper.py")
            print("   2. 更新 search_users() 方法中的选择器")
        else:
            print("\n⚠️  代码执行成功但找到0个用户")
    else:
        print("\n⚠️  代码没有创建'users'变量")

except Exception as e:
    print(f"\n❌ 错误: {{e}}")
    import traceback
    traceback.print_exc()

print("\n⏸  浏览器保持打开30秒...")
time.sleep(30)

browser.close()
playwright.stop()

print("\n✅ 完成")
