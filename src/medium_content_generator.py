#!/usr/bin/env python3
"""
Medium AI 内容生成器 - 使用 Claude API 生成技术博客
基于产品介绍.md，每天生成不同角度的深度技术文章
"""

import anthropic
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MediumContentGenerator:
    def __init__(self, api_key: str, product_intro_path: str = "产品介绍.md"):
        """
        初始化内容生成器

        Args:
            api_key: Anthropic API key
            product_intro_path: 产品介绍.md 文件路径
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.product_intro_path = product_intro_path
        self.history_file = "medium_post_history.json"

    def load_product_intro(self) -> str:
        """读取产品介绍文档"""
        try:
            with open(self.product_intro_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"无法读取产品介绍: {str(e)}")
            raise

    def load_history(self) -> List[Dict]:
        """加载历史发布记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.warning(f"无法读取历史记录: {str(e)}")
            return []

    def save_history(self, post_info: Dict):
        """保存发布记录"""
        try:
            history = self.load_history()
            history.append(post_info)

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 历史记录已保存 (共 {len(history)} 篇)")
        except Exception as e:
            logger.error(f"保存历史记录失败: {str(e)}")

    def get_content_angles(self) -> List[Dict]:
        """
        定义不同的内容角度
        每天轮换不同角度，保持内容多样性
        """
        return [
            {
                'angle': 'architecture',
                'name': '技术架构深度解析',
                'focus': '系统架构、技术选型、设计模式、模块化设计',
                'tone': '技术深度，面向工程师'
            },
            {
                'angle': 'performance',
                'name': '性能优化实战',
                'focus': '性能指标、优化策略、成本控制、效率提升',
                'tone': '数据驱动，展示优化成果'
            },
            {
                'angle': 'ai_innovation',
                'name': 'AI 技术创新应用',
                'focus': 'AI 模型应用、Prompt Engineering、语义匹配、智能分析',
                'tone': '前沿技术，创新应用'
            },
            {
                'angle': 'user_value',
                'name': '用户价值与场景',
                'focus': '用户痛点、解决方案、使用场景、价值体现',
                'tone': '以用户为中心，讲故事'
            },
            {
                'angle': 'build_story',
                'name': 'Build in Public 开发故事',
                'focus': '开发过程、技术挑战、解决方案、经验教训',
                'tone': '真实透明，分享经验'
            },
            {
                'angle': 'technical_deep_dive',
                'name': '核心功能技术深挖',
                'focus': '某个核心功能的深度技术实现、算法细节',
                'tone': '极度技术，教程式'
            }
        ]

    def select_today_angle(self) -> Dict:
        """
        选择今天的内容角度
        基于历史记录轮换，避免重复
        """
        history = self.load_history()
        angles = self.get_content_angles()

        # 统计各个角度的使用次数
        angle_counts = {}
        for angle_info in angles:
            angle_counts[angle_info['angle']] = 0

        for post in history:
            angle = post.get('angle', '')
            if angle in angle_counts:
                angle_counts[angle] += 1

        # 选择使用次数最少的角度
        min_count = min(angle_counts.values())
        available_angles = [
            angle_info for angle_info in angles
            if angle_counts[angle_info['angle']] == min_count
        ]

        # 如果有多个，选择第一个（按定义顺序）
        selected = available_angles[0]

        logger.info(f"📐 今日内容角度: {selected['name']} ({selected['angle']})")
        logger.info(f"   角度使用统计: {angle_counts}")

        return selected

    def generate_article(self, angle: Optional[Dict] = None) -> Dict:
        """
        使用 Claude API 生成 Medium 文章

        Args:
            angle: 内容角度（如果为None，自动选择）

        Returns:
            {
                'title': '文章标题',
                'subtitle': '副标题',
                'content': '完整Markdown内容',
                'tags': ['tag1', 'tag2', ...],
                'angle': 'architecture/performance/...',
                'word_count': 字数,
                'generated_at': '生成时间'
            }
        """
        try:
            # 读取产品介绍
            product_intro = self.load_product_intro()

            # 选择内容角度
            if angle is None:
                angle = self.select_today_angle()

            # 读取历史记录，构建改进上下文
            history = self.load_history()
            history_context = ""
            if history:
                recent_posts = history[-3:]  # 最近3篇
                history_context = "\n\n已发布文章历史（用于避免重复和构建改进）:\n"
                for i, post in enumerate(recent_posts, 1):
                    history_context += f"\n第{i}篇:\n"
                    history_context += f"- 标题: {post['title']}\n"
                    history_context += f"- 角度: {post.get('angle', 'unknown')}\n"
                    history_context += f"- 日期: {post.get('generated_at', 'unknown')}\n"

            # 构建 Prompt
            prompt = f"""你是一位资深的技术博客作者，正在为 HireMeAI (即答侠) 产品撰写 Medium 技术博客文章。

# 产品信息
{product_intro}

# 今日内容角度
- 角度: {angle['name']}
- 重点: {angle['focus']}
- 风格: {angle['tone']}

{history_context}

# 要求
1. **文章长度**: 800-1500 字（英文）
2. **格式**: 使用 Markdown 格式
3. **结构**:
   - 引人入胜的标题（不超过60字符）
   - 副标题（可选，不超过100字符）
   - 开头：引入话题，吸引读者
   - 主体：根据今日角度深度展开（使用 ## 和 ### 标题分段）
   - 技术细节：具体数据、代码片段、架构图描述
   - 结尾：总结 + CTA（号召行动）
4. **风格**:
   - {angle['tone']}
   - Build in Public 透明分享风格
   - 数据驱动，展示真实指标
   - 避免空洞的营销语言
5. **必须包含**:
   - 具体的技术实现细节
   - 真实的性能数据和指标
   - 产品网站: https://interviewasssistant.com
   - 联系方式: liu.lucian6@gmail.com
6. **改进要求**:
   - 如果有历史文章，今天的内容应该在某些方面展示"改进"或"新发现"
   - 即使是"吹嘘"，也要有技术深度支撑
7. **标签**: 建议3-5个相关的 Medium 标签

# 输出格式
请按以下格式输出（使用分隔符）:

---TITLE---
文章标题（不超过60字符）

---SUBTITLE---
副标题（可选，不超过100字符）

---CONTENT---
完整的Markdown内容...

---TAGS---
tag1, tag2, tag3, tag4, tag5

开始生成文章:"""

            logger.info("🤖 调用 Claude API 生成内容...")
            logger.info(f"   模型: claude-3-5-sonnet-20241022")
            logger.info(f"   角度: {angle['name']}")

            # 调用 Claude API (Note: Model deprecated but works until Oct 2025)
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 解析响应（使用分隔符格式）
            response_text = message.content[0].text
            logger.info(f"✅ Claude API 响应成功 ({len(response_text)} 字符)")

            import re

            # 使用分隔符提取各个字段
            try:
                # 提取标题
                title_match = re.search(r'---TITLE---\s*(.*?)(?=\n\s*---)', response_text, re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Untitled"

                # 提取副标题
                subtitle_match = re.search(r'---SUBTITLE---\s*(.*?)(?=\n\s*---)', response_text, re.DOTALL)
                subtitle = subtitle_match.group(1).strip() if subtitle_match else ""

                # 提取内容
                content_match = re.search(r'---CONTENT---\s*(.*?)(?=\n\s*---TAGS---|$)', response_text, re.DOTALL)
                content = content_match.group(1).strip() if content_match else ""

                # 提取标签
                tags_match = re.search(r'---TAGS---\s*(.*?)$', response_text, re.DOTALL)
                if tags_match:
                    tags_text = tags_match.group(1).strip()
                    tags = [t.strip() for t in tags_text.split(',') if t.strip()]
                else:
                    tags = []

                article = {
                    'title': title,
                    'subtitle': subtitle,
                    'content': content,
                    'tags': tags[:5]  # Medium 最多5个标签
                }

                logger.info(f"✅ 成功提取内容:")
                logger.info(f"   标题: {title[:50]}...")
                logger.info(f"   内容长度: {len(content)} 字符")
                logger.info(f"   标签: {', '.join(tags)}")

            except Exception as e:
                logger.error(f"解析失败: {str(e)}")
                logger.error(f"响应文本预览:\n{response_text[:800]}")
                raise

            # 添加元数据
            article['angle'] = angle['angle']
            article['angle_name'] = angle['name']
            article['word_count'] = len(article['content'].split())
            article['generated_at'] = datetime.now().isoformat()

            logger.info(f"✅ 文章生成成功:")
            logger.info(f"   标题: {article['title']}")
            logger.info(f"   字数: {article['word_count']} words")
            logger.info(f"   标签: {', '.join(article['tags'])}")

            return article

        except Exception as e:
            logger.error(f"❌ 内容生成失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def generate_and_save(self) -> Dict:
        """
        生成文章并保存到历史记录

        Returns:
            生成的文章内容
        """
        article = self.generate_article()

        # 保存到历史
        self.save_history({
            'title': article['title'],
            'angle': article['angle'],
            'angle_name': article['angle_name'],
            'word_count': article['word_count'],
            'generated_at': article['generated_at'],
            'tags': article['tags']
        })

        return article


if __name__ == "__main__":
    # 测试
    import sys

    logging.basicConfig(level=logging.INFO)

    # 检查 API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ 请设置 ANTHROPIC_API_KEY 环境变量")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    try:
        generator = MediumContentGenerator(api_key)

        print("🎨 开始生成 Medium 文章...\n")

        article = generator.generate_and_save()

        print("\n" + "="*80)
        print("📝 生成的文章:")
        print("="*80)
        print(f"\n标题: {article['title']}")
        if article.get('subtitle'):
            print(f"副标题: {article['subtitle']}")
        print(f"\n标签: {', '.join(article['tags'])}")
        print(f"字数: {article['word_count']} words")
        print(f"角度: {article['angle_name']}")
        print("\n内容预览:")
        print("-"*80)
        print(article['content'][:500] + "...")
        print("-"*80)

        print("\n✅ 文章已生成并保存到历史记录")
        print(f"📁 历史文件: medium_post_history.json")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
