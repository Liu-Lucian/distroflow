#!/usr/bin/env python3
"""
从 Product Hunt SSR JSON 数据中提取产品
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
import re
from datetime import datetime

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def extract_products_using_js(commenter: ProductHuntCommenter) -> list:
    """使用浏览器 JavaScript 直接提取产品数据"""
    print("\n🔍 使用 JavaScript 提取产品...")

    try:
        # 使用 JavaScript 在浏览器中直接访问 Apollo 数据
        js_code = """
        () => {
            // 访问 Apollo SSR 数据
            const apolloData = window[Symbol.for("ApolloSSRDataTransport")];
            if (!apolloData) {
                return { success: false, error: "Apollo data not found" };
            }

            // 递归查找所有 Post 类型的对象
            const findPosts = (obj, depth = 0) => {
                if (depth > 15) return [];

                const posts = [];

                if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                    // 检查是否是 Post 对象
                    if (obj.__typename === 'Post' && obj.name && obj.slug) {
                        posts.push({
                            name: obj.name,
                            slug: obj.slug,
                            tagline: obj.tagline || '',
                            votesCount: obj.votesCount || obj.latestScore || 0,
                            id: obj.id
                        });
                    }

                    // 递归检查所有属性
                    for (const key in obj) {
                        if (obj.hasOwnProperty(key)) {
                            posts.push(...findPosts(obj[key], depth + 1));
                        }
                    }
                } else if (Array.isArray(obj)) {
                    for (const item of obj) {
                        posts.push(...findPosts(item, depth + 1));
                    }
                }

                return posts;
            };

            // apolloData 可能是数组或单个对象
            const products = Array.isArray(apolloData)
                ? apolloData.flatMap(entry => findPosts(entry))
                : findPosts(apolloData);

            // 去重（基于 slug）
            const uniqueProducts = [];
            const seen = new Set();

            for (const p of products) {
                if (!seen.has(p.slug)) {
                    seen.add(p.slug);
                    uniqueProducts.push(p);
                }
            }

            return { success: true, products: uniqueProducts };
        }
        """

        result = commenter.page.evaluate(js_code)

        if not result.get('success'):
            print(f"   ❌ JavaScript 提取失败: {result.get('error', 'Unknown error')}")
            return []

        raw_products = result.get('products', [])
        print(f"   ✅ JavaScript 提取到 {len(raw_products)} 个产品")

        # 转换为标准格式
        products = []
        for p in raw_products:
            name = p.get('name', '')
            slug = p.get('slug', '')
            tagline = p.get('tagline', '')

            if not name or not slug:
                continue

            products.append({
                'url': f"https://www.producthunt.com/posts/{slug}",
                'name': name,
                'tagline': tagline,
                'category': 'Various',
                'description': tagline,
                'votes': p.get('votesCount', 0)
            })

        print(f"   ✅ 格式化 {len(products)} 个产品")
        return products

    except Exception as e:
        print(f"   ❌ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=" * 80)
    print("🔍 Product Hunt JavaScript 提取")
    print("=" * 80)

    commenter = ProductHuntCommenter()

    try:
        # 访问首页
        print("\n🌐 访问 Product Hunt 首页...")
        commenter.setup_browser(headless=True)

        if not commenter.verify_login():
            print("❌ 登录失败")
            return 1

        commenter.page.goto("https://www.producthunt.com", timeout=60000)
        print("⏳ 等待页面加载...")
        time.sleep(10)

        # 使用 JavaScript 直接提取产品
        products = extract_products_using_js(commenter)

        commenter.close_browser()

        if not products:
            print("\n❌ 未能提取产品")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "SSR JSON Data Extraction",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 成功保存 {len(products)} 个产品")
        print("\n📋 产品列表:")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p['name']} ({p['votes']} votes)")
            print(f"      {p['tagline']}")
            print(f"      {p['url']}")

        print("\n" + "=" * 80)
        print("✅ JavaScript 提取完成！")
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
