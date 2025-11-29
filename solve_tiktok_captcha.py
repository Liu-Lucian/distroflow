#!/usr/bin/env python3
"""
TikTok验证码自动解决器
使用AI Vision识别拼图位置并自动完成滑块验证
"""

import sys
sys.path.append('src')

import json
import time
import base64
import os
from playwright.sync_api import sync_playwright
from openai import OpenAI

print("=" * 70)
print("🔐 TikTok CAPTCHA Solver - AI Vision")
print("=" * 70)

# 检查API Key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("\n❌ OPENAI_API_KEY not set!")
    sys.exit(1)

client = OpenAI(api_key=api_key)

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
    sessionid = auth['tiktok']['sessionid']

TEST_VIDEO = 'https://www.tiktok.com/@anna..papalia/video/7525232648474610958'

print(f"\n📹 测试视频: {TEST_VIDEO}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=300,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.tiktok.com',
        'path': '/'
    }])

    page = context.new_page()

    print("📱 加载视频页面...")
    page.goto(TEST_VIDEO, timeout=30000)
    time.sleep(5)

    print("📜 滚动触发评论区...")
    for i in range(3):
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(2)

    # 截图分析
    print("\n📸 截图分析验证码...")
    screenshot_bytes = page.screenshot()
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

    print("🤖 AI分析验证码位置...\n")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """Analyze this TikTok CAPTCHA puzzle slider.

I can see there's a puzzle piece that needs to be dragged to complete the image.

Please:
1. Identify the MISSING PIECE (the gap in the background image)
2. Calculate approximately how far from the LEFT the gap is (as a percentage, 0-100%)
3. Provide the X-coordinate percentage where I should drag the slider to

Respond ONLY with a JSON object:
{
  "has_captcha": true/false,
  "gap_position_percent": 0-100,
  "confidence": 0.0-1.0,
  "description": "brief description of what you see"
}"""},
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
        print(f"  有验证码: {analysis.get('has_captcha')}")
        print(f"  缺口位置: {analysis.get('gap_position_percent')}%")
        print(f"  置信度: {analysis.get('confidence')}")
        print(f"  描述: {analysis.get('description')}")
        print("=" * 70)

        if analysis.get('has_captcha'):
            gap_percent = analysis.get('gap_position_percent', 50)

            print(f"\n🎯 尝试自动解决验证码...")
            print(f"   目标位置: {gap_percent}%")

            # 查找滑块元素
            slider_selectors = [
                '[class*="slider"]',
                '[class*="Slider"]',
                '[role="slider"]',
                'div[class*="seraph"]',  # TikTok常用的滑块类名
            ]

            slider = None
            for selector in slider_selectors:
                try:
                    slider = page.wait_for_selector(selector, timeout=3000)
                    if slider:
                        print(f"   ✅ 找到滑块: {selector}")
                        break
                except:
                    continue

            if slider:
                # 获取滑块的位置和可拖动距离
                box = slider.bounding_box()

                if box:
                    # 计算拖动距离
                    # 通常滑块轨道宽度约为300-400px
                    track_width = 350  # 估计值
                    drag_distance = (gap_percent / 100) * track_width

                    print(f"   📏 预计拖动距离: {drag_distance:.0f}px")

                    # 模拟人类拖动（不是直线，而是曲线）
                    print("   🖱️  模拟人类拖动...")

                    # 移动到滑块
                    page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    time.sleep(0.5)

                    # 按下
                    page.mouse.down()
                    time.sleep(0.2)

                    # 分段拖动（模拟人类不稳定的手）
                    steps = 10
                    for i in range(1, steps + 1):
                        progress = i / steps
                        # 添加随机抖动
                        import random
                        jitter_y = random.randint(-2, 2)

                        target_x = box['x'] + (drag_distance * progress)
                        target_y = box['y'] + box['height']/2 + jitter_y

                        page.mouse.move(target_x, target_y)
                        time.sleep(random.uniform(0.02, 0.05))

                    # 释放
                    time.sleep(0.3)
                    page.mouse.up()

                    print("   ✅ 拖动完成!")
                    print("\n⏳ 等待验证结果...")
                    time.sleep(5)

                    # 检查是否成功
                    screenshot_after = page.screenshot()
                    screenshot_after_base64 = base64.b64encode(screenshot_after).decode('utf-8')

                    print("🤖 检查验证是否成功...\n")

                    verify_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Is the CAPTCHA still visible? Or has it been solved and the page shows comments? Answer with JSON: {\"captcha_solved\": true/false, \"comments_visible\": true/false}"},
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
                        verify_result = json.loads(verify_text)
                        if verify_result.get('captcha_solved'):
                            print("✅ 验证码已解决!")
                            if verify_result.get('comments_visible'):
                                print("✅ 评论区已可见!")
                            else:
                                print("⏳ 评论正在加载...")
                                time.sleep(3)
                        else:
                            print("⚠️  验证码仍然存在，可能需要重试")
                    except:
                        pass
                else:
                    print("   ❌ 无法获取滑块位置")
            else:
                print("   ❌ 未找到滑块元素")
                print("   💡 建议: 手动完成验证")

        else:
            print("\n✅ AI未检测到验证码")

    except json.JSONDecodeError as e:
        print(f"❌ 解析AI响应失败: {e}")
        print(f"原始响应: {analysis_text}")

    print("\n⏸  浏览器保持打开60秒供检查...")
    print("   (你可以查看验证是否成功)\n")
    time.sleep(60)

    browser.close()

print("✅ 完成")
