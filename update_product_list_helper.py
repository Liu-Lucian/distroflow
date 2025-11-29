#!/usr/bin/env python3
"""
Product Hunt 产品列表更新助手
帮助用户快速手动更新产品列表
"""
import json
from datetime import datetime

print("=" * 80)
print("📋 Product Hunt 产品列表更新助手")
print("=" * 80)

print("\n请按以下步骤操作:")
print("1. 在浏览器中访问: https://www.producthunt.com")
print("2. 查看今日产品列表")
print("3. 选择 3-5 个相关产品（AI Tools, Productivity, Developer Tools）")
print("4. 复制产品 URL（例如: https://www.producthunt.com/posts/nimo）\n")

products = []

print("请输入产品信息（输入空行结束）:\n")

while True:
    url = input(f"产品 {len(products) + 1} URL (直接回车结束): ").strip()

    if not url:
        break

    if '/posts/' not in url:
        print("   ⚠️  URL 格式不正确，应包含 /posts/")
        continue

    # 提取产品名
    try:
        slug = url.split('/posts/')[-1].strip('/').split('?')[0]
        name = slug.replace('-', ' ').title()
    except:
        name = "Product"

    # 可选：输入描述
    tagline = input(f"   产品介绍（可选，直接回车跳过）: ").strip() or f"{name} - Product from Product Hunt"

    products.append({
        'url': url if url.startswith('http') else f"https://www.producthunt.com{url}",
        'name': name,
        'tagline': tagline,
        'category': 'Various',
        'description': tagline
    })

    print(f"   ✅ 已添加: {name}\n")

if not products:
    print("\n❌ 未添加任何产品，退出")
    exit(0)

# 保存到文件
output_file = "todays_producthunt_products.json"

data = {
    "date": datetime.now().strftime('%Y-%m-%d'),
    "source": "Manual update via helper script",
    "products": products
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ 成功保存 {len(products)} 个产品到 {output_file}")
print(f"\n可以运行以下命令开始评论:")
print(f"   python3 auto_producthunt_forever.py")
print("\n" + "=" * 80)
