#!/usr/bin/env python3
"""
Substack 登录并保存认证信息

使用说明：
1. 运行此脚本
2. 在打开的浏览器中手动登录Substack
3. 登录成功后，脚本会自动提取并保存cookies到 substack_auth.json
4. 之后其他脚本可以使用这些cookies自动登录
"""

from playwright.sync_api import sync_playwright
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_and_save_cookies(substack_url: str = None):
    """
    手动登录Substack并保存cookies

    Args:
        substack_url: 你的Substack域名（如 yourname.substack.com），
                     如果为None则使用 substack.com
    """
    logger.info("=" * 80)
    logger.info("🔐 Substack 登录与认证保存工具")
    logger.info("=" * 80)

    home_url = f"https://{substack_url}" if substack_url else "https://substack.com"

    with sync_playwright() as p:
        logger.info("🌐 启动浏览器...")
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        page = context.new_page()

        logger.info(f"📍 访问 {home_url}...")
        page.goto(home_url, wait_until="domcontentloaded", timeout=60000)

        logger.info("\n" + "=" * 80)
        logger.info("👉 请在浏览器中手动登录 Substack")
        logger.info("=" * 80)
        logger.info("\n登录步骤:")
        logger.info("  1. 点击右上角的 'Sign in' 或 'Get started'")
        logger.info("  2. 输入邮箱地址")
        logger.info("  3. 检查邮箱，点击登录链接")
        logger.info("  4. 登录成功后，确认能看到你的Dashboard或个人资料")
        logger.info("\n完成登录后，回到终端按Enter继续...\n")

        input("按Enter继续...")

        # 检查登录状态
        logger.info("\n🔍 验证登录状态...")

        # 检查登录标志
        login_indicators = [
            'button:has-text("New post")',
            'a[href*="/publish"]',
            'a:has-text("Dashboard")',
            '[data-testid="user-menu"]',
            'img[alt*="avatar"]',
            'a:has-text("Settings")'
        ]

        logged_in = False
        for indicator in login_indicators:
            try:
                element = page.wait_for_selector(indicator, timeout=3000)
                if element and element.is_visible():
                    logger.info(f"   ✅ 检测到登录元素: {indicator}")
                    logged_in = True
                    break
            except:
                continue

        if not logged_in:
            logger.warning("   ⚠️  未检测到明确的登录状态，但仍会尝试保存cookies")
            response = input("   是否继续保存cookies？(y/n): ")
            if response.lower() != 'y':
                logger.info("❌ 已取消")
                browser.close()
                return

        # 提取cookies
        logger.info("\n📦 提取cookies...")
        cookies = context.cookies()

        if not cookies:
            logger.error("   ❌ 未找到cookies")
            browser.close()
            return

        logger.info(f"   ✅ 提取到 {len(cookies)} 个cookies")

        # 保存到文件
        auth_data = {
            'cookies': cookies,
            'substack_url': substack_url,
            'saved_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        filename = 'substack_auth.json'
        with open(filename, 'w') as f:
            json.dump(auth_data, f, indent=2)

        logger.info(f"\n✅ 认证信息已保存到: {filename}")
        logger.info("\n" + "=" * 80)
        logger.info("🎉 完成！你现在可以使用以下脚本：")
        logger.info("=" * 80)
        logger.info("  • auto_substack_forever.py - 永久运行发布与回答系统")
        logger.info("  • python3 auto_substack_forever.py --mode generate - 生成并发布单篇文章")
        logger.info("  • python3 auto_substack_forever.py --mode comments - 检查并回复评论")
        logger.info("=" * 80)

        input("\n按Enter关闭浏览器...")
        browser.close()


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 80)
    print("Substack 域名配置")
    print("=" * 80)

    if len(sys.argv) > 1:
        substack_domain = sys.argv[1]
    else:
        print("\n请输入你的Substack域名（例如：yourname.substack.com）")
        print("如果直接按Enter，将使用 substack.com（适用于没有自定义域名的情况）")
        substack_domain = input("\nSubstack域名: ").strip()

    if not substack_domain:
        substack_domain = None
        print("✅ 将使用 substack.com")
    else:
        print(f"✅ 将使用 {substack_domain}")

    print()

    login_and_save_cookies(substack_domain)
