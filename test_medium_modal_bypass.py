#!/usr/bin/env python3
"""
测试绕过 Medium 弹窗的方法
"""
import sys
sys.path.insert(0, 'src')

from medium_poster import MediumPoster
import logging
import time

logging.basicConfig(level=logging.INFO)

poster = MediumPoster()

try:
    poster.setup_browser(headless=False)

    print("=" * 80)
    print("方法1: 尝试用 JavaScript 移除弹窗并强制加载编辑器")
    print("=" * 80)

    # 访问 Medium 首页
    poster.page.goto("https://medium.com/", wait_until="domcontentloaded")
    time.sleep(2)

    # 点击 Write 按钮
    write_btn = poster.page.wait_for_selector('a[href*="/new-story"]', timeout=10000)
    write_btn.click()
    print(f"当前 URL: {poster.page.url}")
    time.sleep(3)

    # 方法1: 用 JavaScript 移除弹窗
    print("\n尝试用 JavaScript 移除弹窗...")
    js_code = """
    (() => {
        // 移除所有弹窗/遮罩层
        const modals = document.querySelectorAll('[role="dialog"], [class*="modal"], [class*="overlay"]');
        modals.forEach(modal => modal.remove());

        // 移除所有固定定位的元素（通常是弹窗）
        const fixedElements = Array.from(document.querySelectorAll('*')).filter(el => {
            const style = window.getComputedStyle(el);
            return style.position === 'fixed' || style.position === 'absolute';
        });
        fixedElements.forEach(el => {
            if (el.textContent && el.textContent.includes('Medium app')) {
                el.remove();
            }
        });

        // 恢复 body 滚动
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';

        return 'Modal removed';
    })();
    """

    result = poster.page.evaluate(js_code)
    print(f"   JavaScript 执行结果: {result}")
    time.sleep(2)

    # 截图1
    poster.take_screenshot("modal_removed")

    # 尝试查找编辑器
    print("\n查找编辑器元素...")
    elements = poster.page.query_selector_all('[contenteditable="true"], [data-slate-editor="true"], h1, h3')
    print(f"   找到 {len(elements)} 个可能的编辑器元素")

    if len(elements) == 0:
        print("\n编辑器仍然未加载，尝试方法2...")
        print("=" * 80)
        print("方法2: 刷新页面并注入 JavaScript 阻止弹窗加载")
        print("=" * 80)

        # 注入脚本来阻止弹窗加载
        poster.page.evaluate("""
            // 在 DOM 加载前注入脚本
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) { // Element node
                            // 移除包含 "Medium app" 的元素
                            if (node.textContent && node.textContent.includes('Medium app')) {
                                node.remove();
                            }
                            // 移除 role="dialog" 的元素
                            if (node.getAttribute && node.getAttribute('role') === 'dialog') {
                                node.remove();
                            }
                        }
                    });
                });
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            return 'Observer installed';
        """)

        # 刷新页面
        poster.page.reload(wait_until="domcontentloaded")
        time.sleep(5)

        # 截图2
        poster.take_screenshot("page_reloaded")

        # 再次查找编辑器
        elements = poster.page.query_selector_all('[contenteditable="true"], [data-slate-editor="true"], h1, h3')
        print(f"   刷新后找到 {len(elements)} 个元素")

    if len(elements) == 0:
        print("\n编辑器仍然未加载，尝试方法3...")
        print("=" * 80)
        print("方法3: 直接访问编辑器 URL 并等待")
        print("=" * 80)

        # 直接导航到新文章 URL
        poster.page.goto("https://medium.com/new-story", wait_until="networkidle")
        time.sleep(5)

        # 移除弹窗
        poster.page.evaluate(js_code)
        time.sleep(2)

        # 截图3
        poster.take_screenshot("direct_navigation")

        # 查找编辑器
        elements = poster.page.query_selector_all('[contenteditable="true"], [data-slate-editor="true"], h1, h3')
        print(f"   直接导航后找到 {len(elements)} 个元素")

    # 打印找到的元素信息
    if len(elements) > 0:
        print("\n✅ 找到编辑器元素!")
        for i, elem in enumerate(elements[:5]):
            try:
                tag_name = elem.evaluate('el => el.tagName')
                attrs = elem.evaluate('el => ({id: el.id, class: el.className, contenteditable: el.contentEditable})')
                print(f"\n元素 {i+1}:")
                print(f"  标签: {tag_name}")
                print(f"  属性: {attrs}")
            except Exception as e:
                print(f"  错误: {e}")

        # 尝试填写标题
        print("\n尝试用键盘输入标题...")
        try:
            first_elem = elements[0]
            first_elem.click(force=True)
            time.sleep(1)

            # 使用键盘输入而不是 fill (因为 contenteditable="inherit")
            poster.page.keyboard.type("Test Title - 这是一个测试标题", delay=50)
            print("   ✅ 标题输入成功!")

            # 按回车进入正文
            poster.page.keyboard.press("Enter")
            time.sleep(1)

            poster.page.keyboard.type("This is test content. 这是测试内容。", delay=50)
            print("   ✅ 正文输入成功!")
        except Exception as e:
            print(f"   ❌ 输入失败: {e}")
    else:
        print("\n❌ 未找到编辑器元素")

    print("\n=" * 80)
    print("等待 30 秒以便检查...")
    time.sleep(30)

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    poster.close_browser()
