#!/usr/bin/env python3
"""
自动获取今日 Product Hunt 产品
"""

import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_todays_products():
    """
    获取今日 Product Hunt 产品
    """
    logger.info("=" * 80)
    logger.info("🔍 获取今日 Product Hunt 产品")
    logger.info("=" * 80)

    commenter = ProductHuntCommenter()

    try:
        # 设置浏览器
        logger.info("\n🌐 设置浏览器...")
        commenter.setup_browser(headless=False)

        if not commenter.verify_login():
            logger.error("❌ 登录失败")
            return []

        logger.info("✅ 登录成功")

        # 访问首页
        logger.info("\n🌐 访问 Product Hunt 首页...")
        commenter.page.goto("https://www.producthunt.com", timeout=60000)
        time.sleep(5)

        # 截图
        commenter.take_screenshot("homepage")

        # 查找今日产品
        logger.info("\n🔍 查找今日产品...")

        # 尝试多种选择器
        products = []

        # 方法1: 查找产品卡片
        try:
            # Product Hunt 的产品通常在列表中
            product_links = commenter.page.query_selector_all('a[href*="/posts/"]')
            logger.info(f"   找到 {len(product_links)} 个产品链接")

            seen_urls = set()
            for link in product_links[:20]:  # 只取前20个
                try:
                    href = link.get_attribute('href')
                    if href and '/posts/' in href and href not in seen_urls:
                        # 构造完整 URL
                        if href.startswith('/'):
                            full_url = f"https://www.producthunt.com{href}"
                        else:
                            full_url = href

                        # 移除查询参数
                        full_url = full_url.split('?')[0]

                        if full_url not in seen_urls:
                            seen_urls.add(full_url)

                            # 尝试获取产品名称
                            try:
                                # 查找父元素中的标题
                                parent = link.evaluate_handle("el => el.closest('[data-test*=\"post\"], article, div[class*=\"item\"]')")
                                if parent:
                                    title_elem = parent.as_element().query_selector('h2, h3, strong, [class*="title"]')
                                    if title_elem:
                                        name = title_elem.inner_text().strip()
                                    else:
                                        name = link.inner_text().strip()
                                else:
                                    name = link.inner_text().strip()
                            except:
                                name = full_url.split('/posts/')[-1].replace('-', ' ').title()

                            if name and len(name) > 2:
                                products.append({
                                    'url': full_url,
                                    'name': name,
                                    'tagline': 'Discovered from Product Hunt homepage',
                                    'category': 'Various',
                                    'description': f'Product from Product Hunt'
                                })
                                logger.info(f"   ✅ {len(products)}. {name}")
                                logger.info(f"      URL: {full_url}")

                            if len(products) >= 10:
                                break
                except Exception as e:
                    continue

        except Exception as e:
            logger.error(f"❌ 查找产品失败: {str(e)}")

        # 如果没找到产品，尝试其他方法
        if len(products) == 0:
            logger.warning("⚠️  未找到产品，尝试备用方法...")

            # 手动记录当前页面的产品
            logger.info("\n📸 请查看浏览器截图，手动记录产品 URL")
            logger.info("   浏览器将保持打开 30 秒...")
            time.sleep(30)

        # 保存结果
        if products:
            logger.info(f"\n✅ 找到 {len(products)} 个产品")

            # 保存到文件
            output_file = "todays_producthunt_products.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ 已保存到: {output_file}")

            # 显示产品列表
            logger.info("\n📋 产品列表:")
            for i, p in enumerate(products, 1):
                logger.info(f"   {i}. {p['name']}")
                logger.info(f"      {p['url']}")
        else:
            logger.warning("\n⚠️  未找到任何产品")
            logger.info("   请手动访问 https://www.producthunt.com")
            logger.info("   并记录今日产品 URL")

        # 关闭浏览器
        commenter.close_browser()

        return products

    except Exception as e:
        logger.error(f"❌ 获取失败: {str(e)}")
        import traceback
        traceback.print_exc()

        try:
            commenter.close_browser()
        except:
            pass

        return []


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 今日产品获取工具                                 ║
╚════════════════════════════════════════════════════════════════╝

功能:
  • 自动访问 Product Hunt 首页
  • 提取今日产品列表
  • 保存到 JSON 文件

准备开始...
""")

    input("按 Enter 开始获取...")

    products = fetch_todays_products()

    if products:
        print(f"\n✅ 成功获取 {len(products)} 个产品")
        print("\n下一步:")
        print("  1. 查看 todays_producthunt_products.json")
        print("  2. 选择 3-5 个相关产品")
        print("  3. 更新 producthunt_account_warmup.py")
        print("  4. 运行 python3 producthunt_account_warmup.py")
    else:
        print("\n⚠️  自动获取失败")
        print("\n手动方法:")
        print("  1. 访问 https://www.producthunt.com")
        print("  2. 记录今日产品 URL")
        print("  3. 手动更新 producthunt_account_warmup.py")
