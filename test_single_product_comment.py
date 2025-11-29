#!/usr/bin/env python3
"""测试单个产品评论"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# 读取产品列表
with open('todays_producthunt_products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    products = data['products']

# 测试第一个产品
product = products[0]
print(f"测试产品: {product['name']}")
print(f"URL: {product['url']}")

# 生成评论
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Write a short enthusiastic Product Hunt comment for {product['name']}: {product['tagline']}. Use internet slang and 1 emoji. Max 100 chars."}],
    temperature=0.9,
    max_tokens=50
)

comment = response.choices[0].message.content.strip().strip('"').strip("'")
print(f"评论: {comment}\n")

# 测试评论
commenter = ProductHuntCommenter()
commenter.setup_browser(headless=False)

if not commenter.verify_login():
    print("❌ 未登录")
    commenter.close_browser()
    sys.exit(1)

success = commenter.comment_on_product(
    product_url=product['url'],
    comment_text=comment,
    upvote=True
)

if success:
    print("✅ 测试成功！")
else:
    print("❌ 测试失败")

input("\n按 Enter 关闭浏览器...")
commenter.close_browser()
