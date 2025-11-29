#!/usr/bin/env python3
"""
Instagram Upload Debug Script
调试Instagram上传流程，找出问题所在
"""

import sys
sys.path.insert(0, 'src')

from instagram_poster import InstagramPoster
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def debug_instagram_upload():
    """详细调试Instagram上传流程"""

    poster = InstagramPoster()

    try:
        # 设置浏览器 (不使用headless，方便观察)
        logger.info("🌐 设置浏览器...")
        poster.setup_browser(headless=False)

        # 验证登录
        if not poster.verify_login():
            logger.error("❌ 登录失败")
            return False

        logger.info("✅ 登录成功")

        # **关键：访问Instagram主页**
        logger.info("🌐 访问Instagram主页...")
        poster.page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        logger.info("✅ Instagram主页已加载")
        poster.take_screenshot("debug_homepage")

        # 步骤1: 点击创建按钮
        logger.info("\n" + "="*80)
        logger.info("步骤1: 点击'创建'按钮")
        logger.info("="*80)

        create_selectors = [
            'a[href*="/create/"]:has-text("创建")',
            'span:has-text("创建")',
        ]

        for selector in create_selectors:
            try:
                elem = poster.page.wait_for_selector(selector, timeout=3000)
                if elem and elem.is_visible():
                    logger.info(f"找到创建按钮: {selector}")
                    elem.click()
                    logger.info("✅ 已点击创建按钮")
                    break
            except:
                continue

        time.sleep(3)
        poster.take_screenshot("debug_after_create_click")

        # 检查页面状态
        logger.info("\n检查当前页面元素...")

        # 查找所有可见的按钮和链接
        buttons = poster.page.query_selector_all('button')
        logger.info(f"找到 {len(buttons)} 个button元素")

        for i, btn in enumerate(buttons[:10]):  # 只看前10个
            try:
                text = btn.inner_text()
                visible = btn.is_visible()
                if text and visible:
                    logger.info(f"  Button {i}: '{text}'")
            except:
                pass

        # 查找所有span元素
        spans = poster.page.query_selector_all('span')
        logger.info(f"\n找到 {len(spans)} 个span元素")

        visible_spans = []
        for span in spans:
            try:
                text = span.inner_text()
                visible = span.is_visible()
                if text and visible and len(text) < 30:
                    visible_spans.append(text)
            except:
                pass

        logger.info(f"可见的span文本 (前20个): {visible_spans[:20]}")

        # 步骤2: 尝试点击"帖子"
        logger.info("\n" + "="*80)
        logger.info("步骤2: 查找并点击'帖子'")
        logger.info("="*80)

        post_selectors = [
            'span:has-text("帖子")',
            'div:has-text("帖子")',
            'button:has-text("帖子")',
        ]

        post_clicked = False
        for selector in post_selectors:
            try:
                elem = poster.page.wait_for_selector(selector, timeout=3000)
                if elem and elem.is_visible():
                    text = elem.inner_text()
                    logger.info(f"找到'帖子'元素: {selector}, 文本='{text}'")
                    elem.click()
                    logger.info("✅ 已点击'帖子'")
                    post_clicked = True
                    break
            except Exception as e:
                logger.debug(f"尝试 {selector} 失败: {str(e)[:50]}")
                continue

        if not post_clicked:
            logger.warning("⚠️  未找到'帖子'按钮")

        time.sleep(5)
        poster.take_screenshot("debug_after_post_click")

        # 步骤3: 检查是否有上传对话框
        logger.info("\n" + "="*80)
        logger.info("步骤3: 检查上传对话框")
        logger.info("="*80)

        # 查找dialog
        dialogs = poster.page.query_selector_all('[role="dialog"]')
        logger.info(f"找到 {len(dialogs)} 个dialog元素")

        for i, dialog in enumerate(dialogs):
            try:
                visible = dialog.is_visible()
                logger.info(f"  Dialog {i}: visible={visible}")
                if visible:
                    # 查找dialog内的所有文本
                    texts = dialog.query_selector_all('span, div, button')
                    dialog_texts = []
                    for t in texts[:20]:
                        try:
                            txt = t.inner_text()
                            if txt and len(txt) < 50:
                                dialog_texts.append(txt)
                        except:
                            pass
                    logger.info(f"    Dialog内的文本: {dialog_texts}")
            except Exception as e:
                logger.error(f"  检查dialog {i} 失败: {e}")

        # 查找form
        forms = poster.page.query_selector_all('form')
        logger.info(f"\n找到 {len(forms)} 个form元素")

        for i, form in enumerate(forms):
            try:
                visible = form.is_visible()
                method = form.get_attribute('method')
                logger.info(f"  Form {i}: visible={visible}, method={method}")
            except Exception as e:
                logger.error(f"  检查form {i} 失败: {e}")

        # 步骤4: 查找file input
        logger.info("\n" + "="*80)
        logger.info("步骤4: 查找file input元素")
        logger.info("="*80)

        file_inputs = poster.page.query_selector_all('input[type="file"]')
        logger.info(f"找到 {len(file_inputs)} 个input[type='file']元素")

        for i, inp in enumerate(file_inputs):
            try:
                visible = inp.is_visible()
                accept = inp.get_attribute('accept')
                name = inp.get_attribute('name')
                logger.info(f"  Input {i}: visible={visible}, accept={accept}, name={name}")
            except Exception as e:
                logger.error(f"  检查input {i} 失败: {e}")

        # 查找所有input
        all_inputs = poster.page.query_selector_all('input')
        logger.info(f"\n找到 {len(all_inputs)} 个input元素")

        for i, inp in enumerate(all_inputs[:10]):
            try:
                type_attr = inp.get_attribute('type')
                accept = inp.get_attribute('accept')
                visible = inp.is_visible()
                logger.info(f"  Input {i}: type={type_attr}, accept={accept}, visible={visible}")
            except Exception as e:
                pass

        # 保持浏览器打开，供手动检查
        logger.info("\n" + "="*80)
        logger.info("🔍 浏览器将保持打开60秒，请手动检查页面状态")
        logger.info("="*80)
        time.sleep(60)

    except Exception as e:
        logger.error(f"❌ 调试过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("关闭浏览器...")
        poster.close_browser()

if __name__ == "__main__":
    debug_instagram_upload()
