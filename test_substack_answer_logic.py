#!/usr/bin/env python3
"""
Substack回答系统逻辑测试 - 纯本地测试，无需浏览器

功能：
1. 测试评论过滤逻辑（should_answer_comment）
2. 测试AI回答生成（generate_answer）
3. 交互式测试模式（输入评论，看AI如何回答）
4. 批量测试多种评论类型

无需登录，无需浏览器，纯本地测试AI逻辑
"""

import os
from openai import OpenAI
import logging
from typing import List, Dict
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


class SubstackAnswerTester:
    """Substack回答逻辑测试器"""

    def __init__(self):
        self.test_results = []

    def should_answer_comment(self, comment_text: str) -> bool:
        """
        判断是否应该回答这条评论（与substack_answer_bot.py相同逻辑）
        """
        comment_lower = comment_text.lower()

        # 太短的评论不回答
        if len(comment_text) < 10:
            return False

        # 检查是否包含问题词
        question_keywords = ['?', '？', 'how', 'why', 'what', 'when', 'where', 'who',
                           'can', 'could', 'would', 'should', '如何', '怎么', '为什么',
                           '什么', '哪里', '谁', '能不能', '可以']

        has_question = any(keyword in comment_lower for keyword in question_keywords)

        # 检查是否包含相关主题
        relevant_topics = ['interview', 'job', 'career', 'ai', 'resume', 'cv',
                          'hiring', 'recruiter', '面试', '工作', '职业', '简历',
                          '求职', 'tech', 'coding', 'programming', '技术']

        is_relevant = any(topic in comment_lower for topic in relevant_topics)

        # 问题 OR 相关主题都可以回答
        return has_question or is_relevant

    def generate_answer(self, comment_text: str, context: str = "") -> str:
        """
        Generate answer (same logic as substack_answer_bot.py)
        """
        product_context = """
You are the founder of HireMeAI (https://interviewasssistant.com), an AI-powered real-time interview assistant.

Product core features:
- Voice recognition (95%+ accuracy)
- Speaker identification (92% accuracy)
- Real-time AI answer generation (<1s latency)
- STAR framework interview optimization

Your response style requirements:
✅ Warm, concise, practical
✅ Use casual internet language naturally (e.g., "damn", "ngl", "tbh", "lowkey", "fr")
✅ Answer seemingly "unrelated" but relevant questions (interview tips, AI applications, career advice)
✅ Don't be overly enthusiastic, don't hard-sell the product
✅ If very relevant, you can naturally mention HireMeAI, but it's not required

❌ Avoid:
- Long-winded responses
- Overly formal tone
- Direct product pitches
- Excessive praise or enthusiasm
"""

        prompt = f"""{product_context}

Article context:
{context if context else "No specific context"}

Comment:
{comment_text}

Generate a brief, valuable response in ENGLISH (50-150 words):
- Directly answer the core question
- Share practical insights or experience
- Natural, warm but not over-the-top tone
- Use casual internet language appropriately
- If highly relevant, casually mention HireMeAI (https://interviewasssistant.com), but don't force it

Output ONLY the response text in ENGLISH, no additional explanation:"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )

            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            logger.error(f"❌ 生成回答失败: {str(e)}")
            return None

    def test_single_comment(self, comment: str, context: str = "", show_details: bool = True):
        """
        测试单条评论

        Args:
            comment: 评论内容
            context: 文章上下文（可选）
            show_details: 是否显示详细信息
        """
        if show_details:
            logger.info("\n" + "="*80)
            logger.info("📝 评论:")
            logger.info(f"   {comment}")
            logger.info("-"*80)

        # 步骤1: 判断是否应该回答
        should_answer = self.should_answer_comment(comment)

        if show_details:
            logger.info(f"🤔 是否应该回答: {'✅ 是' if should_answer else '❌ 否'}")

        if not should_answer:
            if show_details:
                logger.info("   ℹ️  跳过原因: 不符合回答条件（太短/不相关/无问题）")
            return {
                'comment': comment,
                'should_answer': False,
                'answer': None,
                'reason': '不符合回答条件'
            }

        # 步骤2: 生成回答
        if show_details:
            logger.info("🤖 正在生成AI回答...")

        answer = self.generate_answer(comment, context)

        if show_details:
            logger.info("-"*80)
            if answer:
                logger.info("💬 生成的回答:")
                logger.info(f"   {answer}")
                logger.info(f"   （字数: {len(answer)} 字符）")
            else:
                logger.info("❌ 回答生成失败")
            logger.info("="*80)

        result = {
            'comment': comment,
            'should_answer': True,
            'answer': answer,
            'char_count': len(answer) if answer else 0
        }

        self.test_results.append(result)
        return result

    def batch_test_comments(self, test_cases: List[Dict]):
        """
        批量测试多条评论

        Args:
            test_cases: 测试用例列表 [{'comment': '...', 'context': '...', 'expect_answer': True/False}, ...]
        """
        logger.info("\n" + "="*80)
        logger.info("🧪 批量测试模式")
        logger.info("="*80)
        logger.info(f"总共 {len(test_cases)} 个测试用例\n")

        passed = 0
        failed = 0

        for i, case in enumerate(test_cases, 1):
            comment = case['comment']
            context = case.get('context', '')
            expect_answer = case.get('expect_answer', True)

            logger.info(f"\n--- 测试 {i}/{len(test_cases)} ---")
            logger.info(f"评论: {comment[:60]}...")
            logger.info(f"预期: {'应该回答' if expect_answer else '应该跳过'}")

            result = self.test_single_comment(comment, context, show_details=False)

            # 验证结果
            if result['should_answer'] == expect_answer:
                logger.info(f"✅ 通过")
                if result['should_answer'] and result['answer']:
                    logger.info(f"   回答: {result['answer'][:80]}...")
                passed += 1
            else:
                logger.info(f"❌ 失败（预期{expect_answer}，实际{result['should_answer']}）")
                failed += 1

        # 总结
        logger.info("\n" + "="*80)
        logger.info("📊 测试总结")
        logger.info("="*80)
        logger.info(f"✅ 通过: {passed}/{len(test_cases)}")
        logger.info(f"❌ 失败: {failed}/{len(test_cases)}")
        logger.info(f"通过率: {passed/len(test_cases)*100:.1f}%")
        logger.info("="*80)

    def interactive_test(self):
        """
        交互式测试模式 - 手动输入评论，实时看AI回答
        """
        logger.info("\n" + "="*80)
        logger.info("🎮 交互式测试模式")
        logger.info("="*80)
        logger.info("输入评论，按Enter查看AI回答")
        logger.info("输入 'quit' 或 'exit' 退出")
        logger.info("输入 'examples' 查看示例评论")
        logger.info("="*80 + "\n")

        while True:
            try:
                comment = input("💬 评论内容: ").strip()

                if not comment:
                    continue

                if comment.lower() in ['quit', 'exit', 'q']:
                    logger.info("\n👋 退出交互模式")
                    break

                if comment.lower() == 'examples':
                    self._show_example_comments()
                    continue

                # 测试评论
                self.test_single_comment(comment)

            except KeyboardInterrupt:
                logger.info("\n\n👋 退出交互模式")
                break
            except EOFError:
                break

    def _show_example_comments(self):
        """显示示例评论"""
        logger.info("\n" + "="*80)
        logger.info("📋 示例评论（复制粘贴测试）")
        logger.info("="*80)

        examples = [
            "How do you handle nervous candidates during interviews?",
            "This is amazing! Does it work for non-tech interviews?",
            "Damn, this is impressive! How did you get 92% accuracy on speaker ID?",
            "What's the latency? I need real-time responses.",
            "Great article!",  # Should skip
            "Thanks for sharing",  # Should skip
            "Ngl, I've failed 10+ behavioral interviews. Does the STAR framework really help?",
            "Can AI really understand behavioral interview questions?",
            "Are you using GPT-4 or did you train your own model?",
            "I tried it and the latency felt high. How did you optimize it?"
        ]

        for i, example in enumerate(examples, 1):
            logger.info(f"{i}. {example}")

        logger.info("="*80 + "\n")


def run_preset_tests():
    """运行预设测试用例"""
    logger.info("\n" + "🎯"*20)
    logger.info("Substack 回答系统逻辑测试")
    logger.info("🎯"*20 + "\n")

    tester = SubstackAnswerTester()

    # 定义测试用例
    test_cases = [
        # 应该回答的评论（包含问题）
        {
            'comment': 'How do you handle nervous candidates who freeze during behavioral questions?',
            'expect_answer': True
        },
        {
            'comment': 'What\'s the latency like? Does the AI respond fast enough to be useful in real interviews?',
            'expect_answer': True
        },
        {
            'comment': 'Damn, this is impressive! Does it work for technical interviews too?',
            'expect_answer': True
        },
        {
            'comment': 'What do you do when you get nervous during interviews? Any good tips?',
            'expect_answer': True
        },

        # Should answer (contains relevant topics)
        {
            'comment': 'I struggle with behavioral interviews. This could be a game changer for job seekers.',
            'expect_answer': True
        },
        {
            'comment': 'As a recruiter, I\'m curious how AI is changing the interview preparation landscape.',
            'expect_answer': True
        },
        {
            'comment': 'Currently prepping for tech interviews and feeling so stressed tbh',
            'expect_answer': True
        },

        # 应该跳过的评论（太短）
        {
            'comment': 'Great!',
            'expect_answer': False
        },
        {
            'comment': 'Thanks',
            'expect_answer': False
        },

        # 应该跳过的评论（不相关）
        {
            'comment': 'I love pizza! What\'s your favorite food?',
            'expect_answer': False
        },
        {
            'comment': 'Nice weather today, isn\'t it?',
            'expect_answer': False
        },

        # 边界情况
        {
            'comment': 'Interesting article, but not sure if AI can really help with interviews.',
            'expect_answer': True  # 包含"interview"
        },
        {
            'comment': 'This is really well written! Keep up the good work building in public.',
            'expect_answer': False  # 纯赞美，无问题
        },
    ]

    # 运行批量测试
    logger.info("=" * 80)
    logger.info("第一部分：批量测试（验证过滤逻辑）")
    logger.info("=" * 80)
    tester.batch_test_comments(test_cases)

    # 运行详细测试（展示AI回答）
    logger.info("\n\n" + "=" * 80)
    logger.info("第二部分：详细测试（查看AI生成的回答）")
    logger.info("=" * 80)
    logger.info("以下是AI为真实评论生成的回答示例：\n")

    detailed_test_cases = [
        {
            'comment': 'How do you handle the latency issue? 1 second seems fast but is it fast enough for live interviews?',
            'context': 'Article about achieving <1s response time in HireMeAI'
        },
        {
            'comment': 'Damn, how did you get 92% accuracy on speaker ID? I tried a few voice recognition tools and they were terrible.',
            'context': 'Article about speaker identification breakthrough'
        },
        {
            'comment': 'As someone who has failed 10+ behavioral interviews, I wish I had this earlier. Does it help with the "Tell me about yourself" question?',
            'context': 'Article about common interview mistakes'
        },
        {
            'comment': 'I\'m a recruiter and honestly this is both exciting and scary. How do you ensure candidates use it ethically?',
            'context': 'Article about AI in interviews'
        },
    ]

    for case in detailed_test_cases:
        tester.test_single_comment(case['comment'], case.get('context', ''))

    # 保存测试结果
    with open('substack_answer_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)

    logger.info(f"\n💾 测试结果已保存到: substack_answer_test_results.json")

    return tester


def main():
    """主函数"""
    import sys

    logger.info("\n请选择测试模式：")
    logger.info("1. 运行预设测试用例（推荐）")
    logger.info("2. 交互式测试模式（手动输入评论）")
    logger.info("3. 运行全部测试")

    try:
        choice = input("\n选择 (1/2/3): ").strip()
    except (EOFError, KeyboardInterrupt):
        logger.info("\n已取消")
        return

    tester = SubstackAnswerTester()

    if choice == '1':
        run_preset_tests()

    elif choice == '2':
        tester.interactive_test()

    elif choice == '3':
        run_preset_tests()
        logger.info("\n\n")
        response = input("是否继续进入交互式测试？(y/n): ")
        if response.lower() == 'y':
            tester.interactive_test()

    else:
        logger.info("❌ 无效选择")


if __name__ == "__main__":
    # 检查API Key
    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("\n❌ 错误: 未设置 OPENAI_API_KEY 环境变量")
        logger.error("请运行: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    logger.info("✅ OpenAI API Key 已设置")

    main()
