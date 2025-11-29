#!/Users/l.u.c/my-app/MarketingMind AI/venv/bin/python3
"""
Medium 每日自动发布 - 19:00-22:00 随机时间发布
使用 Claude API 生成技术深度文章
永不停息的每日打卡系统
"""
import sys
sys.path.insert(0, 'src')

from medium_poster import MediumPoster
from medium_content_generator import MediumContentGenerator
import schedule
import time
import random
import logging
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medium_daily_post.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def post_to_medium():
    """执行 Medium 发布任务"""
    logger.info("=" * 80)
    logger.info("🟠 开始每日 Medium 自动发布任务")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    poster = None

    try:
        # 步骤1: 生成文章内容
        logger.info("\n📝 步骤1: 使用 Claude API 生成文章...")

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("❌ 未设置 ANTHROPIC_API_KEY")
            return False

        generator = MediumContentGenerator(api_key)
        article = generator.generate_and_save()

        logger.info(f"✅ 文章生成成功:")
        logger.info(f"   标题: {article['title']}")
        logger.info(f"   字数: {article['word_count']} words")
        logger.info(f"   角度: {article['angle_name']}")

        # 步骤2: 准备发布内容
        logger.info("\n📋 步骤2: 准备发布内容...")

        content = {
            'title': article['title'],
            'content': article['content'],
            'tags': article['tags']
        }

        if article.get('subtitle'):
            content['subtitle'] = article['subtitle']

        logger.info(f"   内容长度: {len(content['content'])} 字符")
        logger.info(f"   标签: {', '.join(content['tags'])}")

        # 步骤3: 发布到 Medium
        logger.info("\n🌐 步骤3: 发布到 Medium...")

        poster = MediumPoster()
        poster.setup_browser(headless=True)

        # 验证登录
        logger.info("🔐 验证登录...")
        if not poster.verify_login():
            logger.error("❌ 登录验证失败")
            return False

        logger.info("✅ 登录验证成功")

        # 发布
        logger.info("📤 开始发布...")
        success = poster.create_post(content)

        if success:
            logger.info("=" * 80)
            logger.info("✅ HireMeAI Medium 今日打卡成功！")
            logger.info(f"📝 标题: {article['title']}")
            logger.info(f"🎯 角度: {article['angle_name']}")
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
        if poster:
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
    post_to_medium()

    # 发布完成后，立即安排明天的随机时间
    schedule_random_time()

def main():
    logger.info("=" * 80)
    logger.info("🚀 Medium 每日自动发布系统启动")
    logger.info("⏰ 发布时间: 每天19:00-22:00随机")
    logger.info("🤖 内容生成: Claude API (Sonnet-3.5)")
    logger.info("📖 内容来源: 产品介绍.md")
    logger.info("🔄 运行模式: 永不停息")
    logger.info("=" * 80)

    # 检查 API keys
    if 'ANTHROPIC_API_KEY' not in os.environ:
        logger.error("❌ 请设置 ANTHROPIC_API_KEY")
        logger.error("   export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    # 检查产品介绍文件
    if not os.path.exists("产品介绍.md"):
        logger.error("❌ 未找到产品介绍.md文件")
        sys.exit(1)

    # 检查认证文件
    if not os.path.exists("medium_auth.json"):
        logger.error("❌ 未找到 medium_auth.json")
        logger.error("   请先运行: python3 medium_login_and_save_auth.py")
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
