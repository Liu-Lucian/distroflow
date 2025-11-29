#!/usr/bin/env python3
"""
Product Hunt AI 自愈合更新系统
当遇到问题时自动使用 AI 寻求解决方案
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

def ai_analyze_page_and_extract(screenshot_path: str, page_html: str) -> list:
    """使用 AI 分析页面并提取产品信息和真实链接"""
    print("\n🤖 AI 分析页面...")

    # 读取截图
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # 从 HTML 中提取所有可能的产品链接
    import re
    all_links = re.findall(r'/posts/([a-zA-Z0-9-]+)', page_html)
    unique_slugs = list(set([slug for slug in all_links if slug not in ['new', 'all']]))[:30]

    prompt = f"""你是 Product Hunt 专家。分析这张 Product Hunt 首页截图。

**任务**:
1. 识别页面上的所有产品（从上到下）
2. 对于每个产品，提取：
   - 产品名称（准确识别）
   - 产品描述/标语
   - 产品类别

**页面上找到的 URL slugs**:
{', '.join(unique_slugs[:15])}

**要求**:
1. 识别 5-10 个产品
2. 对于每个产品，从上面的 slugs 列表中选择**最匹配的 slug**
3. 如果无法确定匹配，根据产品名称生成合理的 slug（小写，用连字符）
4. **按照页面显示顺序排列**

**输出格式**（纯 JSON，无其他文字）:
```json
[
  {{
    "name": "产品名称",
    "slug": "最匹配的-slug-或-生成的-slug",
    "tagline": "产品描述",
    "category": "类别",
    "confidence": "high/medium/low"
  }}
]
```

**匹配规则**:
- high: 产品名在 slugs 中找到精确或非常接近的匹配
- medium: 有可能的匹配但不确定
- low: 只能猜测

开始分析："""

    try:
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
            max_tokens=2000,
            temperature=0.3
        )

        ai_output = response.choices[0].message.content.strip()
        print(f"📋 AI 分析结果:\n{ai_output[:500]}...\n")

        # 提取 JSON
        if "```json" in ai_output:
            ai_output = ai_output.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_output:
            ai_output = ai_output.split("```")[1].split("```")[0].strip()

        products_data = json.loads(ai_output)

        # 转换为标准格式
        products = []
        for item in products_data[:10]:
            slug = item.get('slug', item.get('name', '').lower().replace(' ', '-').replace('.', ''))
            confidence = item.get('confidence', 'medium')

            products.append({
                'url': f"https://www.producthunt.com/posts/{slug}",
                'name': item.get('name', 'Product'),
                'tagline': item.get('tagline', 'Product from Product Hunt'),
                'category': item.get('category', 'Various'),
                'description': item.get('tagline', 'Product from Product Hunt'),
                'confidence': confidence
            })

        print(f"✅ AI 提取 {len(products)} 个产品")
        for p in products[:3]:
            print(f"   • {p['name']} ({p['confidence']}) - {p['url']}")

        return products

    except Exception as e:
        print(f"❌ AI 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def verify_product_url(url: str, commenter: ProductHuntCommenter) -> bool:
    """验证产品 URL 是否有效"""
    try:
        commenter.page.goto(url, timeout=30000, wait_until='domcontentloaded')
        time.sleep(2)

        # 检查是否是 404
        page_text = commenter.page.text_content('body').lower()
        if 'lost this page' in page_text or '404' in page_text or 'not found' in page_text:
            return False

        return True
    except:
        return False

def ai_fix_broken_url(product: dict, screenshot_path: str, page_html: str) -> str:
    """使用 AI 修复损坏的 URL"""
    print(f"\n🔧 AI 自动修复: {product['name']}")

    # 从 HTML 提取候选 slugs
    import re
    all_slugs = re.findall(r'/posts/([a-zA-Z0-9-]+)', page_html)
    unique_slugs = list(set([s for s in all_slugs if s not in ['new', 'all']]))

    # 读取截图
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    prompt = f"""你是 Product Hunt URL 修复专家。

