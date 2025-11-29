#!/usr/bin/env python3
"""
Product Hunt 产品列表 - 每日自动 AI 更新
使用 GPT-4o Vision 自动识别首页产品并更新列表
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
import base64
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def capture_producthunt_homepage() -> tuple:
    """截图 Product Hunt 首页并提取真实产品链接"""
    print("🌐 访问 Product Hunt 首页...")

    commenter = ProductHuntCommenter()
    commenter.setup_browser(headless=True)

    if not commenter.verify_login():
        print("❌ 登录失败")
        commenter.close_browser()
        return None, []

    # 访问首页
    commenter.page.goto("https://www.producthunt.com", timeout=60000)
    print("⏳ 等待页面加载...")
    time.sleep(10)

    # 滚动以加载更多产品
    commenter.page.evaluate("window.scrollTo(0, 1500)")
    time.sleep(3)
    commenter.page.evaluate("window.scrollTo(0, 0)")
    time.sleep(2)

    # 提取真实的产品链接
    print("🔗 提取产品链接...")
    real_links = []
    try:
        all_links = commenter.page.query_selector_all('a')
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/posts/' in href:
                # 跳过特殊链接
                if any(skip in href for skip in ['/posts/new', '/posts/all', '/posts?', '/posts#']):
                    continue

                # 构造完整 URL
                if href.startswith('/'):
                    full_url = f"https://www.producthunt.com{href}"
                else:
                    full_url = href

                # 清理 URL
                full_url = full_url.split('?')[0].split('#')[0]

                # 验证是否是有效的产品 URL
                if full_url.endswith('/posts/') or full_url.endswith('/posts'):
                    continue

                if full_url not in real_links:
                    real_links.append(full_url)

        print(f"   找到 {len(real_links)} 个真实产品链接")
    except Exception as e:
        print(f"   ⚠️  提取链接失败: {str(e)}")

    # 截图
    screenshot_path = "ph_homepage_screenshot.png"
    commenter.page.screenshot(path=screenshot_path, full_page=False)
    print(f"📸 截图已保存: {screenshot_path}")

    commenter.close_browser()
    return screenshot_path, real_links

def extract_products_with_ai(screenshot_path: str, real_links: list) -> list:
    """使用 AI Vision 提取产品信息"""
    print("\n🤖 使用 AI Vision 分析截图...")

    # 读取截图并转换为 base64
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    prompt = """分析这张 Product Hunt 首页截图，提取所有可见的产品信息。

**任务**:
1. 识别页面上所有今日产品（从上到下顺序）
2. 对于每个产品，提取：
   - 产品名称
   - 产品简介/标语（tagline）
   - 产品类别/标签（如果可见）
3. 选择 5-10 个最相关的产品（优先 AI Tools, Productivity, Developer Tools）
4. **按照页面上的显示顺序排列**

**输出格式** (严格的 JSON 数组，不要其他文本):
```json
[
  {
    "name": "产品名称",
    "tagline": "产品简介",
    "category": "产品类别"
  }
]
```

**注意**:
- 只输出 JSON 数组，不要任何解释文字
- 不需要生成 slug 或 URL，我们会自动匹配
- 如果看不清某些信息，用合理的值
- 至少提取 5 个产品，最多 10 个
- **重要**: 按照页面从上到下的顺序排列产品

