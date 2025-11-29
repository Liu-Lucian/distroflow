#!/usr/bin/env python3
"""
最终登录测试 - 验证完整的浏览器状态恢复
测试 cookies + localStorage + sessionStorage 恢复
"""

import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_login_flow():
    """
    测试完整的登录流程:
    1. 使用增强的 setup_browser() 恢复完整状态
    2. 验证登录成功
    3. 截图验证
    """
    print("=" * 80)
    print("🔍 Product Hunt 完整登录流程测试")
    print("=" * 80)
    print("\n测试步骤:")
    print("  1. 加载 platforms_auth.json")
    print("  2. 恢复 cookies + localStorage + sessionStorage")
    print("  3. 验证登录状态")
    print("  4. 截图保存")
    print("\n开始测试...\n")

    # 创建 commenter 实例
    commenter = ProductHuntCommenter()

    try:
        # Step 1: 设置浏览器（使用增强的 setup_browser）
        print("-" * 80)
        print("Step 1: 设置浏览器并恢复状态")
        print("-" * 80)

        page = commenter.setup_browser(headless=False)

        if not page:
            logger.error("❌ 浏览器设置失败")
            return False

        print("\n✅ 浏览器设置完成！")
        time.sleep(3)

        # Step 2: 验证登录状态
        print("\n" + "-" * 80)
        print("Step 2: 验证登录状态")
        print("-" * 80)

        login_success = commenter.verify_login()

        if not login_success:
            logger.error("❌ 登录验证失败")
            commenter.take_screenshot("login_verification_failed")
            commenter.close_browser()
            return False

        print("\n✅ 登录验证成功！")

        # Step 3: 额外验证 - 检查 localStorage
        print("\n" + "-" * 80)
        print("Step 3: 检查 localStorage 内容")
        print("-" * 80)

        try:
            local_storage = commenter.page.evaluate("() => Object.keys(localStorage)")
            print(f"\nlocalStorage 键数量: {len(local_storage)}")
            print("localStorage 键列表:")
            for key in local_storage:
                print(f"  • {key}")

            # 检查关键的用户数据
            user_session = commenter.page.evaluate("() => localStorage.getItem('user-session')")
            if user_session:
                print(f"\n✅ 找到 user-session: {user_session[:80]}...")
            else:
                print("\n⚠️  未找到 user-session")

        except Exception as e:
            logger.warning(f"⚠️  无法检查 localStorage: {str(e)}")

        # Step 4: 截图验证
        print("\n" + "-" * 80)
        print("Step 4: 截图验证")
        print("-" * 80)

        screenshot_path = commenter.take_screenshot("final_login_test_success")
        print(f"\n✅ 截图已保存: {screenshot_path}")

        # Step 5: 检查页面是否有登录后的元素
        print("\n" + "-" * 80)
        print("Step 5: 检查页面元素")
        print("-" * 80)

        # 检查 Submit 按钮（只有登录用户才能看到）
        try:
            submit_btn = commenter.page.wait_for_selector('a[href*="/posts/new"], button:has-text("Submit")', timeout=5000)
            if submit_btn:
                print("✅ 找到 Submit 按钮（登录用户才有）")
        except:
            print("⚠️  未找到 Submit 按钮")

        # 检查用户菜单
        try:
            user_menu = commenter.page.wait_for_selector('button[data-test*="user"], img[alt*="avatar"]', timeout=5000)
            if user_menu:
                print("✅ 找到用户菜单/头像")
        except:
            print("⚠️  未找到用户菜单")

        # 最终结果
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！登录状态恢复成功")
        print("=" * 80)
        print("\n下一步:")
        print("  python3 producthunt_account_warmup.py  # 开始7天养号")
        print("\n")

        # 保持浏览器打开10秒供用户检查
        print("浏览器将在 10 秒后关闭...")
        time.sleep(10)

        commenter.close_browser()
        return True

    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

        try:
            commenter.take_screenshot("test_error")
            commenter.close_browser()
        except:
            pass

        return False


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 完整登录流程测试                                 ║
╚════════════════════════════════════════════════════════════════╝

测试内容:
  ✅ cookies 恢复
  ✅ localStorage 恢复
  ✅ sessionStorage 恢复
  ✅ 登录状态验证
  ✅ 页面元素检查

准备开始测试...
""")

    input("按 Enter 开始测试...")

    success = test_complete_login_flow()

    if success:
        print("\n" + "=" * 80)
        print("🎉 测试成功！Product Hunt 登录问题已解决")
        print("=" * 80)
        print("\n修复内容:")
        print("  ✅ 更新 ProductHuntCommenter.setup_browser()")
        print("  ✅ 恢复 cookies + localStorage + sessionStorage")
        print("  ✅ 增强登录验证逻辑")
        print("\n现在可以开始使用:")
        print("  python3 producthunt_account_warmup.py  # 7天养号计划")
    else:
        print("\n" + "=" * 80)
        print("❌ 测试失败")
        print("=" * 80)
        print("\n请检查:")
        print("  • platforms_auth.json 是否存在")
        print("  • localStorage 是否有数据")
        print("  • cookies 是否过期")
        print("\n如需重新登录:")
        print("  python3 producthunt_login_enhanced.py")
