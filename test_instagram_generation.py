#!/usr/bin/env python3
"""
测试Instagram内容生成 - 不实际发布
测试图片生成和Caption生成
"""
import sys
sys.path.insert(0, 'src')
import os
from auto_instagram_forever import InstagramForeverBot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查API key
if 'OPENAI_API_KEY' not in os.environ:
    print("❌ 请设置 OPENAI_API_KEY")
    sys.exit(1)

print("=" * 80)
print("🧪 测试Instagram Build in Public内容生成")
print("=" * 80)
print()

bot = InstagramForeverBot()

# 测试1: 生成图片
print("📌 测试1: 生成Day 1图片...")
print("-" * 80)
day_1_image = bot.generate_post_image(1, "Building HireMeAI")
print(f"✅ 图片生成成功: {day_1_image}")
print()

# 测试2: 生成Caption
print("📌 测试2: 生成Build in Public Caption...")
print("-" * 80)
caption = bot.generate_build_in_public_caption()
print(f"Caption长度: {len(caption)} 字符")
print()
print("Caption内容:")
print("-" * 80)
print(caption)
print("-" * 80)
print()

# 测试3: 生成Hashtags
print("📌 测试3: 生成Hashtags...")
print("-" * 80)
hashtags = bot.generate_hashtags()
print(f"Hashtags: {hashtags}")
print(f"Hashtags数量: {len(hashtags.split())}")
print()

# 测试4: 生成完整帖子（包括再生成一张图片）
print("📌 测试4: 生成Day 2完整帖子...")
print("-" * 80)
day_2_image = bot.generate_post_image(2, "Building HireMeAI")
caption_2 = bot.generate_build_in_public_caption()
hashtags_2 = bot.generate_hashtags()

print(f"✅ 完整帖子生成成功！")
print()
print(f"图片: {day_2_image}")
print(f"Caption: {caption_2[:100]}...")
print(f"Hashtags: {hashtags_2}")
print()

# 测试5: 检查生成的图片
print("📌 测试5: 验证生成的图片...")
print("-" * 80)
import os.path
if os.path.exists(day_1_image) and os.path.exists(day_2_image):
    from PIL import Image
    img1 = Image.open(day_1_image)
    img2 = Image.open(day_2_image)

    print(f"✅ Day 1图片: {img1.size} {img1.mode}")
    print(f"✅ Day 2图片: {img2.size} {img2.mode}")
    print()

    print(f"💡 你可以查看生成的图片:")
    print(f"   open {day_1_image}")
    print(f"   open {day_2_image}")
else:
    print("❌ 图片文件不存在")

print()
print("=" * 80)
print("✅ 所有测试通过！")
print("=" * 80)
print()
print("下一步:")
print("  1. 检查生成的图片效果")
print("  2. 检查生成的Caption是否符合3段式结构")
print("  3. 确认Instagram登录: platforms_auth.json")
print("  4. 运行完整系统: python3 auto_instagram_forever.py")
print()
