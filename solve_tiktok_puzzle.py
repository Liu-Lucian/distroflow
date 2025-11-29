#!/usr/bin/env python3
"""
TikTok拼图验证码自动解决
基于AI Vision识别缺口位置并精确拖动
"""

import sys
sys.path.append('src')

import json
import time
import base64
import os
import random
from playwright.sync_api import sync_playwright
from openai import OpenAI

print("=" * 70)
print("🧩 TikTok拼图验证码自动解决器")
print("=" * 70)

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not set!")
    sys.exit(1)

client = OpenAI(api_key=api_key)

with open('platforms_auth.json', 'r') as f:
    sessionid = json.load(f)['tiktok']['sessionid']

TEST_VIDEO = 'https://www.tiktok.com/@anna..papalia/video/7525232648474610958'

print(f"\n📹 视频: {TEST_VIDEO}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=200,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 800}
    )
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.tiktok.com',
        'path': '/'
    }])

    page = context.new_page()

    print("📱 加载页面...")
    page.goto(TEST_VIDEO, timeout=30000)
    time.sleep(5)

    print("📜 滚动触发验证码...")
    for i in range(3):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(2)

    # 等待验证码出现
    time.sleep(3)

    print("\n📸 截图分析验证码...")
    screenshot_bytes = page.screenshot()
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    print("🤖 AI分析拼图缺口位置...\n")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """分析这个TikTok拼图验证码。

我看到一个背景图片，上面有个**拼图缺口**（空白区域），还有一个需要拖动的拼图片。

请：
1. 找到背景图片中的**缺口位置**（缺少拼图的地方）
2. 估算缺口距离**左边界**的百分比位置（0-100%）
3. 缺口通常在图片中间偏左或偏右

返回JSON格式：
{
  "has_puzzle": true/false,
  "gap_position_percent": 0-100,
  "gap_description": "描述缺口在哪里（如：中间偏左，右侧等）",
  "confidence": 0.0-1.0
}

注意：
- gap_position_percent 是缺口中心距离图片左边的百分比
- 如果缺口在最左边 = 0-20%
- 如果缺口在中间 = 40-60%
- 如果缺口在右边 = 70-100%"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
            ]
        }],
        max_tokens=500,
        temperature=0.2
    )

    analysis_text = response.choices[0].message.content

    # 提取JSON
    if "```json" in analysis_text:
        json_start = analysis_text.find("```json") + 7
        json_end = analysis_text.find("```", json_start)
        analysis_text = analysis_text[json_start:json_end].strip()
    elif "```" in analysis_text:
        json_start = analysis_text.find("```") + 3
        json_end = analysis_text.find("```", json_start)
        analysis_text = analysis_text[json_start:json_end].strip()

    try:
        analysis = json.loads(analysis_text)

        print("=" * 70)
        print("🧠 AI分析结果:")
        print("=" * 70)
        print(f"  检测到拼图: {analysis.get('has_puzzle')}")
        print(f"  缺口位置: {analysis.get('gap_position_percent')}%")
        print(f"  缺口描述: {analysis.get('gap_description')}")
        print(f"  置信度: {analysis.get('confidence')}")
        print("=" * 70)

        if analysis.get('has_puzzle'):
            gap_percent = float(analysis.get('gap_position_percent', 50))

            print(f"\n🎯 开始解决验证码...")
            print(f"   目标位置: {gap_percent}%\n")

            # 查找滑块
            slider_selectors = [
                'div[class*="slider"]',
                'div[class*="Slider"]',
                'div.seraph-slider',
                '[class*="seraph"]',
                'div[id*="slider"]',
            ]

            slider = None
            print("🔍 查找滑块元素...")
            for selector in slider_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        # 找最可能是滑块的元素（通常有个按钮或把手）
                        for elem in elements:
                            box = elem.bounding_box()
                            if box and box['width'] > 200 and box['height'] < 100:
                                slider = elem
                                print(f"   ✅ 找到滑块: {selector}")
                                print(f"   📏 宽度: {box['width']:.0f}px, 高度: {box['height']:.0f}px")
                                break
                    if slider:
                        break
                except:
                    continue

            if slider:
                box = slider.bounding_box()

                # 计算拖动距离
                track_width = box['width'] - 50  # 减去滑块按钮宽度
                target_distance = (gap_percent / 100) * track_width

                print(f"\n🖱️  准备拖动:")
                print(f"   轨道宽度: {track_width:.0f}px")
                print(f"   目标距离: {target_distance:.0f}px")

                # 找到滑块按钮（通常在左边）
                start_x = box['x'] + 25  # 滑块按钮中心
                start_y = box['y'] + box['height'] / 2

                print(f"\n▶️  开始拖动...")

                # 移动到滑块
                page.mouse.move(start_x, start_y)
                time.sleep(random.uniform(0.3, 0.5))

                # 按下鼠标
                page.mouse.down()
                time.sleep(random.uniform(0.1, 0.2))

                # 模拟人类拖动（加速→减速，带抖动）
                steps = 20
                for i in range(1, steps + 1):
                    progress = i / steps

                    # 缓动函数（开始快，结束慢）
                    if progress < 0.5:
                        ease = 2 * progress * progress
                    else:
                        ease = 1 - pow(-2 * progress + 2, 2) / 2

                    current_distance = target_distance * ease

                    # 添加随机抖动（模拟手抖）
                    jitter_x = random.randint(-2, 2)
                    jitter_y = random.randint(-3, 3)

                    target_x = start_x + current_distance + jitter_x
                    target_y = start_y + jitter_y

                    page.mouse.move(target_x, target_y)
                    time.sleep(random.uniform(0.01, 0.03))

                # 在目标位置附近微调（模拟人类调整）
                for _ in range(3):
                    adjust = random.randint(-3, 3)
                    page.mouse.move(start_x + target_distance + adjust, start_y + random.randint(-2, 2))
                    time.sleep(random.uniform(0.05, 0.1))

                # 释放鼠标
                time.sleep(random.uniform(0.2, 0.4))
                page.mouse.up()

                print("   ✅ 拖动完成!\n")
                print("⏳ 等待验证结果（5秒）...")
                time.sleep(5)

                # 检查是否成功
                screenshot_after = page.screenshot()
                screenshot_after_base64 = base64.b64encode(screenshot_after).decode('utf-8')

                print("🔍 检查验证结果...\n")

                verify_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": """检查拼图验证码是否已解决。

