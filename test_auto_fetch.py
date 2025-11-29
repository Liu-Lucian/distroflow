#!/usr/bin/env python3
"""
测试自动获取 Product Hunt 产品功能
"""
import sys
sys.path.insert(0, 'src')

from auto_producthunt_forever import ProductHuntForever
import json

print("=" * 80)
print("🔍 测试自动获取 Product Hunt 产品")
print("=" * 80)

# 创建实例
forever = ProductHuntForever()

# 测试自动获取
print("\n1️⃣ 测试 auto_fetch_todays_products()...")
products = forever.auto_fetch_todays_products()

print(f"\n✅ 获取到 {len(products)} 个产品:")
for i, product in enumerate(products[:5], 1):
    print(f"   {i}. {product['name']}")
    print(f"      URL: {product['url']}")

# 测试 load_available_products() 的自动补充逻辑
print("\n2️⃣ 测试 load_available_products() 自动补充...")

# 先清空产品文件来触发自动获取
import os
backup_file = "todays_producthunt_products.json.backup"
if os.path.exists("todays_producthunt_products.json"):
    os.rename("todays_producthunt_products.json", backup_file)
    print("   已备份现有产品列表")

available = forever.load_available_products()

print(f"\n✅ load_available_products() 返回 {len(available)} 个可用产品")

# 恢复备份
if os.path.exists(backup_file):
    os.rename(backup_file, "todays_producthunt_products.json")
    print("   已恢复产品列表备份")

# 检查文件是否被更新
if os.path.exists("todays_producthunt_products.json"):
    with open("todays_producthunt_products.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"\n✅ 产品列表文件包含 {len(data.get('products', []))} 个产品")

print("\n" + "=" * 80)
print("✅ 测试完成！")
print("=" * 80)
