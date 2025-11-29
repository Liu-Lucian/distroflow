#!/usr/bin/env python3
"""
快速测试 Medium 内容生成 - 简化版本
不使用复杂的 JSON，直接返回 Markdown
"""

import sys
sys.path.insert(0, 'src')

from medium_poster import MediumPoster
import anthropic
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 简单测试：手动创建一篇文章
test_content = {
    'title': 'Building HireMeAI: Day 1 - System Architecture',
    'subtitle': 'A technical deep dive into our AI interview assistant',
    'content': '''## Introduction

When building HireMeAI (即答侠), we faced a fundamental challenge: how do you create a real-time AI interview assistant that responds in less than 1 second?

Today, I'll share the technical architecture decisions that power our system.

## The Core Challenge

Real-time interview assistance requires:
- Speech recognition with 95%+ accuracy
- Intelligent speaker identification
- Sub-second response latency
- Context-aware answer generation

## Our Technical Stack

### AI Engine
- **OpenAI GPT-4**: High-quality content generation
- **Azure Speech Services**: Enterprise-grade recognition
- **Picovoice Eagle**: Professional speaker identification
- **ChromaDB**: Vector semantic search

### Performance Optimization
- **Dual-level caching**: Memory + disk persistence
- **Streaming responses**: Server-Sent Events
- **Smart pre-computation**: 80% faster for common questions
- **Batch processing**: Reduced API costs by 70%

## Key Metrics

Our optimizations achieved:
- Embedding generation: 1.459s → 0.3s (80% improvement)
- First response latency: 2.7s → 1.0s (60% improvement)
- Cache hit rate: 90%+ for common questions
- API cost savings: 70%+

## What's Next

Tomorrow I'll dive into the speech recognition pipeline and how we achieved 95%+ accuracy.

---

Building this has been an incredible journey. The key lesson? Performance optimization isn't optional for real-time AI systems - it's essential.

Learn more: https://interviewasssistant.com
Contact: liu.lucian6@gmail.com

#AI #BuildInPublic #TechArchitecture #InterviewPrep #MachineLearning''',
    'tags': ['AI', 'BuildInPublic', 'TechArchitecture', 'InterviewPrep', 'MachineLearning']
}

logger.info("🎨 开始测试 Medium 发布...")
logger.info(f"标题: {test_content['title']}")
logger.info(f"字数: {len(test_content['content'].split())} words")

poster = MediumPoster()

try:
    logger.info("🌐 设置浏览器...")
    poster.setup_browser(headless=False)

    logger.info("🔐 验证登录...")
    if not poster.verify_login():
        logger.error("❌ 登录验证失败，请先运行 medium_login_and_save_auth.py")
        sys.exit(1)

    logger.info("✅ 登录验证成功")

    logger.info("📤 开始发布...")
    success = poster.create_post(test_content)

    if success:
        logger.info("=" * 80)
        logger.info("✅ Medium 文章发布成功！")
        logger.info("=" * 80)
    else:
        logger.error("❌ 发布失败")

except Exception as e:
    logger.error(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    try:
        input("\n按 Enter 关闭浏览器...")
    except EOFError:
        pass
    poster.close_browser()
