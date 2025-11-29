#!/usr/bin/env python3
"""
TikTok评论抓取修复工具 - 使用AI Healer自动找到正确选择器
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright
from ai_scraper_healer import AIScraperHealer

print("=" * 70)
print("🔧 TikTok Comment Scraper - AI Healer Fix")
print("=" * 70)

# 测试视频
TEST_VIDEO = "https://www.tiktok.com/@careercoachkate/video/7438726085817994539"

print(f"\n📹 Test video: {TEST_VIDEO}")
print("🤖 AI Healer will analyze and generate correct selectors...\n")

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
    sessionid = auth['tiktok']['sessionid']

healer = AIScraperHealer()

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

    # 访问视频
    print("📱 Loading video...")
    page.goto(TEST_VIDEO, timeout=30000)
    time.sleep(5)

    # 滚动加载评论
    print("📜 Scrolling to load comments...")
    for i in range(5):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(1)

    # 截图
    screenshot_path = "tiktok_comments_for_ai.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"📸 Screenshot saved: {screenshot_path}")

    # AI分析
    print("\n🤖 AI Healer analyzing page structure...")
    print("   (This may take 10-20 seconds...)")

    prompt = """
I need to scrape TikTok video comments. The page is loaded and scrolled.

Analyze the screenshot and generate Python code using the 'page' variable (Playwright) to:

1. Find ALL comment elements on the page
2. For each comment, extract:
   - Username (usually in <a> tag with href="/@username")
   - Comment text (usually in <span> or <p> tag)

Requirements:
- Test multiple CSS selectors until you find working ones
- Return a list of dictionaries: [{'username': '...', 'text': '...'}, ...]
- Skip any elements that don't have both username and text
- Only return comments with text longer than 10 characters

Important:
- TikTok uses dynamic class names, so avoid exact class names
- Use attribute selectors like [data-e2e="..."] when possible
- Try multiple approaches if first one fails

Return executable Python code that prints the number of comments found and shows the first 3 examples.
"""

    try:
        # 使用AI Vision分析页面
        analysis = healer.analyze_page_with_vision(
            screenshot_path=screenshot_path,
            task_description="Extract TikTok video comments with usernames and text",
            additional_context=prompt
        )

        print(f"\n🧠 AI Analysis:\n{analysis}\n")

        # 从分析中提取代码（假设AI会在分析中包含代码）
        # 如果分析中有Python代码块，提取它
        if "```python" in analysis:
            code_start = analysis.find("```python") + 9
            code_end = analysis.find("```", code_start)
            code = analysis[code_start:code_end].strip()
        elif "```" in analysis:
            code_start = analysis.find("```") + 3
            code_end = analysis.find("```", code_start)
            code = analysis[code_start:code_end].strip()
        else:
            code = None
            print("⚠️  AI didn't provide code, showing analysis only")

        if code:
            print("\n💻 AI Generated Code:")
            print("=" * 70)
            print(code)
            print("=" * 70)

            print("\n▶️  Executing AI code...")
            try:
                # 执行AI生成的代码
                exec_globals = {
                    'page': page,
                    'time': time,
                    'print': print
                }
                exec(code, exec_globals)

                # 如果AI代码定义了comments变量，获取它
                if 'comments' in exec_globals:
                    comments = exec_globals['comments']
                    print(f"\n✅ AI successfully extracted {len(comments)} comments!")

                    if comments:
                        print("\n📝 Saving selectors to config...")
                        # 保存成功的选择器
                        with open('tiktok_comment_selectors.txt', 'w') as f:
                            f.write("# TikTok Comment Selectors (AI Generated)\n")
                            f.write("# Date: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
                            f.write("# Copy these selectors to run_tiktok_campaign_optimized.py\n\n")
                            f.write(code)

                        print("✅ Selectors saved to: tiktok_comment_selectors.txt")
                        print("\n🎯 Next steps:")
                        print("   1. Review the AI-generated code above")
                        print("   2. Update run_tiktok_campaign_optimized.py with working selectors")
                        print("   3. Run: ./start_tiktok_campaign.sh")

            except Exception as e:
                print(f"❌ Error executing AI code: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ AI Healer failed to generate code")
            print("   Manual inspection needed")

    except Exception as e:
        print(f"❌ AI Healer error: {e}")
        import traceback
        traceback.print_exc()

    print("\n⏸  Browser will stay open for 30 seconds for manual inspection...")
    time.sleep(30)

    browser.close()

print("\n✅ Done!")
