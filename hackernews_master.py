#!/usr/bin/env python3
"""
Hacker News 自动化大师控制器
===============================

统一管理 HN 的发帖 + 评论，一个命令搞定所有事情。

功能：
1. 自动发帖（Show HN + Ask HN）- 每月1 Show HN + 4 Ask HN
2. 自动评论（技术讨论）- 每天2-3条高质量评论
3. 智能调度 - 避免频率过高被检测
4. 统一监控 - 一个界面查看所有活动

运行模式：
- 单次运行: python3 hackernews_master.py --once
- 永久运行: python3 hackernews_master.py --forever
- 仅发帖: python3 hackernews_master.py --post-only
- 仅评论: python3 hackernews_master.py --comment-only

使用前确保：
1. export ANTHROPIC_API_KEY='sk-ant-api03-...'
2. python3 hackernews_login_and_save_auth.py (一次性登录)
"""

import sys
sys.path.insert(0, 'src')

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import random
import argparse

# 导入子系统
from hackernews_auto_poster import HackerNewsAutoPoster
from hackernews_auto_reply import HackerNewsAutoReplier

# ==================== 配置 ====================

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hackernews_master.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 频率控制
SCHEDULE_CONFIG = {
    # 发帖频率（每月）
    'posts_per_month': {
        'show_hn': 1,   # 每月1次 Show HN
        'ask_hn': 4     # 每月4次 Ask HN（每周1次）
    },

    # 评论频率（每天）
    'comments_per_day': {
        'min': 2,       # 每天至少2条
        'max': 3        # 每天最多3条
    },

    # 评论时间段（避免太规律）
    'comment_time_windows': [
        (9, 11),    # 上午 09:00-11:00
        (14, 16),   # 下午 14:00-16:00
        (19, 21)    # 晚上 19:00-21:00
    ],

    # 发帖时间段（工作日白天）
    'post_time_windows': [
        (9, 12),    # 上午 09:00-12:00
        (14, 17)    # 下午 14:00-17:00
    ],

    # 检查间隔（小时）
    'check_interval_hours': 2
}

# ==================== 主控制器 ====================

