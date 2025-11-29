#!/usr/bin/env python3
"""
检查 Product Hunt 产品页面结构
找到正确的评论框和点赞按钮选择器
"""

import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_product_page():
    """
    检查产品页面，找到正确的选择器
    """
    logger.info("=" * 80)
    logger.info("🔍 检查 Product Hunt 产品页面结构")
    logger.info("=" * 80)

    # 加载今日产品
    try:
        with open('todays_producthunt_products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', [])
    except FileNotFoundError:
        logger.error("❌ 未找到 todays_producthunt_products.json")
        return

    if not products:
        logger.error("❌ 产品列表为空")
        return

    # 使用第一个产品测试
    test_product = products[0]
    logger.info(f"\n测试产品: {test_product['name']}")
    logger.info(f"URL: {test_product['url']}")

    commenter = ProductHuntCommenter()

    try:
        # 设置浏览器
        logger.info("\n🌐 设置浏览器...")
        commenter.setup_browser(headless=False)

        if not commenter.verify_login():
            logger.error("❌ 登录失败")
            return

        logger.info("✅ 登录成功")

        # 访问产品页面
        logger.info(f"\n🌐 访问产品页面...")
        commenter.page.goto(test_product['url'], timeout=60000)
        time.sleep(5)

        # 截图
        commenter.take_screenshot("product_page_inspection")

        logger.info("\n" + "=" * 80)
        logger.info("📋 页面检查任务")
        logger.info("=" * 80)
        logger.info("\n浏览器将保持打开，请检查以下元素:")
        logger.info("\n1. 点赞按钮 (Upvote):")
        logger.info("   • 右键点击 Upvote 按钮")
        logger.info("   • 选择 'Inspect' / '检查元素'")
        logger.info("   • 记录元素的:")
        logger.info("     - data-test 属性")
        logger.info("     - class 属性")
        logger.info("     - 父元素结构")

        logger.info("\n2. 评论输入框:")
        logger.info("   • 滚动到页面底部评论区")
        logger.info("   • 右键点击评论输入框")
        logger.info("   • 选择 'Inspect'")
        logger.info("   • 记录:")
        logger.info("     - 是 textarea 还是 contenteditable div?")
        logger.info("     - placeholder 文本")
        logger.info("     - data-test, class, name 属性")

        logger.info("\n3. 提交评论按钮:")
        logger.info("   • 右键点击 Post/Submit 按钮")
        logger.info("   • 记录 data-test, class 属性")

        logger.info("\n" + "=" * 80)
        logger.info("⏳ 浏览器将保持打开 120 秒...")
        logger.info("=" * 80)
        logger.info("\n检查完成后，记录以下信息:")
        logger.info("  1. Upvote 按钮选择器")
        logger.info("  2. 评论输入框选择器")
        logger.info("  3. 提交按钮选择器")

        # 等待用户检查
        time.sleep(120)

        # 尝试自动检测选择器
        logger.info("\n" + "=" * 80)
        logger.info("🔍 自动检测选择器...")
        logger.info("=" * 80)

        # 检测点赞按钮
        logger.info("\n1. 检测点赞按钮:")
        upvote_selectors = [
            'button[data-test*="upvote"]',
            'button[data-test*="vote"]',
            'button:has-text("Upvote")',
            'button[class*="upvote"]',
            'button[class*="vote"]',
            'div[data-test*="upvote"] button',
            '[data-test="vote-button"]',
            '[data-test="upvote-button"]',
        ]

        found_upvote = False
        for selector in upvote_selectors:
            try:
                elem = commenter.page.query_selector(selector)
                if elem:
                    logger.info(f"   ✅ 找到: {selector}")
                    found_upvote = True
                    break
            except:
                pass

        if not found_upvote:
            logger.warning("   ⚠️  未找到点赞按钮")

        # 检测评论框
        logger.info("\n2. 检测评论输入框:")
        comment_selectors = [
            'textarea[placeholder*="comment"]',
            'textarea[placeholder*="Comment"]',
            'textarea[name="comment"]',
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea[class*="comment"]',
            'textarea[data-test*="comment"]',
            '[data-test="comment-input"]',
            '[data-test="comment-textarea"]',
        ]

        found_comment = False
        for selector in comment_selectors:
            try:
                elem = commenter.page.query_selector(selector)
                if elem and elem.is_visible():
                    logger.info(f"   ✅ 找到: {selector}")
                    found_comment = True
                    break
            except:
                pass

        if not found_comment:
            logger.warning("   ⚠️  未找到评论输入框")

        # 检测提交按钮
        logger.info("\n3. 检测提交按钮:")
        submit_selectors = [
            'button[type="submit"]',
            'button:has-text("Post")',
            'button:has-text("Comment")',
            'button:has-text("Submit")',
            'button[class*="submit"]',
            'button[class*="post"]',
            'button[data-test*="submit"]',
            'button[data-test*="post"]',
        ]

        found_submit = False
        for selector in submit_selectors:
            try:
                elem = commenter.page.query_selector(selector)
                if elem:
                    logger.info(f"   ✅ 找到: {selector}")
                    found_submit = True
                    break
            except:
                pass

        if not found_submit:
            logger.warning("   ⚠️  未找到提交按钮")

        logger.info("\n" + "=" * 80)
        logger.info("📸 截图已保存供后续分析")
        logger.info("=" * 80)

        # 关闭浏览器
        commenter.close_browser()

    except Exception as e:
        logger.error(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()

        try:
            commenter.close_browser()
        except:
            pass


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 页面结构检查工具                                 ║
╚════════════════════════════════════════════════════════════════╝

目标:
  • 访问真实产品页面
  • 检查页面元素
  • 找到正确的选择器

准备开始...
""")

    input("按 Enter 开始检查...")

    inspect_product_page()

    print("\n完成！现在可以更新选择器了")
