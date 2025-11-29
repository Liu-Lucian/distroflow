#!/usr/bin/env python3
"""
调试Reddit评论抓取 - 截图并分析HTML结构
"""

import json
from playwright.sync_api import sync_playwright
import time

def debug_reddit_post():
    """打开Reddit帖子，截图并分析评论结构"""

    # 使用一个已知有评论的Reddit帖子
    test_url = "https://www.reddit.com/r/jobs/comments/1ob924z/feeling_stuck"

    print("=" * 70)
    print("🔍 Reddit Comment Debug Tool")
    print("=" * 70)

    # 加载认证
    with open('reddit_auth.json', 'r') as f:
        storage_state = json.load(f)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,  # 显示浏览器
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            storage_state=storage_state,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 1200}
        )

        page = context.new_page()

        # 添加反检测
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print(f"\n📱 Opening: {test_url}")
        page.goto(test_url, timeout=30000)

        print("⏳ Waiting 5 seconds for page load...")
        time.sleep(5)

        # 滚动一下加载评论
        print("📜 Scrolling to load comments...")
        for i in range(3):
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(1)

        # 截图
        screenshot_path = "debug_reddit_full_page.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 Full page screenshot saved: {screenshot_path}")

        # 尝试多种评论选择器
        print("\n" + "=" * 70)
        print("🔍 Testing Comment Selectors:")
        print("=" * 70)

        selectors = [
            'div[data-testid^="comment-"]',
            '[id^="t1_"]',
            'shreddit-comment',
            'div.Comment',
            '[class*="comment"]',
        ]

        for selector in selectors:
            elements = page.query_selector_all(selector)
            print(f"\n{selector}:")
            print(f"   Found: {len(elements)} elements")

            if elements and len(elements) > 0:
                # 分析第一个评论元素
                first_elem = elements[0]

                print(f"\n   📋 Analyzing first element:")

                # 尝试获取HTML
                try:
                    html = first_elem.inner_html()
                    print(f"      HTML length: {len(html)} chars")

                    # 保存HTML到文件
                    with open(f'debug_comment_{selector.replace("[", "").replace("]", "").replace("^=", "").replace('"', "")[:20]}.html', 'w') as f:
                        f.write(html)
                    print(f"      ✅ Saved HTML to file")
                except Exception as e:
                    print(f"      ❌ Could not get HTML: {e}")

                # 尝试提取用户名
                print(f"\n   👤 Testing username selectors:")
                username_selectors = [
                    'a[href*="/user/"]',
                    '[href*="/user/"]',
                    'a[data-testid="comment_author_link"]',
                    '[slot="authorName"]',
                    'a[slot="authorName"]',
                ]

                for u_sel in username_selectors:
                    try:
                        u_elem = first_elem.query_selector(u_sel)
                        if u_elem:
                            username = u_elem.inner_text().strip()
                            print(f"      ✅ {u_sel}: '{username}'")
                        else:
                            print(f"      ❌ {u_sel}: Not found")
                    except Exception as e:
                        print(f"      ❌ {u_sel}: Error - {e}")

                # 尝试提取文本
                print(f"\n   📝 Testing text selectors:")
                text_selectors = [
                    '[data-testid="comment"] > div',
                    'div[data-testid*="comment-body"]',
                    'div.md',
                    'p',
                    '[slot="comment"]',
                    'div[slot="comment"]',
                ]

                for t_sel in text_selectors:
                    try:
                        t_elem = first_elem.query_selector(t_sel)
                        if t_elem:
                            text = t_elem.inner_text().strip()
                            preview = text[:80] if text else "(empty)"
                            print(f"      ✅ {t_sel}: '{preview}...'")
                        else:
                            print(f"      ❌ {t_sel}: Not found")
                    except Exception as e:
                        print(f"      ❌ {t_sel}: Error - {e}")

                # 最后：直接获取整个元素的文本
                print(f"\n   📄 Full element text:")
                try:
                    full_text = first_elem.inner_text().strip()
                    print(f"      Length: {len(full_text)} chars")
                    print(f"      Preview: '{full_text[:100]}...'")
                except Exception as e:
                    print(f"      ❌ Error: {e}")

        print("\n" + "=" * 70)
        print("✅ Debug Complete!")
        print("=" * 70)
        print("\nFiles saved:")
        print(f"  - {screenshot_path}")
        print("  - debug_comment_*.html (HTML of first comment for each selector)")
        print("\n⏸️  Browser will stay open for 30 seconds for manual inspection...")

        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    try:
        debug_reddit_post()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
