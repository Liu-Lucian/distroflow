#!/usr/bin/env python3
"""
从现有 cookies 提取 Product Hunt localStorage 和 sessionStorage
不需要手动登录 - 使用已有的 cookies
"""

from playwright.sync_api import sync_playwright
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AUTH_FILE = "platforms_auth.json"

def extract_storage_from_existing_cookies():
    """
    使用现有 cookies 提取 localStorage 和 sessionStorage
    """
    logger.info("=" * 80)
    logger.info("🔧 Product Hunt Storage 提取工具")
    logger.info("=" * 80)
    logger.info("\n目标: 从现有 cookies 提取 localStorage 和 sessionStorage")
    logger.info("优点: 不需要手动重新登录\n")

    # 1. 加载现有认证数据
    try:
        with open(AUTH_FILE, 'r') as f:
            auth_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ 未找到 {AUTH_FILE}")
        return False

    ph_auth = auth_data.get('producthunt', {})
    if not ph_auth:
        logger.error("❌ 未找到 Product Hunt 认证信息")
        return False

    existing_cookies = ph_auth.get('cookies', [])
    if not existing_cookies:
        logger.error("❌ 未找到现有 cookies")
        logger.info("   请先运行: python3 producthunt_login_enhanced.py")
        return False

    logger.info(f"✅ 找到现有 cookies: {len(existing_cookies)} 个")

    # 2. 使用现有 cookies 打开浏览器
    with sync_playwright() as p:
        logger.info("\n🌐 启动浏览器...")
        browser = p.chromium.launch(
            headless=False,  # 可见模式，方便调试
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )

        # 获取 user_agent
        user_agent = ph_auth.get('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # 创建上下文并加载 cookies
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
        )

        logger.info("📦 加载现有 cookies...")
        context.add_cookies(existing_cookies)

        page = context.new_page()

        # 3. 访问 Product Hunt
        logger.info("🌐 访问 Product Hunt...")
        page.goto("https://www.producthunt.com", timeout=60000)
        time.sleep(5)

        # 截图初始状态
        page.screenshot(path="ph_storage_extract_step1.png")
        logger.info("📸 截图已保存: ph_storage_extract_step1.png")

        # 4. 检查登录状态
        logger.info("\n🔍 检查登录状态...")

        # 方法1: 检查 localStorage
        try:
            local_storage = page.evaluate("() => Object.keys(localStorage)")
            user_keys = [k for k in local_storage if 'user' in k.lower() or 'auth' in k.lower() or 'session' in k.lower()]

            if user_keys:
                logger.info(f"✅ 检测到 localStorage 用户数据: {', '.join(user_keys[:5])}")
                login_verified = True
            else:
                logger.warning("⚠️  localStorage 中未找到用户数据")
                login_verified = False
        except Exception as e:
            logger.error(f"❌ 无法检查 localStorage: {str(e)}")
            login_verified = False

        # 方法2: 检查页面元素
        if not login_verified:
            try:
                page.wait_for_selector('img[alt*="avatar"], img[alt*="profile"], button[data-test*="user"]', timeout=5000)
                logger.info("✅ 检测到用户头像/菜单元素")
                login_verified = True
            except:
                logger.warning("⚠️  未检测到登录指示器")

        if not login_verified:
            logger.error("\n❌ 未检测到登录状态！")
            logger.info("   原因: cookies 可能已过期")
            logger.info("   解决: 运行 python3 producthunt_login_enhanced.py 重新登录")
            page.screenshot(path="ph_storage_extract_not_logged_in.png")
            browser.close()
            return False

        logger.info("✅ 登录状态验证成功！")

        # 5. 提取 localStorage
        logger.info("\n📦 提取 localStorage...")
        try:
            local_storage_data = page.evaluate("""() => {
                let data = {};
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    data[key] = localStorage.getItem(key);
                }
                return data;
            }""")
            logger.info(f"   ✅ localStorage: {len(local_storage_data)} 个键")

            # 显示前几个键
            sample_keys = list(local_storage_data.keys())[:5]
            for key in sample_keys:
                value_preview = str(local_storage_data[key])[:50]
                logger.info(f"      • {key}: {value_preview}...")

        except Exception as e:
            logger.warning(f"   ⚠️  无法提取 localStorage: {str(e)}")
            local_storage_data = {}

        # 6. 提取 sessionStorage
        logger.info("\n📦 提取 sessionStorage...")
        try:
            session_storage_data = page.evaluate("""() => {
                let data = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    let key = sessionStorage.key(i);
                    data[key] = sessionStorage.getItem(key);
                }
                return data;
            }""")
            logger.info(f"   ✅ sessionStorage: {len(session_storage_data)} 个键")
        except Exception as e:
            logger.warning(f"   ⚠️  无法提取 sessionStorage: {str(e)}")
            session_storage_data = {}

        # 截图最终状态
        page.screenshot(path="ph_storage_extract_step2.png")
        logger.info("📸 截图已保存: ph_storage_extract_step2.png")

        # 7. 更新认证文件
        logger.info("\n💾 保存到认证文件...")

        # 更新 Product Hunt 认证信息
        auth_data['producthunt'] = {
            'cookies': existing_cookies,  # 保留原有 cookies
            'localStorage': local_storage_data,
            'sessionStorage': session_storage_data,
            'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_agent': user_agent,
        }

        # 保存
        try:
            with open(AUTH_FILE, 'w') as f:
                json.dump(auth_data, f, indent=2)

            logger.info(f"✅ 已更新 {AUTH_FILE}")
            logger.info(f"\n📊 保存内容:")
            logger.info(f"   • Cookies: {len(existing_cookies)} 个")
            logger.info(f"   • localStorage: {len(local_storage_data)} 个键")
            logger.info(f"   • sessionStorage: {len(session_storage_data)} 个键")
            logger.info(f"   • User Agent: {user_agent[:50]}...")
            logger.info(f"   • 保存时间: {auth_data['producthunt']['saved_at']}")

        except Exception as e:
            logger.error(f"❌ 保存失败: {str(e)}")
            browser.close()
            return False

        # 关闭浏览器
        logger.info("\n🔒 关闭浏览器...")
        browser.close()

        logger.info("\n" + "=" * 80)
        logger.info("✅ 提取成功！")
        logger.info("=" * 80)
        logger.info("\n下一步:")
        logger.info("  python3 test_producthunt_login_final.py  # 测试登录")
        logger.info("  python3 producthunt_account_warmup.py     # 开始养号")

        return True


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt Storage 提取工具                                 ║
╚════════════════════════════════════════════════════════════════╝

目标: 从现有 cookies 提取 localStorage 和 sessionStorage
优点: 不需要手动重新登录

准备开始...
""")

    input("按 Enter 开始提取...")

    success = extract_storage_from_existing_cookies()

    if not success:
        print("\n❌ 提取失败")
        print("\n可能原因:")
        print("  • Cookies 已过期")
        print("  • 网络连接问题")
        print("\n解决方案:")
        print("  python3 producthunt_login_enhanced.py  # 重新登录")