**问题**: 产品 "{product['name']}" 的 URL 无效: {product['url']}

**页面可用的 URL slugs**:
{', '.join(unique_slugs[:20])}

**任务**:
1. 分析截图，找到产品 "{product['name']}"
2. 从上面的 slugs 中选择最匹配的
3. 如果找不到，生成最可能的 slug

**输出格式**（只输出 slug，不要其他文字）:
```
正确的-slug
```

开始分析："""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}
                        }
                    ]
                }
            ],
            max_tokens=100,
            temperature=0.3
        )

        fixed_slug = response.choices[0].message.content.strip().strip('`').strip()
        fixed_url = f"https://www.producthunt.com/posts/{fixed_slug}"

        print(f"   AI 建议: {fixed_url}")
        return fixed_url

    except Exception as e:
        print(f"   ❌ AI 修复失败: {str(e)}")
        return None

def main():
    print("=" * 80)
    print("🤖 Product Hunt AI 自愈合更新系统")
    print("=" * 80)

    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ 错误: 未设置 OPENAI_API_KEY")
        return 1

    commenter = ProductHuntCommenter()

    try:
        # 步骤 1: 访问首页
        print("\n🌐 访问 Product Hunt 首页...")
        commenter.setup_browser(headless=True)

        if not commenter.verify_login():
            print("❌ 登录失败")
            return 1

        commenter.page.goto("https://www.producthunt.com", timeout=60000)
        print("⏳ 等待页面加载...")
        time.sleep(10)

        # 滚动加载
        commenter.page.evaluate("window.scrollTo(0, 1500)")
        time.sleep(3)
        commenter.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # 截图
        screenshot_path = "ph_homepage_screenshot.png"
        commenter.page.screenshot(path=screenshot_path, full_page=False)
        print(f"📸 截图保存: {screenshot_path}")

        # 获取页面 HTML
        page_html = commenter.page.content()

        commenter.close_browser()

        # 步骤 2: AI 分析提取产品
        products = ai_analyze_page_and_extract(screenshot_path, page_html)

        if not products:
            print("❌ AI 未能提取产品")
            return 1

        # 步骤 3: 验证 URL（重新打开浏览器）
        print("\n🔍 验证产品 URL...")
        commenter.setup_browser(headless=True)
        commenter.verify_login()

        verified_products = []
        for i, product in enumerate(products, 1):
            print(f"\n验证 {i}/{len(products)}: {product['name']}")
            print(f"   URL: {product['url']}")

            if verify_product_url(product['url'], commenter):
                print(f"   ✅ URL 有效")
                verified_products.append(product)
            else:
                print(f"   ❌ URL 无效，尝试 AI 修复...")

                # AI 自动修复
                fixed_url = ai_fix_broken_url(product, screenshot_path, page_html)

                if fixed_url and verify_product_url(fixed_url, commenter):
                    print(f"   ✅ 修复成功: {fixed_url}")
                    product['url'] = fixed_url
                    product['ai_fixed'] = True
                    verified_products.append(product)
                else:
                    print(f"   ⚠️  无法修复，跳过此产品")

            # 限制 5 个产品
            if len(verified_products) >= 5:
                break

        commenter.close_browser()

        if not verified_products:
            print("\n❌ 没有有效的产品")
            return 1

        # 步骤 4: 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "AI Self-Healing System",
            "products": verified_products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 成功保存 {len(verified_products)} 个验证的产品")
        print("\n📋 产品列表:")
        for i, p in enumerate(verified_products, 1):
            fixed_mark = " [AI修复]" if p.get('ai_fixed') else ""
            print(f"   {i}. {p['name']}{fixed_mark}")
            print(f"      {p['url']}")

        print("\n" + "=" * 80)
        print("✅ AI 自愈合更新完成！")
        print("=" * 80)

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
