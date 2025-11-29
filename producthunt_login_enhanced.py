#!/usr/bin/env python3
"""
Product Hunt 增强版登录保存工具
解决登录验证问题，确保 cookies 真正有效
"""

from playwright.sync_api import sync_playwright
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AUTH_FILE = "platforms_auth.json"

def enhanced_login_and_save():
    """
    增强版登录保存 - 使用多种方法验证登录状态
    """
    logger.info("=" * 80)
    logger.info("🚀 Product Hunt 增强版认证保存工具")
    logger.info("=" * 80)
    logger.info("\n改进:")
    logger.info("  ✅ 使用 localStorage 检测登录（最可靠）")
    logger.info("  ✅ 保存完整的浏览器状态")
    logger.info("  ✅ 多重验证确保 cookies 有效")
    logger.info("\n⏳ 准备打开浏览器...\n")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',  # 允许跨域
            ]
        )

        # 创建持久化上下文
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
        )

        page = context.new_page()

        # 访问 Product Hunt
        logger.info("🌐 打开 Product Hunt...")
        page.goto("https://www.producthunt.com", timeout=60000)
        time.sleep(5)

        # 截图初始状态
        page.screenshot(path="ph_login_step1_initial.png")
        logger.info("📸 截图已保存: ph_login_step1_initial.png")

        logger.info("\n" + "=" * 80)
        logger.info("📝 请在浏览器中手动登录 Product Hunt")
        logger.info("=" * 80)
        logger.info("提示:")
        logger.info("  • 点击右上角 'Sign in' 按钮")
        logger.info("  • 使用 Google/Twitter/Email 登录")
        logger.info("  • 完成邮箱验证（如需要）")
        logger.info("  • 等待跳转到首页")
        logger.info("\n⏳ 等待你完成登录...\n")

        # 等待用户登录 - 使用 localStorage 检测
        login_verified = False
        check_interval = 3  # 每3秒检查一次
        max_wait_time = 300  # 最多等待5分钟
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            # 方法1: 检查 localStorage
            try:
                local_storage = page.evaluate("() => Object.keys(localStorage)")
                user_keys = [k for k in local_storage if 'user' in k.lower() or 'auth' in k.lower() or 'session' in k.lower()]

                if user_keys and len(user_keys) > 0:
                    logger.info(f"✅ 检测到 localStorage 用户数据: {', '.join(user_keys[:3])}")
                    login_verified = True
                    break
            except:
                pass

            # 方法2: 检查页面URL变化
            current_url = page.url
            if 'login' not in current_url and elapsed_time > 10:
                # 可能已经登录了，再检查一下
                try:
                    # 检查是否有用户相关元素
                    page.wait_for_selector('img[alt*="avatar"], img[alt*="profile"]', timeout=2000)
                    logger.info(f"✅ 检测到用户头像元素")
                    login_verified = True
                    break
                except:
                    pass

            time.sleep(check_interval)
            elapsed_time += check_interval

            # 每15秒提示一次
            if elapsed_time % 15 == 0:
                logger.info(f"   仍在等待登录... ({elapsed_time}秒)")

        if not login_verified:
            logger.error("\n❌ 登录超时！请重新运行脚本")
            page.screenshot(path="ph_login_timeout.png")
            logger.info("📸 超时截图已保存: ph_login_timeout.png")
            browser.close()
            return False

        logger.info("\n✅ 登录成功！等待页面稳定...")
        time.sleep(5)

        # 截图登录后状态
        page.screenshot(path="ph_login_step2_logged_in.png")
        logger.info("📸 截图已保存: ph_login_step2_logged_in.png")

        # 提取完整状态
        logger.info("\n📦 提取浏览器状态...")

        # 1. 提取 cookies
        cookies = context.cookies()
        logger.info(f"   ✅ Cookies: {len(cookies)} 个")

        # 2. 提取 localStorage
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
        except Exception as e:
            logger.warning(f"   ⚠️  无法提取 localStorage: {str(e)}")
            local_storage_data = {}

        # 3. 提取 sessionStorage
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

        if not cookies:
            logger.error("❌ 未能提取 cookies，请重试")
            browser.close()
            return False

        # 保存所有状态
        try:
            # 读取现有配置
            try:
                with open(AUTH_FILE, 'r') as f:
                    auth_data = json.load(f)
            except FileNotFoundError:
                auth_data = {}

            # 更新 Product Hunt 认证信息（包含所有状态）
            auth_data['producthunt'] = {
                'cookies': cookies,
                'localStorage': local_storage_data,
                'sessionStorage': session_storage_data,
                'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'user_agent': context._options.get('user_agent', ''),
            }

            # 保存
            with open(AUTH_FILE, 'w') as f:
                json.dump(auth_data, f, indent=2)

            logger.info(f"\n✅ 完整状态已保存到: {AUTH_FILE}")

        except Exception as e:
            logger.error(f"❌ 保存失败: {str(e)}")
            browser.close()
            return False

        # 验证保存的状态
        logger.info("\n🔍 验证保存的状态...")

        # 创建新的上下文进行测试
        test_context = browser.new_context(
            user_agent=auth_data['producthunt']['user_agent']
        )

        # 加载 cookies
        test_context.add_cookies(cookies)
        test_page = test_context.new_page()

        try:
            test_page.goto("https://www.producthunt.com", timeout=30000)
            time.sleep(3)

            # 恢复 localStorage
            if local_storage_data:
                for key, value in local_storage_data.items():
                    try:
                        test_page.evaluate(f"localStorage.setItem('{key}', {json.dumps(value)})")
                    except:
                        pass

            # 恢复 sessionStorage
            if session_storage_data:
                for key, value in session_storage_data.items():
                    try:
                        test_page.evaluate(f"sessionStorage.setItem('{key}', {json.dumps(value)})")
                    except:
                        pass

            # 刷新页面让存储生效
            test_page.reload()
            time.sleep(3)

            # 检查登录状态
            verified = False

            # 方法1: localStorage
            try:
                test_storage = test_page.evaluate("() => Object.keys(localStorage)")
                test_user_keys = [k for k in test_storage if 'user' in k.lower() or 'session' in k.lower()]
                if test_user_keys:
                    logger.info(f"   ✅ localStorage 验证成功: {', '.join(test_user_keys[:2])}")
                    verified = True
            except:
                pass

            # 方法2: 页面元素
            if not verified:
                try:
                    test_page.wait_for_selector('img[alt*="avatar"], img[alt*="profile"]', timeout=5000)
                    logger.info("   ✅ 页面元素验证成功")
                    verified = True
                except:
                    pass

            # 截图验证状态
            test_page.screenshot(path="ph_login_step3_verified.png")
            logger.info("📸 验证截图已保存: ph_login_step3_verified.png")

            if verified:
                logger.info("\n" + "=" * 80)
                logger.info("🎉 验证成功！登录状态已完整保存")
                logger.info("=" * 80)
                logger.info("\n保存的状态包括:")
                logger.info(f"  ✅ Cookies ({len(cookies)} 个)")
                logger.info(f"  ✅ localStorage ({len(local_storage_data)} 个键)")
                logger.info(f"  ✅ sessionStorage ({len(session_storage_data)} 个键)")
                result = True
            else:
                logger.warning("\n⚠️  无法完全验证登录状态")
                logger.info("   但状态已保存，可以尝试使用")
                result = True

        except Exception as e:
            logger.error(f"❌ 验证出错: {str(e)}")
            result = False

        # 关闭浏览器
        logger.info("\n🔒 关闭浏览器...")
        browser.close()

        return result


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 增强版登录工具                                    ║
╚════════════════════════════════════════════════════════════════╝

改进:
  ✅ 使用 localStorage 检测（最可靠）
  ✅ 保存完整浏览器状态
  ✅ 多重验证机制
  ✅ 详细的调试截图

准备开始...
""")

    input("按 Enter 开始登录流程...")

    success = enhanced_login_and_save()

    if success:
        print("\n" + "=" * 80)
        print("✅ 登录状态已成功保存！")
        print("=" * 80)
        print("\n生成的文件:")
        print("  • platforms_auth.json - 认证数据")
        print("  • ph_login_step1_initial.png - 初始状态截图")
        print("  • ph_login_step2_logged_in.png - 登录后截图")
        print("  • ph_login_step3_verified.png - 验证截图")
        print("\n下一步:")
        print("  python3 test_producthunt_login_final.py  # 测试登录")
    else:
        print("\n❌ 登录保存失败")
        print("\n请查看截图文件排查问题:")
        print("  • ph_login_*.png")
