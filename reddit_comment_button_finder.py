#!/usr/bin/env python3
"""
Reddit评论按钮AI识别器
使用GPT-4o Vision自动识别并点击评论按钮
"""
import base64
import os
from openai import OpenAI

def find_comment_button_position(screenshot_path):
    """
    使用GPT-4o Vision识别评论按钮位置

    Args:
        screenshot_path: 截图路径

    Returns:
        dict: {'x': int, 'y': int} 按钮中心坐标，或None如果识别失败
    """
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    # 读取截图
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # 让AI识别评论按钮
    prompt = """
Please analyze this Reddit post page screenshot and find the COMMENT BUTTON.

The comment button is usually located below the post title and description, next to the upvote/downvote buttons and share button. It typically shows:
- A comment/chat bubble icon
- A number indicating how many comments (e.g., "22")

Please identify the CENTER coordinates of the comment button and return ONLY a JSON object in this exact format:
{"x": <x_coordinate>, "y": <y_coordinate>}

If you cannot find the comment button, return:
{"error": "Comment button not found"}

Return ONLY the JSON, no other text.
"""

    try:
        print(f"   📤 发送截图到GPT-4o Vision...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100,
            temperature=0
        )

        result_text = response.choices[0].message.content.strip()
        print(f"   📥 GPT-4o返回: {result_text}")

        # 解析JSON响应
        import json
        result = json.loads(result_text)

        if 'error' in result:
            print(f"   ❌ AI无法识别评论按钮: {result['error']}")
            return None

        if 'x' in result and 'y' in result:
            print(f"   ✅ AI成功识别评论按钮位置: ({result['x']}, {result['y']})")
            return result

        print(f"   ❌ AI返回格式错误: {result_text}")
        return None

    except Exception as e:
        print(f"   ❌ AI识别失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def click_comment_button_with_ai(page, screenshot_name="reddit_comment_button.png"):
    """
    使用AI Vision识别并点击评论按钮

    Args:
        page: Playwright page对象
        screenshot_name: 截图文件名

    Returns:
        bool: 是否成功点击
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info("🤖 启动AI Vision识别评论按钮...")

    # 截取当前页面
    screenshot_path = f"/tmp/{screenshot_name}"
    page.screenshot(path=screenshot_path, full_page=False)
    logger.info(f"   📸 页面截图已保存: {screenshot_path}")

    # 使用AI识别按钮位置
    logger.info(f"   🧠 调用GPT-4o Vision分析截图...")
    position = find_comment_button_position(screenshot_path)

    if not position:
        logger.error(f"   ❌ AI无法识别评论按钮位置")
        return False

    # 点击识别到的位置
    try:
        logger.info(f"   🎯 AI识别到评论按钮坐标: ({position['x']}, {position['y']})")
        logger.info(f"   🖱️  执行鼠标点击...")
        page.mouse.click(position['x'], position['y'])
        logger.info(f"   ✅ 已成功点击评论按钮")
        return True
    except Exception as e:
        logger.error(f"   ❌ 点击失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试脚本
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 reddit_comment_button_finder.py <screenshot_path>")
        sys.exit(1)

    screenshot_path = sys.argv[1]

    if not os.path.exists(screenshot_path):
        print(f"❌ 截图不存在: {screenshot_path}")
        sys.exit(1)

    print("=" * 80)
    print("🤖 Reddit评论按钮AI识别器")
    print("=" * 80)

    position = find_comment_button_position(screenshot_path)

    if position:
        print(f"\n✅ 成功识别评论按钮！")
        print(f"   坐标: ({position['x']}, {position['y']})")
    else:
        print(f"\n❌ 无法识别评论按钮")

    print("=" * 80)
