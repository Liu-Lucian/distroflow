#!/usr/bin/env python3
"""
Substack Master - 一键永久运行所有自动化
自动处理：发布文章 + 评论养号
"""

import sys
sys.path.insert(0, 'src')
import subprocess
import time
import json
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# ==================== 配置 ====================

CONFIG = {
    # 评论设置
    "comment_runs_per_day": 3,
    "comment_run_times": ["09:00", "14:00", "20:00"],
    "max_comments_per_day": 15,

    # 发布设置
    "auto_schedule_posts": True,  # 是否自动安排新文章
    "schedule_posts_every_days": 7,  # 每7天安排一次新文章
    "last_scheduled_file": "last_post_schedule.json",  # 记录上次安排时间
}


# ==================== 评论系统 ====================

def get_today_comment_count():
    """统计今天评论数"""
    try:
        with open('substack_commented_posts.json', 'r') as f:
            history = json.load(f)
        today = datetime.now().date()
        today_comments = [p for p in history if datetime.fromisoformat(p['commented_at']).date() == today]
        return len(today_comments)
    except FileNotFoundError:
        return 0


def should_run_comments():
    """检查是否应该运行评论"""
    today_count = get_today_comment_count()
    if today_count >= CONFIG['max_comments_per_day']:
        logger.warning(f"⚠️  今日已评论 {today_count} 条（限额: {CONFIG['max_comments_per_day']}）")
        return False
    return True


def run_comment_farmer():
    """运行评论系统"""
    logger.info("\n" + "="*80)
    logger.info("🌾 评论养号任务")
    logger.info("="*80)

    if not should_run_comments():
        logger.info("⏭️  今日评论已达限额，跳过")
        return

    try:
        logger.info("🚀 启动评论系统...\n")
        result = subprocess.run(
            ['python3', 'substack_comment_farmer.py'],
            env=os.environ.copy()
        )

        if result.returncode == 0:
            logger.info("\n✅ 评论任务完成")
        else:
            logger.error(f"\n❌ 评论任务失败 (code {result.returncode})")

    except Exception as e:
        logger.error(f"❌ 评论系统错误: {e}")


# ==================== 发布系统 ====================

def get_last_scheduled_time():
    """获取上次安排文章的时间"""
    try:
        with open(CONFIG['last_scheduled_file'], 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_scheduled'])
    except FileNotFoundError:
        return None


def save_scheduled_time():
    """保存本次安排时间"""
    with open(CONFIG['last_scheduled_file'], 'w') as f:
        json.dump({
            'last_scheduled': datetime.now().isoformat()
        }, f)


def should_schedule_new_posts():
    """检查是否需要安排新文章"""
    if not CONFIG['auto_schedule_posts']:
        return False

    last_time = get_last_scheduled_time()

    if last_time is None:
        logger.info("📅 首次运行，需要安排文章")
        return True

    days_since = (datetime.now() - last_time).days

    if days_since >= CONFIG['schedule_posts_every_days']:
        logger.info(f"📅 距上次安排已 {days_since} 天，需要安排新文章")
        return True

    logger.info(f"📅 距上次安排 {days_since} 天，还不需要安排（{CONFIG['schedule_posts_every_days']}天一次）")
    return False


def schedule_new_posts():
    """安排新的文章发布"""
    logger.info("\n" + "="*80)
    logger.info("📅 安排新文章发布")
    logger.info("="*80)

    try:
        logger.info("🚀 运行发布安排系统...\n")
        result = subprocess.run(
            ['python3', 'schedule_substack_posts.py'],
            env=os.environ.copy()
        )

        if result.returncode == 0:
            logger.info("\n✅ 文章安排完成")
            save_scheduled_time()
        else:
            logger.error(f"\n❌ 文章安排失败 (code {result.returncode})")

    except Exception as e:
        logger.error(f"❌ 发布系统错误: {e}")


# ==================== 主控制器 ====================

def run_single_session():
    """运行一次完整会话"""
    logger.info("\n" + "="*80)
    logger.info("🤖 Substack Master - 自动化会话")
    logger.info("="*80)
    logger.info(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 统计信息
    today_comments = get_today_comment_count()
    logger.info(f"📊 今日评论: {today_comments}/{CONFIG['max_comments_per_day']}")

    # 检查并安排文章
    if should_schedule_new_posts():
        schedule_new_posts()

    # 运行评论
    run_comment_farmer()

    logger.info("\n" + "="*80)
    logger.info("✅ 会话完成")
    logger.info("="*80)


def run_continuous():
    """持续运行模式"""
    logger.info("="*80)
    logger.info("🚀 Substack Master - 永久运行模式")
    logger.info("="*80)
    logger.info("配置:")
    logger.info(f"  • 每天评论: {CONFIG['comment_runs_per_day']} 次")
    logger.info(f"  • 运行时间: {', '.join(CONFIG['comment_run_times'])}")
    logger.info(f"  • 每日限额: {CONFIG['max_comments_per_day']} 条")
    logger.info(f"  • 自动发布: {'是' if CONFIG['auto_schedule_posts'] else '否'}")
    if CONFIG['auto_schedule_posts']:
        logger.info(f"  • 发布间隔: 每 {CONFIG['schedule_posts_every_days']} 天")
    logger.info("")
    logger.info("按 Ctrl+C 停止")
    logger.info("="*80)

    last_run = None

    while True:
        try:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")

            # 检查是否到了运行时间
            should_run = False
            for run_time in CONFIG['comment_run_times']:
                run_hour, run_minute = map(int, run_time.split(':'))
                if current_time.hour == run_hour and abs(current_time.minute - run_minute) <= 1:
                    # 确保1小时内不重复运行
                    if last_run is None or (current_time - last_run).total_seconds() > 3600:
                        should_run = True
                        break

            if should_run:
                logger.info(f"\n⏰ 定时运行: {current_time_str}")
                run_single_session()
                last_run = current_time
                time.sleep(120)  # 等2分钟避免重复
            else:
                # 每分钟检查一次
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  用户停止")
            break
        except Exception as e:
            logger.error(f"❌ 运行错误: {e}")
            logger.info("⏳ 等待5分钟后重试...")
            time.sleep(300)


def main():
    """主函数"""
    import sys

    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("❌ 未设置 OPENAI_API_KEY")
        logger.info("设置方法: export OPENAI_API_KEY='sk-proj-...'")
        return

    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            run_continuous()
        elif sys.argv[1] == "--once":
            run_single_session()
        elif sys.argv[1] == "--help":
            print("""
Substack Master - 一键永久运行所有自动化

用法:
  python3 substack_master.py                运行一次（默认）
  python3 substack_master.py --once         运行一次
  python3 substack_master.py --continuous   持续运行（推荐）
  python3 substack_master.py --help         显示帮助

功能:
  ✅ 自动评论养号（每天3次）
  ✅ 自动安排文章发布（每周一次）
  ✅ 完全自动化，无需手动干预

配置:
  编辑本文件开头的 CONFIG 字典自定义配置
            """)
        else:
            logger.error(f"未知参数: {sys.argv[1]}")
            logger.info("使用 --help 查看帮助")
    else:
        # 默认运行一次
        run_single_session()


if __name__ == "__main__":
    main()
