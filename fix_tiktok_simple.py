#!/usr/bin/env python3
"""
TikTok评论抓取修复 - 简单直接版本
使用AI Vision直接生成评论抓取代码
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
print("🔧 TikTok Comment Scraper Fix - Simple Version")
print("=" * 70)

# 检查API Key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not set!")
    print("Run: export OPENAI_API_KEY='your-key'")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# 测试视频
TEST_VIDEO = "https://www.tiktok.com/@careercoachkate/video/7438726085817994539"

print(f"\n📹 Test video: {TEST_VIDEO}")
print("🤖 AI will analyze the page and generate scraping code...\n")

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
    sessionid = auth['tiktok']['sessionid']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
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

    # 访问视频并加载评论
    print("📱 Loading video page...")
    page.goto(TEST_VIDEO, timeout=30000)
    time.sleep(5)

    print("📜 Scrolling to load comments...")
    for i in range(5):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(1)

    # 截图
    print("📸 Taking screenshot...")
    screenshot_bytes = page.screenshot(full_page=True)
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    # AI分析
    print("\n🤖 Sending to AI for analysis...")
    print("   (This may take 15-30 seconds...)\n")

    prompt = """I need to scrape comments from this TikTok video page.

CRITICAL: A Playwright 'page' object is ALREADY LOADED with the TikTok video page.
DO NOT create a new browser or page. Use the existing 'page' variable.

Write Python code that:

1. Uses the EXISTING 'page' variable (Playwright page already on TikTok video)
2. Finds ALL comment elements on the page
3. For each comment, extracts:
   - Username (look for links with href="/@...")
   - Comment text (look for text content in spans or paragraphs)
4. Creates a list called 'comments' with dictionaries: [{'username': 'user1', 'text': 'comment text'}, ...]
5. Prints the count and first 3 examples

Requirements:
- DO NOT use 'with sync_playwright()' or create any browser/page objects
- ONLY use the 'page' variable that already exists
- Try multiple CSS selectors if needed
- Skip comments that don't have both username and text
- Only include comments with text longer than 10 characters
- MUST create a variable called 'comments' with the results

Important for finding selectors:
- TikTok uses dynamic class names, so avoid hardcoded class names
- Try data-e2e attributes first like [data-e2e="comment-item"]
- Look for container elements that hold each comment
- The username is usually in an <a> tag with href="/@username"
- The comment text is usually in a <span> or <p> tag

Example structure:
```python
comments = []
comment_elements = page.query_selector_all('YOUR_SELECTOR_HERE')
for elem in comment_elements:
    username = ... # extract username
    text = ... # extract text
    if username and text and len(text) > 10:
        comments.append({'username': username, 'text': text})

print(f"Found {len(comments)} comments")
print("First 3:", comments[:3])
```

Return ONLY executable Python code (no markdown, no explanations).
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
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
                }
            ],
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

        print("✅ AI generated code!")
        print("\n" + "=" * 70)
        print("📝 Generated Code:")
        print("=" * 70)
        print(code)
        print("=" * 70)

        print("\n▶️  Executing code...\n")

        # 执行AI生成的代码
        exec_globals = {'page': page, 'print': print}
        exec(code, exec_globals)

        # 保存代码
        if 'comments' in exec_globals:
            comments = exec_globals['comments']

            if comments:
                print(f"\n✅ SUCCESS! Found {len(comments)} comments")

                # 保存代码到文件
                with open('tiktok_comment_code.py', 'w') as f:
                    f.write("# AI-Generated TikTok Comment Scraper\n")
                    f.write("# " + "=" * 68 + "\n\n")
                    f.write(code)
                    f.write("\n\n# Usage:\n")
                    f.write("# This code expects 'page' to be a Playwright page object\n")
                    f.write("# with a TikTok video already loaded.\n")

                print("\n📁 Code saved to: tiktok_comment_code.py")
                print("\n🎯 Next steps:")
                print("   1. Review the code above")
                print("   2. Copy the working selectors to run_tiktok_campaign_optimized.py")
                print("   3. Run: ./start_tiktok_campaign.sh")
            else:
                print("\n⚠️  Code executed but found 0 comments")
                print("   The selectors might need adjustment")
        else:
            print("\n⚠️  Code executed but didn't create 'comments' variable")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n⏸  Browser staying open for 10 seconds...")
    time.sleep(10)

    browser.close()

print("\n✅ Done!")