如果：
- 拼图验证码消失了 = 成功
- 可以看到评论区了 = 成功
- 仍然显示拼图 = 失败

返回JSON: {"solved": true/false, "comments_visible": true/false}"""},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_after_base64}"}}
                        ]
                    }],
                    max_tokens=200,
                    temperature=0.2
                )

                verify_text = verify_response.choices[0].message.content
                if "```json" in verify_text:
                    json_start = verify_text.find("```json") + 7
                    json_end = verify_text.find("```", json_start)
                    verify_text = verify_text[json_start:json_end].strip()

                try:
                    result = json.loads(verify_text)

                    print("=" * 70)
                    if result.get('solved'):
                        print("✅ 验证码已解决!")
                        if result.get('comments_visible'):
                            print("✅ 评论区已显示!")

                            print("\n🎉 开始抓取评论...")
                            time.sleep(3)

                            # 滚动加载更多评论
                            for i in range(5):
                                page.evaluate("window.scrollBy(0, 600)")
                                time.sleep(1)

                            # 抓取评论（简单测试）
                            user_links = page.query_selector_all('a[href*="/@"]')
                            print(f"\n找到 {len(user_links)} 个用户链接")
                            print("✅ 验证码解决成功！系统可以正常运行了！")
                        else:
                            print("⏳ 评论正在加载...")
                    else:
                        print("❌ 验证码仍存在")
                        print("💡 可能需要:")
                        print("   1. 调整gap_position_percent")
                        print("   2. 重试")
                        print("   3. 手动完成")
                    print("=" * 70)

                except:
                    print("⚠️  无法解析验证结果")

            else:
                print("❌ 未找到滑块元素")
                print("\n可见的元素类型:")
                all_divs = page.query_selector_all('div')[:20]
                for div in all_divs:
                    classes = div.get_attribute('class') or ''
                    if 'slider' in classes.lower() or 'seraph' in classes.lower():
                        print(f"  - {classes}")

        else:
            print("\n✅ AI未检测到拼图验证码")
            print("   评论区可能已经可见")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n⏸  浏览器保持打开30秒...")
    time.sleep(30)

    browser.close()

print("\n✅ 完成")
