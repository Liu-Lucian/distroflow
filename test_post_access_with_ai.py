#!/usr/bin/env python3
"""
测试帖子访问 - 使用AI Helper截图诊断
"""
import sys
sys.path.append('src')

import json
import time
import random
from playwright.sync_api import sync_playwright

# 导入AI Healer
try:
    from ai_scraper_healer import AIScraperHealer
    AI_HEALER_AVAILABLE = True
    print("✅ AI Healer available")
except:
    AI_HEALER_AVAILABLE = False
    print("⚠️  AI Healer not available")

print("\n🔍 Testing Instagram post access with human-like behavior...\n")

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
sessionid = auth['instagram']['sessionid']

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/'
    }])

    page = context.new_page()

    try:
        # 步骤1: 访问hashtag页面
        hashtag_url = 'https://www.instagram.com/explore/tags/jobsearch/'
        print(f"📱 Visiting hashtag page: {hashtag_url}")
        page.goto(hashtag_url, timeout=30000)
        time.sleep(3)

        # 关闭通知
        try:
            for selector in ['button:has-text("Not Now")', 'button:has-text("以后再说")']:
                try:
                    btn = page.wait_for_selector(selector, timeout=2000)
                    if btn:
                        btn.click()
                        time.sleep(1)
                        break
                except:
                    pass
        except:
            pass

        print("✅ Hashtag page loaded")

        # 步骤2: 收集帖子链接（人类行为）
        print("\n🔍 Collecting post links with human-like behavior...")

        # 人类行为：随机鼠标移动
        try:
            viewport = page.viewport_size
            if viewport:
                print("   → Moving mouse randomly...")
                for _ in range(3):
                    x = random.randint(200, viewport['width'] - 200)
                    y = random.randint(200, viewport['height'] - 200)
                    page.mouse.move(x, y)
                    time.sleep(random.uniform(0.2, 0.5))
        except:
            pass

        # 平滑滚动
        print("   → Scrolling smoothly...")
        try:
            current = page.evaluate('window.pageYOffset')
            target = page.evaluate('document.body.scrollHeight')
            steps = 5
            scroll_each = (target - current) / steps
            for _ in range(steps):
                page.evaluate(f'window.scrollBy(0, {int(scroll_each)})')
                time.sleep(random.uniform(0.4, 0.8))
        except:
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)

        # 收集链接
        links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
        print(f"✅ Found {len(links)} post links")

        if not links:
            print("❌ No post links found!")
            if AI_HEALER_AVAILABLE:
                print("\n🤖 Using AI Helper to analyze the page...")
                healer = AIScraperHealer()
                analysis = healer.analyze_page_with_vision(
                    page=page,
                    task_description="Find Instagram post links on this hashtag page",
                    current_url=page.url,
                    error_message="No post links found with standard selectors"
                )
                print(f"\nAI Analysis:\n{analysis}\n")
            browser.close()
            sys.exit(1)

        # 步骤3: 尝试访问第一个帖子（人类行为）
        first_link = links[0]
        href = first_link.get_attribute('href')
        if not href.startswith('http'):
            href = f'https://www.instagram.com{href}'

        print(f"\n📄 Attempting to access first post: {href}")

        # 方法1: 尝试点击链接（更像人类）
        clicked = False
        try:
            print("   Method 1: Trying to click the link (human-like)...")
            box = first_link.bounding_box()
            if box:
                # 移动鼠标到链接
                center_x = box['x'] + box['width'] / 2
                center_y = box['y'] + box['height'] / 2
                page.mouse.move(center_x, center_y)
                time.sleep(random.uniform(0.5, 1.0))
                print(f"      → Mouse moved to ({int(center_x)}, {int(center_y)})")

                # 点击
                first_link.click()
                clicked = True
                print("      ✓ Clicked!")
                time.sleep(random.uniform(3, 5))
        except Exception as e:
            print(f"      ✗ Click failed: {str(e)[:100]}")

        # 方法2: Fallback到goto
        if not clicked:
            print("   Method 2: Using goto (fallback)...")
            page.goto(href, timeout=30000, wait_until='domcontentloaded')
            time.sleep(random.uniform(3, 5))

        # 人类行为：随机滚动新页面
        print("   → Scrolling new page (simulating reading)...")
        try:
            for _ in range(3):
                scroll = random.randint(-200, 500)
                page.evaluate(f'window.scrollBy(0, {scroll})')
                time.sleep(random.uniform(0.5, 1.2))
        except:
            pass

        # 检查结果
        current_url = page.url
        page_title = page.title()
        page_content_sample = page.content()[:500]

        print(f"\n📊 Result:")
        print(f"   Current URL: {current_url}")
        print(f"   Page title: {page_title}")

        # 检查错误
        if 'HTTP ERROR' in page_content_sample or 'ERR_ABORTED' in page_content_sample:
            print("\n❌ ERROR PAGE DETECTED!")
            print("   Taking screenshot and asking AI...")

            if AI_HEALER_AVAILABLE:
                healer = AIScraperHealer()
                analysis = healer.analyze_page_with_vision(
                    page=page,
                    task_description="Analyze this error page and tell me what went wrong",
                    current_url=current_url,
                    error_message="Post access failed with error page"
                )
                print(f"\n🤖 AI Analysis:\n{analysis}\n")
        else:
            print("   ✅ Post loaded successfully!")

            # 尝试找评论
            print("\n   Looking for comments...")
            comment_elements = page.query_selector_all('span')
            print(f"   Found {len(comment_elements)} span elements")

        print("\n✅ Test complete. Check the browser window.")
        print("Press Enter to close...")
        input()

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        browser.close()
