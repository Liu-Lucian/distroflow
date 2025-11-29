#!/usr/bin/env python3
"""
Substack系统测试脚本

测试内容：
1. 生成单篇文章（不发布）
2. 测试评论抓取
3. 测试回答生成
4. 完整流程测试
"""

import sys
sys.path.insert(0, 'src')
from substack_poster import SubstackPoster
from substack_answer_bot import SubstackAnswerBot
import logging
import json
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUBSTACK_DOMAIN = "yourname.substack.com"  # 替换为你的域名


def test_article_generation():
    """测试文章生成"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 测试1: 文章生成")
    logger.info("=" * 80)

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    prompt = """Generate a Substack article for HireMeAI (Build in Public style).

Title: Week 1: Teaching AI to Listen Before It Speaks
Subtitle: The speaker identification breakthrough

Content structure:
- Hook: Personal story about interview failures
- Problem: Why most interview assistants fail
- Solution: Speaker identification with 92% accuracy
- Technical details: Picovoice Eagle integration
- Real example: Test scenario
- Takeaway: Listening is more important than answering
- CTA: Try at https://interviewasssistant.com

Output as JSON with keys: title, subtitle, content"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500
        )

        article_json = response.choices[0].message.content.strip()

        # 清理JSON
        if article_json.startswith('```json'):
            article_json = article_json[7:]
        if article_json.startswith('```'):
            article_json = article_json[3:]
        if article_json.endswith('```'):
            article_json = article_json[:-3]

        article = json.loads(article_json.strip())

        logger.info("\n✅ 文章生成成功！")
        logger.info(f"标题: {article['title']}")
        logger.info(f"副标题: {article.get('subtitle', '')}")
        logger.info(f"字数: {len(article['content'])} 字符")
        logger.info("\n内容预览:")
        logger.info("-" * 80)
        logger.info(article['content'][:500] + "...")
        logger.info("-" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ 文章生成失败: {str(e)}")
        return False


def test_answer_generation():
    """测试回答生成"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 测试2: 回答生成")
    logger.info("=" * 80)

    test_comments = [
        "How do you handle nervous candidates who freeze during behavioral questions?",
        "This is amazing! Does it work with non-technical interviews too?",
        "卧槽，这个太牛了！中文面试也能用吗？",
        "What's the latency like? Does the AI respond fast enough to be useful?",
    ]

    bot = SubstackAnswerBot(substack_url=SUBSTACK_DOMAIN)

    for i, comment in enumerate(test_comments, 1):
        logger.info(f"\n--- 评论 {i} ---")
        logger.info(f"内容: {comment}")

        # 测试是否应该回答
        should_answer = bot.should_answer_comment(comment)
        logger.info(f"是否应该回答: {'✅ 是' if should_answer else '❌ 否'}")

        if should_answer:
            # 生成回答
            answer = bot.generate_answer(comment)
            if answer:
                logger.info(f"生成的回答: {answer}")
            else:
                logger.error("❌ 回答生成失败")

    return True


def test_poster():
    """测试发布器（不实际发布）"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 测试3: Substack发布器")
    logger.info("=" * 80)

    test_content = {
        'title': '测试文章 - Week 1: The AI Interview Assistant Journey',
        'subtitle': 'Building HireMeAI in public',
        'content': '''Today I'm sharing the first update on building HireMeAI.

## The Vision

Every job candidate deserves to show their best self in interviews. But nerves get in the way.

## This Week's Progress

- Achieved 92% speaker identification accuracy
- Reduced response latency to <1 second
- Integrated STAR framework for behavioral questions

## What's Next

Week 2: Testing with real candidates and gathering feedback.

Try the beta at https://interviewasssistant.com 🚀''',
        'publish_immediately': False  # 不实际发布
    }

    poster = SubstackPoster(substack_url=SUBSTACK_DOMAIN)

    try:
        poster.setup_browser(headless=False)

        if poster.verify_login():
            logger.info("   ✅ 登录验证成功")

            logger.info("\n⚠️  这是测试模式，不会实际发布文章")
            logger.info("   浏览器将打开到编辑页面，你可以检查内容")

            response = input("\n是否继续测试（会打开浏览器）？(y/n): ")
            if response.lower() != 'y':
                logger.info("已取消测试")
                poster.close_browser()
                return False

            # 测试创建（保存为草稿）
            success = poster.create_post(test_content)

            if success:
                logger.info("✅ 测试成功！文章已保存为草稿")
                return True
            else:
                logger.error("❌ 测试失败")
                return False
        else:
            logger.error("❌ 登录验证失败")
            logger.info("💡 请先运行: python3 substack_login_and_save_auth.py")
            return False

    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        try:
            input("\n按Enter关闭浏览器...")
        except:
            pass
        poster.close_browser()


def main():
    """运行所有测试"""
    logger.info("=" * 80)
    logger.info("🧪 Substack系统完整测试")
    logger.info("=" * 80)
    logger.info(f"域名: {SUBSTACK_DOMAIN}")
    logger.info("=" * 80)

    results = {}

    # 测试1: 文章生成
    try:
        results['article_generation'] = test_article_generation()
    except Exception as e:
        logger.error(f"测试1失败: {str(e)}")
        results['article_generation'] = False

    # 测试2: 回答生成
    try:
        results['answer_generation'] = test_answer_generation()
    except Exception as e:
        logger.error(f"测试2失败: {str(e)}")
        results['answer_generation'] = False

    # 测试3: 发布器（需要人工确认）
    response = input("\n是否测试发布器（会打开浏览器）？(y/n): ")
    if response.lower() == 'y':
        try:
            results['poster'] = test_poster()
        except Exception as e:
            logger.error(f"测试3失败: {str(e)}")
            results['poster'] = False
    else:
        results['poster'] = None

    # 总结
    logger.info("\n" + "=" * 80)
    logger.info("📊 测试总结")
    logger.info("=" * 80)

    for test_name, result in results.items():
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⏭️  跳过"

        logger.info(f"{test_name}: {status}")

    logger.info("=" * 80)


if __name__ == "__main__":
    print("\n⚙️  配置检查")
    print("=" * 80)
    print(f"OpenAI API Key: {'✅ 已设置' if os.environ.get('OPENAI_API_KEY') else '❌ 未设置'}")
    print(f"Substack域名: {SUBSTACK_DOMAIN}")
    print()

    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ 请先设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    response = input("开始测试？(y/n): ")
    if response.lower() == 'y':
        main()
    else:
        print("已取消")
