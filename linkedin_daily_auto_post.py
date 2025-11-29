#!/Users/l.u.c/my-app/MarketingMind AI/venv/bin/python3
"""
LinkedIn每日自动发布 - 19:00-22:00随机时间发布
永不停息的每日打卡系统
"""
import sys
sys.path.insert(0, 'src')

from linkedin_poster import LinkedInPoster
import schedule
import time
import random
import logging
from datetime import datetime, timedelta
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_daily_post.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 从产品介绍生成每日内容
def get_daily_content():
    """每天生成不同的HireMeAI产品介绍内容"""

    # 多个不同角度的产品介绍模板
    templates = [
        {
            'content': '''🚀 Introducing HireMeAI (即答侠) - Your AI Interview Assistant

Transform your interview preparation with the next-generation AI-powered interview assistance platform.

🎯 What Makes HireMeAI Different:

✅ Real-Time Voice Assistant
• 95%+ accuracy in speech recognition (Chinese + English)
• Intelligent speaker identification - distinguishes interviewer vs interviewee
• <1s first-word latency for instant responses
• Azure Speech + Picovoice Eagle technology

✅ Smart Resume Optimizer
• ATS scoring system with 4-dimensional analysis
• STAR framework enhancement
• Personalized versions for different companies
• 85%+ correlation with manual scoring

✅ Personalized Answer Templates
• Deep analysis based on your resume + job description
• 4-tier storage system (CORE/MEDIUM/SHORT/TEMPORARY)
• 1536-dimensional vector semantic matching
• 88%+ semantic matching accuracy

✅ Performance Optimization
• Embedding generation: 1.459s → 0.3s (80% improvement)
• First response latency: 2.7s → 1.0s (60% improvement)
• 90%+ cache hit rate for common questions
• 70%+ API cost savings

💡 Perfect For:
• Job seekers preparing for interviews
• Career training institutions
• HR teams standardizing interview processes

🔧 Tech Stack:
OpenAI GPT-4 | Azure Speech Services | Picovoice Eagle | ChromaDB | Python 3.8+

📊 Results:
• Reduce interview preparation time from days to hours
• Standardized professional answers
• Lower interview anxiety, boost confidence

🌐 Learn More: https://interviewasssistant.com
📧 Contact: liu.lucian6@gmail.com

Making every interview a success story.

#AI #InterviewPrep #CareerDevelopment #JobSearch #HRTech #MachineLearning #SpeechRecognition #NLP #TechInnovation #StartupLife''',
            'post_as': 'personal'
        },
        # 可以添加更多不同的内容变体
    ]

    # 随机选择一个模板（现在只有一个，以后可以扩展）
    return random.choice(templates)

def post_to_linkedin():
    """执行LinkedIn发布任务"""
    logger.info("=" * 80)
    logger.info("🔵 开始每日LinkedIn自动发布任务")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    poster = LinkedInPoster()

    try:
        # 设置浏览器（无头模式）
        logger.info("🌐 设置浏览器...")
        poster.setup_browser(headless=True)

        # 验证登录
        logger.info("🔐 验证登录...")
        if not poster.verify_login():
            logger.error("❌ 登录验证失败")
            return False

        logger.info("✅ 登录验证成功")

        # 获取今日内容
        content = get_daily_content()
        logger.info(f"📝 准备发布内容 ({len(content['content'])} 字符)")

        # 发布
        logger.info("📤 发布到LinkedIn...")
        success = poster.create_post(content)

        if success:
            logger.info("=" * 80)
            logger.info("✅ HireMeAI今日打卡成功！")
            logger.info("=" * 80)
            return True
        else:
            logger.error("❌ 发布失败")
            return False

    except Exception as e:
        logger.error(f"❌ 发布过程出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        try:
            poster.close_browser()
        except:
            pass

def schedule_random_time():
    """在19:00-22:00之间随机安排今天的发布时间"""
    # 生成19:00-22:00之间的随机时间
    random_hour = random.randint(19, 21)  # 19, 20, 21
    random_minute = random.randint(0, 59)

    scheduled_time = f"{random_hour:02d}:{random_minute:02d}"

    logger.info(f"📅 今日发布时间已安排: {scheduled_time}")

    # 清除之前的任务
    schedule.clear()

    # 安排今天的发布任务
    schedule.every().day.at(scheduled_time).do(job_wrapper)

    return scheduled_time

def job_wrapper():
    """任务包装器：执行发布并安排明天的时间"""
    # 执行发布
    post_to_linkedin()

    # 发布完成后，立即安排明天的随机时间
    schedule_random_time()

def main():
    logger.info("=" * 80)
    logger.info("🚀 LinkedIn每日自动发布系统启动")
    logger.info("⏰ 发布时间: 每天19:00-22:00随机")
    logger.info("🔄 运行模式: 永不停息")
    logger.info("=" * 80)

    # 检查API key
    if 'OPENAI_API_KEY' not in os.environ:
        logger.error("❌ 请设置 OPENAI_API_KEY")
        sys.exit(1)

    # 首次启动时安排今天的任务
    scheduled_time = schedule_random_time()

    logger.info(f"✅ 系统已启动，等待执行...")
    logger.info(f"下次发布时间: 今天 {scheduled_time}")

    # 永久运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("\n👋 系统已停止")
    except Exception as e:
        logger.error(f"❌ 系统错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
