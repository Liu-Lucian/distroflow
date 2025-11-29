#!/usr/bin/env python3
"""
简单测试 Medium 发布功能
使用预定义内容快速测试
"""
import sys
sys.path.insert(0, 'src')

from medium_poster import MediumPoster
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试内容
test_content = {
    'title': 'HireMeAI Tech Stack: Building a Real-Time AI Interview Assistant',
    'subtitle': 'Behind the scenes of our sub-second response architecture',
    'content': '''## Introduction

Building HireMeAI (即答侠) required solving a unique challenge: creating an AI interview assistant that responds in real-time with professional-grade answers.

## The Core Challenge

Our users need:
- **Real-time speech recognition** with 95%+ accuracy
- **Intelligent speaker identification** to separate interviewer from candidate
- **Sub-second response latency** for natural conversation flow
- **Context-aware answer generation** based on resume and job description

## Technical Architecture

### AI & NLP Stack
- **OpenAI GPT-4**: High-quality, context-aware answer generation
- **Azure Speech Services**: Enterprise-grade speech-to-text recognition
- **Picovoice Eagle**: Professional speaker identification and diarization
- **ChromaDB**: Vector database for semantic search and matching

### Performance Optimization
We achieved our <1s response time through several key optimizations:

**1. Dual-Level Caching**
- Memory cache for frequently accessed data
- Disk persistence for long-term storage
- 90%+ cache hit rate on common interview questions

**2. Streaming Response Architecture**
- Server-Sent Events (SSE) for real-time updates
- Progressive answer rendering as tokens arrive
- No waiting for complete response generation

**3. Smart Pre-Computation**
- Resume embeddings generated during upload
- Common question patterns pre-indexed
- 80% faster response for frequent queries

**4. Batch Processing**
- Question clustering for efficient API calls
- Reduced OpenAI API costs by 70%
- Maintained response quality with smart batching

## Performance Metrics

Our optimizations delivered impressive results:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Embedding Generation | 1.459s | 0.3s | **80%** |
| First Response | 2.7s | 1.0s | **63%** |
| Cache Hit Rate | - | 90%+ | - |
| API Cost Savings | - | 70%+ | - |

## Real-World Impact

These optimizations translate to real user value:
- Natural conversation flow without awkward pauses
- Instant access to personalized answer suggestions
- Cost-effective scaling as user base grows
- Reliable performance under load

## What's Next

We're continuously improving the system:
- Multi-language support expansion
- Enhanced context understanding with GPT-4 Turbo
- Real-time collaborative interview preparation
- Advanced analytics for interview performance

## Try It Yourself

Experience the power of real-time AI interview assistance:

🔗 **Website**: https://interviewasssistant.com
📧 **Contact**: liu.lucian6@gmail.com

---

*Building this system taught us that performance optimization isn't just about speed—it's about creating a seamless user experience that feels natural and intuitive. Every millisecond counts when you're helping someone land their dream job.*

#BuildInPublic #AI #TechArchitecture #PerformanceOptimization #InterviewPrep''',
    'tags': ['AI', 'Performance-Optimization', 'System-Architecture', 'BuildInPublic', 'Interview-Prep']
}

def main():
    logger.info("="*80)
    logger.info("🧪 Medium 发布功能测试")
    logger.info("="*80)

    logger.info(f"📝 测试内容:")
    logger.info(f"   标题: {test_content['title']}")
    logger.info(f"   字数: {len(test_content['content'].split())} words")
    logger.info(f"   标签: {', '.join(test_content['tags'])}")

    poster = MediumPoster()

    try:
        # 步骤1: 设置浏览器
        logger.info("\n🌐 步骤1: 设置浏览器...")
        poster.setup_browser(headless=False)
        logger.info("   ✅ 浏览器已启动")

        # 步骤2: 验证登录
        logger.info("\n🔐 步骤2: 验证登录状态...")
        if not poster.verify_login():
            logger.error("   ❌ 登录验证失败")
            logger.error("   请先运行: python3 medium_login_and_save_auth.py")
            return False

        logger.info("   ✅ 登录验证成功")

        # 步骤3: 发布文章
        logger.info("\n📤 步骤3: 开始发布文章...")
        success = poster.create_post(test_content)

        if success:
            logger.info("\n" + "="*80)
            logger.info("✅ Medium 文章发布成功！")
            logger.info("="*80)
            logger.info(f"📝 标题: {test_content['title']}")
            logger.info(f"🏷️  标签: {', '.join(test_content['tags'])}")
            logger.info("="*80)
            return True
        else:
            logger.error("\n❌ 发布失败")
            return False

    except Exception as e:
        logger.error(f"\n❌ 测试过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

    finally:
        try:
            logger.info("\n⏸️  按 Enter 关闭浏览器...")
            input()
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass

        poster.close_browser()
        logger.info("🔒 浏览器已关闭")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
