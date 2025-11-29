#!/usr/bin/env python3
"""
Product Hunt 登录并保存认证信息
手动登录后自动提取并保存 cookies
"""

from playwright.sync_api import sync_playwright
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AUTH_FILE = "platforms_auth.json"

def login_and_save():
    """
    打开 Product Hunt 登录页面，手动登录后保存 cookies
    """
    logger.info("=" * 80)
    logger.info("🚀 Product Hunt 认证保存工具")
    logger.info("=" * 80)
    logger.info("\n步骤:")
    logger.info("  1. 浏览器将自动打开 Product Hunt 登录页面")
    logger.info("  2. 请手动完成登录（可能需要邮箱验证码）")
    logger.info("  3. 登录成功后，等待页面跳转到首页")
    logger.info("  4. 脚本会自动检测登录状态并保存 cookies")
    logger.info("\n⏳ 准备打开浏览器...\n")

    with sync_playwright() as p:
        # 启动浏览器（非无头模式）
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        # 访问 Product Hunt
        logger.info("🌐 打开 Product Hunt...")
        page.goto("https://www.producthunt.com", timeout=30000)
        time.sleep(3)

        logger.info("\n" + "=" * 80)
        logger.info("📝 请在浏览器中手动登录 Product Hunt")
        logger.info("=" * 80)
        logger.info("提示:")
        logger.info("  • Product Hunt 支持邮箱登录或 Google/Twitter 登录")
        logger.info("  • 登录后会收到邮箱验证码（如果使用邮箱登录）")
        logger.info("  • 登录成功后，你会看到首页的产品列表")
        logger.info("\n⏳ 等待你完成登录...\n")

        # 等待用户登录
        login_verified = False
        check_interval = 5  # 每5秒检查一次
        max_wait_time = 300  # 最多等待5分钟
        elapsed_time = 0

        # 登录状态检测选择器
        login_indicators = [
            'a[href*="/posts/new"]',  # Submit 按钮
            'button[data-test="user-menu"]',  # 用户菜单
            'div[data-test="header-user-menu"]',  # 用户头像
            'a[href*="/settings"]',  # Settings 链接
        ]

        while elapsed_time < max_wait_time:
            # 检查是否有登录状态指示器
            for selector in login_indicators:
                try:
                    element = page.wait_for_selector(selector, timeout=1000)
                    if element and element.is_visible():
                        logger.info(f"✅ 检测到登录状态: {selector}")
                        login_verified = True
                        break
                except:
                    continue

            if login_verified:
                break

            time.sleep(check_interval)
            elapsed_time += check_interval

            # 每30秒提示一次
            if elapsed_time % 30 == 0:
                logger.info(f"   仍在等待登录... ({elapsed_time}秒)")

        if not login_verified:
            logger.error("\n❌ 登录超时！请重新运行脚本")
            browser.close()
            return False

        logger.info("\n✅ 登录成功！正在提取认证信息...\n")
        time.sleep(2)

        # 提取 cookies
        cookies = context.cookies()

        if not cookies:
            logger.error("❌ 未能提取 cookies，请重试")
            browser.close()
            return False

        logger.info(f"📦 提取到 {len(cookies)} 个 cookies")

        # 保存到 platforms_auth.json
        try:
            # 读取现有配置（如果存在）
            try:
                with open(AUTH_FILE, 'r') as f:
                    auth_data = json.load(f)
            except FileNotFoundError:
                auth_data = {}

            # 更新 Product Hunt 认证信息
            auth_data['producthunt'] = {
                'cookies': cookies,
                'saved_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # 保存
            with open(AUTH_FILE, 'w') as f:
                json.dump(auth_data, f, indent=2)

            logger.info(f"✅ 认证信息已保存到: {AUTH_FILE}")

        except Exception as e:
            logger.error(f"❌ 保存失败: {str(e)}")
            browser.close()
            return False

        # 验证保存的 cookies
        logger.info("\n🔍 验证保存的 cookies...")

        # 创建新的上下文测试
        test_context = browser.new_context()
        test_context.add_cookies(cookies)
        test_page = test_context.new_page()

        try:
            test_page.goto("https://www.producthunt.com", timeout=30000)
            time.sleep(3)

            # 检查登录状态
            verified = False
            for selector in login_indicators:
                try:
                    element = test_page.wait_for_selector(selector, timeout=3000)
                    if element and element.is_visible():
                        verified = True
                        break
                except:
                    continue

            if verified:
                logger.info("   ✅ Cookies 验证成功！")
                logger.info("\n" + "=" * 80)
                logger.info("🎉 完成！你现在可以使用 auto_producthunt_forever.py 了")
                logger.info("=" * 80)
                result = True
            else:
                logger.warning("   ⚠️  Cookies 验证失败，但已保存，请尝试运行自动脚本")
                result = True

        except Exception as e:
            logger.error(f"   ❌ 验证出错: {str(e)}")
            result = False

        # 关闭浏览器
        logger.info("\n🔒 关闭浏览器...")
        browser.close()

        return result


def check_existing_auth():
    """检查现有的认证信息"""
    try:
        with open(AUTH_FILE, 'r') as f:
            auth_data = json.load(f)

        if 'producthunt' in auth_data:
            saved_at = auth_data['producthunt'].get('saved_at', 'Unknown')
            num_cookies = len(auth_data['producthunt'].get('cookies', []))
            logger.info(f"ℹ️  发现已有认证信息:")
            logger.info(f"   保存时间: {saved_at}")
            logger.info(f"   Cookies 数量: {num_cookies}")
            return True
        else:
            logger.info("ℹ️  未找到 Product Hunt 认证信息")
            return False

    except FileNotFoundError:
        logger.info("ℹ️  认证文件不存在")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Product Hunt 认证保存工具")
    print("=" * 80)

    # 检查现有认证
    has_existing = check_existing_auth()

    if has_existing:
        print("\n⚠️  已存在 Product Hunt 认证信息")
        response = input("是否要重新登录并覆盖？(y/N): ")
        if response.lower() != 'y':
            print("\n✅ 保持现有认证，退出")
            exit(0)

    print("\n开始登录流程...")
    success = login_and_save()

    if success:
        print("\n" + "=" * 80)
        print("✅ 设置完成！")
        print("=" * 80)
        print("\n下一步:")
        print("  1. 设置 OpenAI API Key:")
        print("     export OPENAI_API_KEY='sk-proj-...'")
        print("\n  2. 修改 auto_producthunt_forever.py 中的产品列表")
        print("\n  3. 运行自动评论系统:")
        print("     python3 auto_producthunt_forever.py")
        print("\n")
    else:
        print("\n❌ 设置失败，请重试")
        exit(1)
