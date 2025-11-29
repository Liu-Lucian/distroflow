#!/usr/bin/env python3
"""
使用 AI Vision 提取产品 + URL 验证
这是最可靠的方法：AI 从截图识别产品，然后访问页面获取真实 slug
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
from datetime import datetime
import base64
from openai import OpenAI

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def extract_products_with_vision(screenshot_path: str) -> list:
    """使用 GPT-4o Vision 从截图提取产品名称"""
    print("\n🤖 使用 AI Vision 识别产品...")

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # 读取截图
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请仔细分析这个 Product Hunt 首页截图，提取所有可见的产品。

对于每个产品，请提供：
1. 产品名称（精确的名称）
2. 产品的一句话描述（tagline）

请以 JSON 数组格式返回，每个产品包含：
{
  "name": "产品名称",
  "tagline": "产品描述"
}

只返回 JSON，不要其他文字。限制在前 10 个产品。"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )

        content = response.choices[0].message.content.strip()

        # 提取 JSON
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()

        products = json.loads(content)
        print(f"   ✅ AI 识别到 {len(products)} 个产品")

        return products

    except Exception as e:
        print(f"   ❌ AI Vision 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def find_product_slug(commenter: ProductHuntCommenter, product_name: str) -> str:
    """访问 Product Hunt 搜索页面，找到产品的真实 slug"""
    print(f"\n   🔍 查找 '{product_name}' 的 slug...")

    try:
        # 使用 Product Hunt 的搜索功能
        search_url = f"https://www.producthunt.com/search?q={product_name.replace(' ', '+')}"
        commenter.page.goto(search_url, timeout=30000)
        time.sleep(5)

        # 在搜索结果中找到第一个产品链接
        js_code = f"""
        () => {{
            const links = document.querySelectorAll('a[href*="/posts/"]');
            for (const link of links) {{
                const href = link.getAttribute('href');
                if (href && href.includes('/posts/') &&
                    !href.includes('/posts/new') &&
                    !href.includes('/posts/all')) {{
                    return href;
                }}
            }}
            return null;
        }}
        """

        result = commenter.page.evaluate(js_code)

        if result:
            # 提取 slug
            match = result.split('/posts/')[1].split('?')[0].split('#')[0]
            print(f"      ✅ 找到 slug: {match}")
            return match

        print(f"      ⚠️  未找到，使用名称生成 slug")
        # 回退方案：从名称生成 slug
        slug = product_name.lower().replace(' ', '-').replace('.', '').replace("'", '')
        return slug

    except Exception as e:
        print(f"      ❌ 查找失败: {e}")
        slug = product_name.lower().replace(' ', '-').replace('.', '').replace("'", '')
        return slug

def main():
    print("=" * 80)
    print("🔍 Product Hunt AI Vision + URL 验证提取")
    print("=" * 80)

    # 使用现有截图
    screenshot_path = "ph_smart_extract.png"
    if not os.path.exists(screenshot_path):
        screenshot_path = "ph_homepage_screenshot.png"

    if not os.path.exists(screenshot_path):
        print(f"❌ 未找到截图文件")
        return 1

    print(f"📸 使用截图: {screenshot_path}")

    # 步骤 1: AI Vision 识别产品
    ai_products = extract_products_with_vision(screenshot_path)

    if not ai_products:
        print("\n❌ AI 未能识别产品")
        return 1

    # 步骤 2: 为每个产品查找真实 slug
    commenter = ProductHuntCommenter()

    try:
        print("\n🌐 启动浏览器查找产品 slug...")
        commenter.setup_browser(headless=True)
        commenter.verify_login()

        products = []

        for i, ai_prod in enumerate(ai_products[:10], 1):
            name = ai_prod.get('name', '')
            tagline = ai_prod.get('tagline', '')

            if not name:
                continue

            print(f"\n📦 处理产品 {i}/{len(ai_products)}: {name}")

            # 查找真实 slug
            slug = find_product_slug(commenter, name)

            products.append({
                'url': f"https://www.producthunt.com/posts/{slug}",
                'name': name,
                'tagline': tagline,
                'category': 'Various',
                'description': tagline,
                'votes': 0
            })

            time.sleep(2)  # 避免请求过快

        commenter.close_browser()

        if not products:
            print("\n❌ 未能提取产品")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "AI Vision + Search Verification",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n" + "=" * 80)
        print(f"✅ 成功保存 {len(products)} 个产品")
        print("=" * 80)
        print("\n📋 产品列表:")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p['name']}")
            print(f"      {p['tagline']}")
            print(f"      {p['url']}")
            print()

        return 0

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        try:
            commenter.close_browser()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