class HackerNewsMaster:
    """HN 自动化主控制器"""

    def __init__(self):
        self.poster = HackerNewsAutoPoster()
        self.replier = HackerNewsAutoReplier()
        self.state_file = 'hackernews_master_state.json'
        self.state = self.load_state()

    def load_state(self) -> Dict:
        """加载运行状态"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'last_post_date': None,
                'last_comment_date': None,
                'posts_this_month': 0,
                'comments_today': 0,
                'total_posts': 0,
                'total_comments': 0,
                'current_month': datetime.now().strftime('%Y-%m')
            }

    def save_state(self):
        """保存运行状态"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def should_post_today(self) -> bool:
        """判断今天是否应该发帖"""

        # 重置月度计数器
        current_month = datetime.now().strftime('%Y-%m')
        if self.state['current_month'] != current_month:
            logger.info("📅 新的一月，重置发帖计数器")
            self.state['posts_this_month'] = 0
            self.state['current_month'] = current_month
            self.save_state()

        # 检查是否已达到本月限额
        total_posts_limit = (SCHEDULE_CONFIG['posts_per_month']['show_hn'] +
                            SCHEDULE_CONFIG['posts_per_month']['ask_hn'])

        if self.state['posts_this_month'] >= total_posts_limit:
            logger.info(f"⏸️  本月发帖已达上限 ({self.state['posts_this_month']}/{total_posts_limit})")
            return False

        # 检查今天是否已发帖
        last_post_date = self.state.get('last_post_date')
        if last_post_date:
            last_date = datetime.fromisoformat(last_post_date).date()
            today = datetime.now().date()

            if last_date == today:
                logger.info("⏸️  今天已经发过帖了")
                return False

        # 检查是否在发帖时间窗口内
        current_hour = datetime.now().hour
        in_time_window = any(
            start <= current_hour < end
            for start, end in SCHEDULE_CONFIG['post_time_windows']
        )

        if not in_time_window:
            logger.info(f"⏸️  当前时间 ({current_hour}:00) 不在发帖窗口内")
            return False

        # 随机决定（避免太规律）- 30% 概率发帖
        if random.random() < 0.3:
            logger.info("✅ 决定今天发帖")
            return True
        else:
            logger.info("⏸️  今天随机决定不发帖")
            return False

    def should_comment_now(self) -> bool:
        """判断现在是否应该评论"""

        # 重置每日计数器
        today_str = datetime.now().strftime('%Y-%m-%d')
        last_comment_date = self.state.get('last_comment_date', '')

        if not last_comment_date or not last_comment_date.startswith(today_str):
            logger.info("📅 新的一天，重置评论计数器")
            self.state['comments_today'] = 0
            self.save_state()

        # 检查是否已达到今日限额
        max_comments = SCHEDULE_CONFIG['comments_per_day']['max']
        if self.state['comments_today'] >= max_comments:
            logger.info(f"⏸️  今日评论已达上限 ({self.state['comments_today']}/{max_comments})")
            return False

        # 检查是否在评论时间窗口内
        current_hour = datetime.now().hour
        in_time_window = any(
            start <= current_hour < end
            for start, end in SCHEDULE_CONFIG['comment_time_windows']
        )

        if not in_time_window:
            logger.info(f"⏸️  当前时间 ({current_hour}:00) 不在评论窗口内")
            return False

        # 确保已完成最少评论数
        min_comments = SCHEDULE_CONFIG['comments_per_day']['min']
        if self.state['comments_today'] < min_comments:
            logger.info(f"✅ 今日评论未达最低要求 ({self.state['comments_today']}/{min_comments})")
            return True

        # 随机决定（避免太规律）- 40% 概率评论
        if random.random() < 0.4:
            logger.info("✅ 决定现在评论")
            return True
        else:
            logger.info("⏸️  随机决定暂时不评论")
            return False

    def execute_posting(self):
        """执行发帖任务"""
        logger.info("\n" + "=" * 80)
        logger.info("📤 执行发帖任务")
        logger.info("=" * 80)

        try:
            # 加载或生成本月计划
            filename, schedule = self.poster.load_or_generate_current_schedule()

            if not schedule:
                logger.error("❌ 加载/生成发帖计划失败")
                return False

            # 执行计划中今天的任务
            today_str = datetime.now().strftime('%Y-%m-%d')
            posted_today = False

            for post in schedule.get('posts', []):
                # 检查是否是今天的帖子且未发布
                if post['scheduled_date'] == today_str and not post.get('posted', False):
                    logger.info(f"📝 找到今天的帖子: {post['post_data']['title'][:60]}...")

                    # 执行发帖
                    success = self.poster.execute_schedule(filename, schedule)

                    if success:
                        posted_today = True
                        break

            if posted_today:
                # 更新状态
                self.state['last_post_date'] = datetime.now().isoformat()
                self.state['posts_this_month'] += 1
                self.state['total_posts'] += 1
                self.save_state()

                logger.info("✅ 发帖任务完成")
                return True
            else:
                logger.info("⏸️  今天没有计划的帖子")
                return False

        except Exception as e:
            logger.error(f"❌ 发帖任务失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def execute_commenting(self):
        """执行评论任务"""
        logger.info("\n" + "=" * 80)
        logger.info("💬 执行评论任务")
        logger.info("=" * 80)

        try:
            # 加载或生成今日评论计划
            filename, schedule = self.replier.load_or_generate_today_schedule()

            if not schedule:
                logger.error("❌ 加载/生成评论计划失败")
                return False

            # 执行计划
            success = self.replier.run_today_schedule(filename, schedule)

            if success:
                # 更新状态
                self.state['last_comment_date'] = datetime.now().isoformat()
                self.state['comments_today'] += 1
                self.state['total_comments'] += 1
                self.save_state()

                logger.info("✅ 评论任务完成")
                return True
            else:
                logger.info("⏸️  今天没有待执行的评论")
                return False

        except Exception as e:
            logger.error(f"❌ 评论任务失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_once(self, post_only=False, comment_only=False):
        """运行一次检查"""
        logger.info("\n" + "=" * 80)
        logger.info("🤖 HN 自动化大师 - 单次运行")
        logger.info("=" * 80)
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"模式: {'仅发帖' if post_only else '仅评论' if comment_only else '发帖+评论'}")
        logger.info("=" * 80)

        # 显示当前状态
        self.print_status()

        actions_taken = []

        # 检查是否需要发帖
        if not comment_only:
            if self.should_post_today():
                if self.execute_posting():
                    actions_taken.append("发帖")

        # 检查是否需要评论
        if not post_only:
            if self.should_comment_now():
                if self.execute_commenting():
                    actions_taken.append("评论")

        # 总结
        logger.info("\n" + "=" * 80)
        if actions_taken:
            logger.info(f"✅ 本次运行完成，执行了: {', '.join(actions_taken)}")
        else:
            logger.info("⏸️  本次运行未执行任何操作")
        logger.info("=" * 80)

        return len(actions_taken) > 0

    def run_forever(self, post_only=False, comment_only=False):
        """永久运行（定时检查）"""
        logger.info("\n" + "=" * 80)
        logger.info("🤖 HN 自动化大师 - 永久运行模式")
        logger.info("=" * 80)
        logger.info(f"模式: {'仅发帖' if post_only else '仅评论' if comment_only else '发帖+评论'}")
        logger.info(f"检查间隔: {SCHEDULE_CONFIG['check_interval_hours']} 小时")
        logger.info("=" * 80)

        try:
            while True:
                self.run_once(post_only=post_only, comment_only=comment_only)

                # 等待下次检查
                wait_hours = SCHEDULE_CONFIG['check_interval_hours']
                # 添加随机偏移（±30分钟）
                wait_minutes = wait_hours * 60 + random.randint(-30, 30)

                next_check = datetime.now() + timedelta(minutes=wait_minutes)
                logger.info(f"\n⏰ 下次检查时间: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"   (等待 {wait_minutes} 分钟)")

                time.sleep(wait_minutes * 60)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断，正在关闭...")
        finally:
            self.cleanup()

    def print_status(self):
        """打印当前状态"""
        logger.info("\n📊 当前状态:")
        logger.info(f"   本月发帖: {self.state['posts_this_month']} / {SCHEDULE_CONFIG['posts_per_month']['show_hn'] + SCHEDULE_CONFIG['posts_per_month']['ask_hn']}")
        logger.info(f"   今日评论: {self.state['comments_today']} / {SCHEDULE_CONFIG['comments_per_day']['max']}")
        logger.info(f"   总发帖数: {self.state['total_posts']}")
        logger.info(f"   总评论数: {self.state['total_comments']}")

        if self.state.get('last_post_date'):
            logger.info(f"   上次发帖: {self.state['last_post_date']}")
        if self.state.get('last_comment_date'):
            logger.info(f"   上次评论: {self.state['last_comment_date']}")
        logger.info("")

    def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理资源...")

        if hasattr(self.replier, 'commenter') and self.replier.commenter:
            try:
                self.replier.commenter.close_browser()
            except:
                pass

        logger.info("✅ 清理完成")

# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(
        description='HN 自动化大师 - 统一管理发帖和评论',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 单次运行（发帖+评论）
  python3 hackernews_master.py --once

  # 永久运行（发帖+评论）
  python3 hackernews_master.py --forever

  # 仅发帖
  python3 hackernews_master.py --once --post-only

  # 仅评论
  python3 hackernews_master.py --once --comment-only

  # 查看状态
  python3 hackernews_master.py --status
        """
    )

    parser.add_argument('--once', action='store_true', help='运行一次检查')
    parser.add_argument('--forever', action='store_true', help='永久运行（定时检查）')
    parser.add_argument('--post-only', action='store_true', help='仅发帖，不评论')
    parser.add_argument('--comment-only', action='store_true', help='仅评论，不发帖')
    parser.add_argument('--status', action='store_true', help='显示当前状态')

    args = parser.parse_args()

    # 检查 API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("❌ 未设置 ANTHROPIC_API_KEY")
        logger.info("   请运行: export ANTHROPIC_API_KEY='sk-ant-api03-...'")
        return 1

    master = HackerNewsMaster()

    # 仅显示状态
    if args.status:
        master.print_status()
        return 0

    # 默认是单次运行
    if not args.once and not args.forever:
        args.once = True

    # 执行
    if args.once:
        master.run_once(post_only=args.post_only, comment_only=args.comment_only)
    elif args.forever:
        master.run_forever(post_only=args.post_only, comment_only=args.comment_only)

    return 0

if __name__ == "__main__":
    exit(main())
