#!/usr/bin/env python3
"""
立即测试Instagram Build in Public发布
不等待调度，直接生成并发布一个帖子
"""
import sys
sys.path.insert(0, 'src')
import os
import logging
from auto_instagram_forever import InstagramForeverBot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查API key
if 'OPENAI_API_KEY' not in os.environ:
    print("❌ 请设置 OPENAI_API_KEY")
    print("export OPENAI_API_KEY='your-key'")
    sys.exit(1)

print("=" * 80)
print("📸 Instagram Build in Public - 立即发布测试")
print("=" * 80)
print()

bot = InstagramForeverBot()

# 步骤1: 生成图片
print("🎨 步骤1: 生成Day图片...")
day_number = bot.increment_day()
image_path = bot.generate_post_image(day_number, "Building HireMeAI")
print(f"   ✅ 图片生成: {image_path}")
print()

# 步骤2: 生成Caption
print("✍️  步骤2: 生成Build in Public Caption...")
caption = bot.generate_build_in_public_caption()
print(f"   ✅ Caption生成 ({len(caption)} 字符)")
print()
print("Caption内容:")
print("-" * 80)
print(caption)
print("-" * 80)
print()

# 步骤3: 生成Hashtags
print("🏷️  步骤3: 生成Hashtags...")
hashtags = bot.generate_hashtags()
print(f"   ✅ Hashtags: {hashtags}")
print()

# 步骤4: 准备帖子数据
post_data = {
    'day_number': day_number,
    'image_path': image_path,
    'caption': caption,
    'hashtags': hashtags
}

# 步骤5: 询问用户确认
print("=" * 80)
print("📋 准备发布的内容:")
print("=" * 80)
print(f"Day: {day_number}")
print(f"Image: {image_path}")
print(f"Caption: {caption[:100]}...")
print(f"Hashtags: {hashtags.split()[0]}... ({len(hashtags.split())} tags)")
print("=" * 80)
print()

# 自动打开图片预览
import subprocess
try:
    subprocess.run(['open', image_path], check=True)
    print("✅ 图片已在预览中打开")
except:
    print("⚠️  无法打开图片预览")

print()
confirm = input("确认立即发布到Instagram? (y/n): ")

if confirm.lower() != 'y':
    print("❌ 已取消发布")
    sys.exit(0)

# 步骤6: 发布到Instagram
print()
print("=" * 80)
print("📤 步骤6: 发布到Instagram...")
print("=" * 80)
print()

success = bot.post_single_instagram(post_data)

print()
print("=" * 80)
if success:
    print("✅ Instagram帖子发布成功！")
    print(f"   Day {day_number}")
    print(f"   Caption: {len(caption)} 字符")
    print(f"   Hashtags: {len(hashtags.split())} 个")
else:
    print("❌ Instagram发布失败")
    print("   请检查日志查看详细错误")
print("=" * 80)
