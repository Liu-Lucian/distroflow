#!/usr/bin/env python3
"""
Reddit DOM结构调试工具
用于查看实际的HTML结构，帮助修复选择器
"""
import sys
sys.path.insert(0, 'src')
from reddit_poster import RedditPoster
import time

poster = RedditPoster()

try:
    print("🌐 启动浏览器...")
    poster.setup_browser(headless=False)

    if not poster.verify_login():
        print("❌ 请先运行 reddit_login_and_save_auth.py 登录")
        exit(1)

    print("✅ 登录成功")
    print("\n" + "="*80)
    print("📊 访问 r/technology 查看DOM结构")
    print("="*80)

    poster.page.goto("https://www.reddit.com/r/technology/hot",
                     wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)  # 等待页面完全加载

    # 尝试不同的post选择器
    print("\n🔍 测试帖子容器选择器...")

    selectors = [
        'shreddit-post',
        'article',
        'div[data-testid="post-container"]',
        'div.Post'
    ]

    for selector in selectors:
        elements = poster.page.query_selector_all(selector)
        print(f"\n   {selector}: 找到 {len(elements)} 个元素")

        if len(elements) > 0:
            print(f"   ✅ 使用这个选择器！")

            # 获取第一个元素的outerHTML
            first_elem = elements[0]

            print(f"\n   📝 第一个元素的结构：")
            print(f"   " + "-"*76)

            # 尝试获取标题
            print(f"\n   🎯 查找标题...")
            title_selectors = [
                'h3',
                '[slot="title"]',
                'a[slot="full-post-link"]',
                'div[slot="title"]'
            ]

            for ts in title_selectors:
                title_elem = first_elem.query_selector(ts)
                if title_elem:
                    title = title_elem.inner_text()
                    print(f"      ✅ {ts}: {title[:60]}...")
                else:
                    print(f"      ❌ {ts}: 未找到")

            # 尝试获取链接
            print(f"\n   🔗 查找链接...")
            link_selectors = [
                'a[href*="/comments/"]',
                'a[slot="full-post-link"]'
            ]

            for ls in link_selectors:
                link_elem = first_elem.query_selector(ls)
                if link_elem:
                    href = link_elem.get_attribute('href')
                    print(f"      ✅ {ls}: {href[:60]}...")
                else:
                    print(f"      ❌ {ls}: 未找到")

            # 尝试获取upvotes
            print(f"\n   👍 查找upvote数...")
            upvote_selectors = [
                'faceplate-number',
                'shreddit-score',
                'div[id*="vote"]'
            ]

            for us in upvote_selectors:
                upvote_elem = first_elem.query_selector(us)
                if upvote_elem:
                    upvotes = upvote_elem.inner_text()
                    print(f"      ✅ {us}: {upvotes}")
                else:
                    print(f"      ❌ {us}: 未找到")

            # 打印完整的outerHTML (前500字符)
            print(f"\n   📄 元素HTML (前500字符):")
            print(f"   " + "-"*76)
            html = first_elem.evaluate('el => el.outerHTML')
            print(f"   {html[:500]}...")

            break

    print("\n" + "="*80)
    print("✅ 调试完成！")
    print("\n💡 根据上面的输出，更新 reddit_karma_farmer.py 中的选择器")
    print("="*80)

    print("\n⏸️  浏览器将保持打开60秒供检查...")
    print("   你可以在浏览器中手动检查元素")
    time.sleep(60)

finally:
    poster.close_browser()
    print("\n✅ 调试工具已关闭")
