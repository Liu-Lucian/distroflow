#!/usr/bin/env python3
"""
测试AI Vision评论按钮识别器
用用户提供的截图测试
"""
import sys
import os

# 测试AI识别能力
from reddit_comment_button_finder import find_comment_button_position

print("=" * 80)
print("🧪 测试AI Vision评论按钮识别器")
print("=" * 80)
print()

# 如果用户提供了截图路径，使用用户的截图
if len(sys.argv) > 1:
    screenshot_path = sys.argv[1]
else:
    # 否则提示用户提供截图
    print("请提供Reddit截图路径：")
    print("  python3 test_ai_comment_finder.py /path/to/screenshot.png")
    print()
    print("或者拖拽截图到这里后按回车：")
    screenshot_path = input().strip()

if not os.path.exists(screenshot_path):
    print(f"❌ 截图不存在: {screenshot_path}")
    sys.exit(1)

print(f"📸 截图路径: {screenshot_path}")
print()
print("🧠 正在调用GPT-4o Vision识别...")
print()

position = find_comment_button_position(screenshot_path)

print()
print("=" * 80)

if position:
    print("✅ AI识别成功！")
    print()
    print(f"📍 评论按钮位置: ({position['x']}, {position['y']})")
    print()
    print("这个坐标可以用来精确点击评论按钮！")
else:
    print("❌ AI识别失败")
    print()
    print("可能的原因：")
    print("1. 截图中没有明显的评论按钮")
    print("2. 评论按钮被遮挡")
    print("3. API调用失败")

print("=" * 80)
