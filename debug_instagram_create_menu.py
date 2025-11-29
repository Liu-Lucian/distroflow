#!/usr/bin/env python3
"""
Instagram Create Menu Debug Script
专门调试点击"创建"后的菜单行为
"""

import sys
sys.path.insert(0, 'src')

from instagram_poster import InstagramPoster
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def debug_create_menu():
    """详细调试Instagram创建菜单"""

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

        # 访问Instagram主页
        logger.info("🌐 访问Instagram主页...")
        poster.page.goto("https://www.instagram.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        logger.info("✅ Instagram主页已加载")
        poster.take_screenshot("menu_debug_1_homepage")

        # 步骤1: 点击"创建"按钮
        logger.info("\n" + "="*80)
        logger.info("步骤1: 点击'创建'按钮")
        logger.info("="*80)

        create_selectors = [
            'a[href*="/create/"]:has-text("创建")',
            'span:has-text("创建")',
            'div:has-text("创建")',
        ]

        create_clicked = False
        for selector in create_selectors:
            try:
                elem = poster.page.wait_for_selector(selector, timeout=3000)
                if elem and elem.is_visible():
                    logger.info(f"找到创建按钮: {selector}")
                    elem.click()
                    logger.info("✅ 已点击创建按钮")
                    create_clicked = True
                    break
            except:
                continue

        if not create_clicked:
            logger.error("❌ 未找到创建按钮")
            return False

        # 关键：等待菜单出现
        logger.info("\n等待创建菜单出现...")
        time.sleep(2)  # 给菜单时间渲染

        poster.take_screenshot("menu_debug_2_after_create_click")

        # 检查页面状态 - 查找菜单相关元素
        logger.info("\n" + "="*80)
        logger.info("检查创建菜单状态")
        logger.info("="*80)

        # 查找所有可能的菜单容器
        menu_selectors = [
            '[role="dialog"]',
            '[role="menu"]',
            'div[class*="menu"]',
            'div[class*="Menu"]',
            'div[class*="popup"]',
            'div[class*="Popup"]',
        ]

        menu_found = False
        for selector in menu_selectors:
            try:
                elems = poster.page.query_selector_all(selector)
                if elems:
                    logger.info(f"找到 {len(elems)} 个 {selector} 元素")
                    for i, elem in enumerate(elems):
                        visible = elem.is_visible()
                        if visible:
                            logger.info(f"  元素 {i}: visible=True")
                            # 尝试获取内部文本
                            try:
                                text = elem.inner_text()
                                logger.info(f"    文本内容: {text[:200]}")
                                menu_found = True
                            except:
                                pass
            except Exception as e:
                pass

        if not menu_found:
            logger.warning("⚠️  未找到明显的菜单元素")

        # 查找包含"帖子"文本的所有元素
        logger.info("\n" + "="*80)
        logger.info("查找包含'帖子'的所有可见元素")
        logger.info("="*80)

        # 方法1: 使用:has-text查找
        post_elements = poster.page.query_selector_all('*:has-text("帖子")')
        logger.info(f"找到 {len(post_elements)} 个包含'帖子'的元素")

        visible_post_elements = []
        for i, elem in enumerate(post_elements[:20]):  # 只看前20个
            try:
                if elem.is_visible():
                    tag = elem.evaluate('el => el.tagName')
                    text = elem.inner_text()
                    classes = elem.get_attribute('class') or ''
                    logger.info(f"  元素 {i}: <{tag}> class='{classes[:50]}' text='{text[:50]}'")
                    visible_post_elements.append(elem)
            except:
                pass

        # 步骤2: 尝试点击"帖子"（使用更精确的选择器）
        logger.info("\n" + "="*80)
        logger.info("步骤2: 尝试点击'帖子'选项")
        logger.info("="*80)

        if visible_post_elements:
            logger.info(f"尝试点击第一个可见的'帖子'元素...")
            try:
                visible_post_elements[0].click()
                logger.info("✅ 已点击'帖子'")

                # 等待上传对话框
                logger.info("\n等待上传对话框出现...")
                time.sleep(3)

                poster.take_screenshot("menu_debug_3_after_post_click")

                # 检查上传对话框
                logger.info("\n" + "="*80)
                logger.info("检查上传对话框状态")
                logger.info("="*80)

                # 查找dialog
                dialogs = poster.page.query_selector_all('[role="dialog"]')
                logger.info(f"找到 {len(dialogs)} 个dialog元素")

                for i, dialog in enumerate(dialogs):
                    try:
                        visible = dialog.is_visible()
                        logger.info(f"  Dialog {i}: visible={visible}")
                        if visible:
                            # 获取dialog的所有文本
                            text = dialog.inner_text()
                            logger.info(f"    Dialog文本: {text[:300]}")

                            # 查找文件input
                            file_inputs = dialog.query_selector_all('input[type="file"]')
                            logger.info(f"    Dialog内的file input: {len(file_inputs)} 个")

                            for j, inp in enumerate(file_inputs):
                                accept = inp.get_attribute('accept')
                                visible_input = inp.is_visible()
                                logger.info(f"      Input {j}: accept={accept}, visible={visible_input}")
                    except Exception as e:
                        logger.error(f"  检查dialog {i} 失败: {e}")

                # 查找所有file input（全局）
                all_file_inputs = poster.page.query_selector_all('input[type="file"]')
                logger.info(f"\n全局file input总数: {len(all_file_inputs)}")

                for i, inp in enumerate(all_file_inputs):
                    try:
                        accept = inp.get_attribute('accept')
                        visible = inp.is_visible()
                        name = inp.get_attribute('name')
                        logger.info(f"  Input {i}: accept={accept}, name={name}, visible={visible}")
                    except:
                        pass

            except Exception as e:
                logger.error(f"❌ 点击'帖子'失败: {e}")

        else:
            logger.warning("⚠️  未找到可见的'帖子'元素")

        # 保持浏览器打开，供手动检查
        logger.info("\n" + "="*80)
        logger.info("🔍 浏览器将保持打开60秒，请手动点击'创建'→'帖子'观察实际行为")
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
    debug_create_menu()
