#!/usr/bin/env python3
"""
Product Hunt 登录状态诊断工具
帮助排查登录验证问题
"""

import sys
sys.path.insert(0, 'src')
from producthunt_commenter import ProductHuntCommenter
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_login():
    """诊断 Product Hunt 登录状态"""

    logger.info("=" * 80)
    logger.info("🔍 Product Hunt 登录状态诊断工具")
    logger.info("=" * 80)

    # 1. 检查 cookies 文件
    logger.info("\n📦 检查 1/4: 检查 cookies 文件...")
    try:
        with open('platforms_auth.json', 'r') as f:
            auth_data = json.load(f)

        if 'producthunt' in auth_data:
            cookies = auth_data['producthunt'].get('cookies', [])
            logger.info(f"   ✅ 找到 Product Hunt cookies ({len(cookies)} 个)")
            logger.info(f"   保存时间: {auth_data['producthunt'].get('saved_at', 'Unknown')}")
        else:
            logger.error("   ❌ 未找到 Product Hunt 认证信息")
            logger.info("   请运行: python3 producthunt_login_and_save_auth.py")
            return False

    except FileNotFoundError:
        logger.error("   ❌ 未找到 platforms_auth.json 文件")
        logger.info("   请运行: python3 producthunt_login_and_save_auth.py")
        return False
    except Exception as e:
        logger.error(f"   ❌ 读取认证文件失败: {str(e)}")
        return False

    # 2. 启动浏览器
    logger.info("\n🌐 检查 2/4: 启动浏览器并加载 cookies...")
    commenter = ProductHuntCommenter()
    commenter.setup_browser(headless=False)

    logger.info("   ✅ 浏览器启动成功")
    logger.info("   ✅ Cookies 已加载")

    # 3. 访问 Product Hunt 首页
    logger.info("\n🏠 检查 3/4: 访问 Product Hunt 首页...")
    try:
        commenter.page.goto("https://www.producthunt.com", timeout=30000)
        time.sleep(3)
        logger.info("   ✅ 首页加载成功")

        # 截图
        commenter.take_screenshot("diagnose_homepage")
        logger.info("   📸 截图已保存: diagnose_homepage_*.png")

    except Exception as e:
        logger.error(f"   ❌ 访问首页失败: {str(e)}")
        commenter.close_browser()
        return False

    # 4. 检测登录状态 - 使用多种方法
    logger.info("\n🔐 检查 4/4: 检测登录状态...")

    # 方法1: 检查原有的选择器
    logger.info("   方法 1: 检查常见登录指示器...")
    login_indicators = [
        'a[href*="/posts/new"]',  # Submit 按钮
        'button[data-test="user-menu"]',  # 用户菜单
        'div[data-test="header-user-menu"]',  # 用户头像
        'a[href*="/settings"]',  # Settings 链接
        'button:has-text("Submit")',  # Submit 按钮（文本）
        '[data-test*="user"]',  # 任何包含 user 的元素
    ]

    found_indicators = []
    for selector in login_indicators:
        try:
            element = commenter.page.wait_for_selector(selector, timeout=2000)
            if element and element.is_visible():
                found_indicators.append(selector)
                logger.info(f"      ✅ 找到: {selector}")
        except:
            pass

    # 方法2: 检查是否有登录/注册按钮（未登录才有）
    logger.info("\n   方法 2: 检查未登录指示器...")
    not_logged_in_indicators = [
        'button:has-text("Sign in")',
        'button:has-text("Log in")',
        'a:has-text("Sign in")',
        'a:has-text("Log in")',
    ]

    found_logout_indicators = []
    for selector in not_logged_in_indicators:
        try:
            element = commenter.page.wait_for_selector(selector, timeout=2000)
            if element and element.is_visible():
                found_logout_indicators.append(selector)
                logger.warning(f"      ⚠️  找到未登录指示器: {selector}")
        except:
            pass

    # 方法3: 检查 localStorage
    logger.info("\n   方法 3: 检查浏览器存储...")
    try:
        # 获取 localStorage 数据
        local_storage = commenter.page.evaluate("() => Object.keys(localStorage)")
        if local_storage:
            logger.info(f"      ✅ localStorage 包含 {len(local_storage)} 个键")
            # 检查是否有用户相关的数据
            user_keys = [k for k in local_storage if 'user' in k.lower() or 'auth' in k.lower()]
            if user_keys:
                logger.info(f"      ✅ 找到用户相关数据: {', '.join(user_keys[:3])}")
    except Exception as e:
        logger.warning(f"      ⚠️  无法检查 localStorage: {str(e)}")

    # 生成诊断报告
    logger.info("\n" + "=" * 80)
    logger.info("📊 诊断报告")
    logger.info("=" * 80)

    print("\n✅ Cookies 检查:")
    print(f"   文件存在: ✅")
    print(f"   Product Hunt cookies: ✅ ({len(cookies)} 个)")

    print("\n🔍 登录状态检测:")
    print(f"   找到登录指示器: {len(found_indicators)} 个")
    if found_indicators:
        for indicator in found_indicators:
            print(f"      ✅ {indicator}")

    print(f"\n   找到未登录指示器: {len(found_logout_indicators)} 个")
    if found_logout_indicators:
        for indicator in found_logout_indicators:
            print(f"      ⚠️  {indicator}")

    # 判断登录状态
    print("\n" + "=" * 80)
    if len(found_indicators) > 0 and len(found_logout_indicators) == 0:
        logger.info("✅ 判断: 已登录！")
        logger.info("\n建议: 登录验证选择器可能需要更新")
        logger.info("      我会自动修复 producthunt_commenter.py 中的验证逻辑")
        status = "logged_in"
    elif len(found_logout_indicators) > 0:
        logger.error("❌ 判断: 未登录")
        logger.info("\n建议: Cookies 可能已过期，请重新登录")
        logger.info("      运行: python3 producthunt_login_and_save_auth.py")
        status = "not_logged_in"
    else:
        logger.warning("⚠️  判断: 无法确定登录状态")
        logger.info("\n建议: Product Hunt 页面可能发生变化")
        logger.info("      请查看截图 diagnose_homepage_*.png")
        status = "unknown"

    # 保持浏览器打开
    logger.info("\n" + "=" * 80)
    logger.info("🔍 浏览器将保持打开状态，请手动检查:")
    logger.info("=" * 80)
    logger.info("  1. 页面右上角是否有你的头像？")
    logger.info("  2. 是否能看到 'Submit' 按钮？")
    logger.info("  3. 点击头像是否有下拉菜单？")
    logger.info("\n检查完成后按 Enter 关闭浏览器...")
    input()

    commenter.close_browser()

    return status


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 登录状态诊断工具                                 ║
╚════════════════════════════════════════════════════════════════╝

此工具将帮助你诊断 Product Hunt 登录验证问题：

检查项目：
  1. ✅ 检查 platforms_auth.json 文件
  2. ✅ 检查 Product Hunt cookies
  3. ✅ 访问 Product Hunt 首页
  4. ✅ 使用多种方法检测登录状态
  5. ✅ 生成诊断报告

准备开始诊断...
""")

    input("按 Enter 开始...")

    status = diagnose_login()

    print("\n" + "=" * 80)
    if status == "logged_in":
        print("✅ 诊断完成！你已经登录 Product Hunt")
        print("\n下一步: 我会修复登录验证逻辑，请稍等...")
    elif status == "not_logged_in":
        print("❌ 诊断完成！Cookies 已过期")
        print("\n下一步: 运行 python3 producthunt_login_and_save_auth.py")
    else:
        print("⚠️  诊断完成，但无法确定登录状态")
        print("\n下一步: 检查截图文件 diagnose_homepage_*.png")
    print("=" * 80)
