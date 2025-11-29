#!/usr/bin/env python3
"""
测试单个产品的评论和点赞
快速验证选择器是否正确
"""

import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import json
import logging
import os
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_test_comment(product_info: dict) -> str:
    """生成测试评论"""
    prompt = f"""You are an enthusiastic tech enthusiast. Write a SHORT, genuine Product Hunt comment about:

Product: {product_info.get('name', 'N/A')}
Tagline: {product_info.get('tagline', 'N/A')}
Category: {product_info.get('category', 'N/A')}

Style:
- Be enthusiastic and genuine
- Use 1-2 internet slang (ngl, tbh, fr, lol)
- 1-2 emoji max (🔥💯🎉)
- Ask a quick question OR share excitement
- Max 200 characters

Output ONLY the comment text in ENGLISH:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=80
    )

    return response.choices[0].message.content.strip().strip('"').strip("'")


def test_single_comment():
    """测试单个产品的完整流程"""
    logger.info("=" * 80)
    logger.info("🧪 测试单个产品评论流程")
    logger.info("=" * 80)

    # 加载今日产品
    try:
        with open('todays_producthunt_products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', [])
    except FileNotFoundError:
        logger.error("❌ 未找到 todays_producthunt_products.json")
        return False

    if not products:
        logger.error("❌ 产品列表为空")
        return False

    # 使用第一个产品
    test_product = products[0]
    logger.info(f"\n测试产品: {test_product['name']}")
    logger.info(f"URL: {test_product['url']}")

    commenter = ProductHuntCommenter()

    try:
        # 设置浏览器
        logger.info("\n🌐 设置浏览器...")
        commenter.setup_browser(headless=False)

        if not commenter.verify_login():
            logger.error("❌ 登录失败")
            return False

        logger.info("✅ 登录成功")

        # 生成评论
        logger.info("\n✍️  生成评论...")
        comment_text = generate_test_comment(test_product)
        logger.info(f"   评论预览: {comment_text}")

        # 访问产品页面
        logger.info(f"\n🌐 访问产品页面...")
        if not commenter.navigate_to_product(test_product['url']):
            logger.error("❌ 导航失败")
            return False

        logger.info("✅ 页面加载成功")

        # 测试点赞
        logger.info("\n👍 测试点赞...")
        upvote_success = commenter.upvote_product()

        if upvote_success:
            logger.info("✅ 点赞成功")
        else:
            logger.warning("⚠️  点赞失败（但继续测试评论）")

        # 测试评论
        logger.info("\n💬 测试评论...")
        comment_success = commenter.post_comment(comment_text)

        if comment_success:
            logger.info("✅ 评论发布成功")
        else:
            logger.error("❌ 评论发布失败")
            return False

        # 最终结果
        logger.info("\n" + "=" * 80)
        if upvote_success and comment_success:
            logger.info("🎉 所有测试通过！")
            logger.info("=" * 80)
            logger.info("\n结果:")
            logger.info("  ✅ 点赞成功")
            logger.info("  ✅ 评论成功")
            logger.info("\n下一步:")
            logger.info("  python3 producthunt_account_warmup.py  # 运行完整养号")
            return True
        elif comment_success:
            logger.info("⚠️  部分成功")
            logger.info("=" * 80)
            logger.info("\n结果:")
            logger.info("  ⚠️  点赞失败")
            logger.info("  ✅ 评论成功")
            logger.info("\n评论功能可用，点赞功能需要检查")
            return True
        else:
            logger.error("❌ 测试失败")
            return False

    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        logger.info("\n⏳ 5秒后关闭浏览器...")
        import time
        time.sleep(5)
        commenter.close_browser()


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 单个评论测试                                     ║
╚════════════════════════════════════════════════════════════════╝

测试内容:
  • 登录验证
  • 访问产品页面
  • 点赞功能
  • 评论发布功能

准备开始...
""")

    input("按 Enter 开始测试...")

    success = test_single_comment()

    if success:
        print("\n✅ 测试成功！可以开始使用 warmup 脚本了")
    else:
        print("\n❌ 测试失败，需要进一步调试")