开始分析："""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # 使用 Vision 模型
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
            max_tokens=1500,
            temperature=0.3
        )

        ai_output = response.choices[0].message.content.strip()
        print(f"\n📋 AI 识别结果:\n{ai_output}\n")

        # 提取 JSON（可能被包裹在 ```json ``` 中）
        if "```json" in ai_output:
            ai_output = ai_output.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_output:
            ai_output = ai_output.split("```")[1].split("```")[0].strip()

        products_data = json.loads(ai_output)

        # 如果没有真实链接，从产品名生成 slug
        if not real_links or len(real_links) == 0:
            print("   ⚠️  使用 AI 识别的产品名生成 URL")
            products = []
            for item in products_data[:10]:
                name = item.get('name', 'Product')
                slug = name.lower().replace(' ', '-').replace('.', '')
                products.append({
                    'url': f"https://www.producthunt.com/posts/{slug}",
                    'name': name,
                    'tagline': item.get('tagline', 'Product from Product Hunt'),
                    'category': item.get('category', 'Various'),
                    'description': item.get('tagline', 'Product from Product Hunt')
                })
            print(f"✅ 成功提取 {len(products)} 个产品（AI 生成 URL）")
            return products

        # 使用真实链接匹配 AI 识别的产品
        products = []
        num_products = min(len(products_data), len(real_links), 10)

        for i in range(num_products):
            item = products_data[i] if i < len(products_data) else {}
            url = real_links[i] if i < len(real_links) else f"https://www.producthunt.com/posts/product-{i}"

            products.append({
                'url': url,  # 使用真实链接
                'name': item.get('name', 'Product'),
                'tagline': item.get('tagline', 'Product from Product Hunt'),
                'category': item.get('category', 'Various'),
                'description': item.get('tagline', 'Product from Product Hunt')
            })

        print(f"✅ 成功提取 {len(products)} 个产品（使用真实链接）")
        return products

    except json.JSONDecodeError as e:
        print(f"❌ AI 返回的 JSON 格式错误: {e}")
        print(f"原始输出: {ai_output}")
        # 如果 AI 失败但有真实链接，直接使用真实链接
        if real_links:
            print("⚠️  使用真实链接作为备用方案...")
            return create_products_from_links(real_links[:10])
        return []
    except Exception as e:
        print(f"❌ AI 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        # 如果 AI 失败但有真实链接，直接使用真实链接
        if real_links:
            print("⚠️  使用真实链接作为备用方案...")
            return create_products_from_links(real_links[:10])
        return []

def create_products_from_links(links: list) -> list:
    """从链接创建产品列表（备用方案）"""
    products = []
    for url in links[:10]:
        try:
            # 从 URL 提取产品名
            slug = url.split('/posts/')[-1].strip('/')
            name = slug.replace('-', ' ').title()

            products.append({
                'url': url,
                'name': name,
                'tagline': f'{name} - Product from Product Hunt',
                'category': 'Various',
                'description': f'Product discovered from Product Hunt'
            })
        except:
            continue

    return products

def save_product_list(products: list):
    """保存产品列表到文件"""
    data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "source": "Auto-updated via AI Vision",
        "products": products,
        "updated_at": datetime.now().isoformat()
    }

    with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 产品列表已保存到: {PRODUCT_LIST_FILE}")
    print(f"   包含 {len(products)} 个产品")

def main():
    print("=" * 80)
    print("🤖 Product Hunt 产品列表 - 每日自动 AI 更新")
    print("=" * 80)

    # 检查 API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ 错误: 未设置 OPENAI_API_KEY")
        print("   export OPENAI_API_KEY='sk-proj-...'")
        return 1

    # 步骤 1: 截图首页并提取真实链接
    screenshot_path, real_links = capture_producthunt_homepage()
    if not screenshot_path:
        print("❌ 截图失败")
        return 1

    if not real_links:
        print("⚠️  警告: 未找到产品链接，将依赖 AI 猜测")

    # 步骤 2: AI 提取产品信息并匹配真实链接
    products = extract_products_with_ai(screenshot_path, real_links)
    if not products:
        print("❌ AI 未能提取到产品")
        return 1

    # 步骤 3: 保存列表
    save_product_list(products)

    # 显示产品预览
    print("\n📋 产品列表预览:")
    for i, p in enumerate(products, 1):
        print(f"   {i}. {p['name']}")
        print(f"      {p['tagline']}")
        print(f"      {p['url']}")

    print("\n" + "=" * 80)
    print("✅ 自动更新完成！")
    print(f"   可以直接运行: python3 auto_producthunt_forever.py")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
