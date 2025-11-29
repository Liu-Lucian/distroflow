#!/usr/bin/env python3
"""
Reddit账号管理 - 跟踪账号状态和发帖历史
实现养号策略
"""
import json
import os
from datetime import datetime, timedelta

class RedditAccountManager:
    def __init__(self, state_file='reddit_account_state.json'):
        self.state_file = state_file
        self.load_state()

    def load_state(self):
        """加载账号状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            # 初始化状态
            self.state = {
                "account_created_at": datetime.now().isoformat(),
                "total_posts": 0,
                "posts_history": [],  # [{timestamp, subreddit, title, success}]
                "current_phase": "cold_start",  # cold_start, growing, stable, mature
                "last_post_at": None
            }
            self.save_state()

    def save_state(self):
        """保存账号状态"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_account_age_days(self):
        """获取账号年龄（天数）"""
        created = datetime.fromisoformat(self.state["account_created_at"])
        return (datetime.now() - created).days

    def determine_phase(self):
        """根据账号年龄确定当前阶段"""
        age_days = self.get_account_age_days()

        if age_days <= 5:
            phase = "cold_start"
        elif age_days <= 14:
            phase = "growing"
        elif age_days <= 30:
            phase = "stable"
        else:
            phase = "mature"

        self.state["current_phase"] = phase
        return phase

    def get_daily_post_limit(self):
        """获取每日发帖上限"""
        phase = self.determine_phase()

        limits = {
            "cold_start": 1,    # 0-5天: 最多1篇/天
            "growing": 1,       # 5-14天: 1篇/天（隔天更好）
            "stable": 3,        # 15-30天: 2-3篇/天
            "mature": 4         # 30天+: 最多4篇/天
        }

        return limits.get(phase, 1)

    def get_minimum_interval_hours(self):
        """获取最小发帖间隔（小时）"""
        phase = self.determine_phase()

        intervals = {
            "cold_start": 24,   # 冷启动: 24小时
            "growing": 12,      # 养号期: 12小时
            "stable": 4,        # 稳定期: 4小时
            "mature": 2         # 成熟期: 2小时
        }

        return intervals.get(phase, 24)

    def can_post_now(self):
        """检查现在是否可以发帖"""
        # 1. 检查是否有最后发帖记录
        if not self.state["last_post_at"]:
            return True, "首次发帖"

        # 2. 检查发帖间隔
        last_post = datetime.fromisoformat(self.state["last_post_at"])
        min_interval = timedelta(hours=self.get_minimum_interval_hours())

        if datetime.now() - last_post < min_interval:
            remaining = (last_post + min_interval) - datetime.now()
            return False, f"距离上次发帖不足{self.get_minimum_interval_hours()}小时，还需等待{remaining}"

        # 3. 检查今日发帖数
        today_posts = self.get_today_posts_count()
        daily_limit = self.get_daily_post_limit()

        if today_posts >= daily_limit:
            return False, f"今日已达发帖上限({daily_limit}篇)"

        return True, "可以发帖"

    def get_today_posts_count(self):
        """获取今日已发帖数"""
        today = datetime.now().date()
        count = 0

        for post in self.state["posts_history"]:
            post_date = datetime.fromisoformat(post["timestamp"]).date()
            if post_date == today and post.get("success", False):
                count += 1

        return count

    def record_post(self, subreddit, title, success=True):
        """记录发帖"""
        post_record = {
            "timestamp": datetime.now().isoformat(),
            "subreddit": subreddit,
            "title": title,
            "success": success
        }

        self.state["posts_history"].append(post_record)

        if success:
            self.state["total_posts"] += 1
            self.state["last_post_at"] = datetime.now().isoformat()

        self.save_state()

    def get_stats(self):
        """获取统计信息"""
        return {
            "账号年龄": f"{self.get_account_age_days()}天",
            "当前阶段": self.state["current_phase"],
            "总发帖数": self.state["total_posts"],
            "今日已发": self.get_today_posts_count(),
            "每日上限": self.get_daily_post_limit(),
            "最小间隔": f"{self.get_minimum_interval_hours()}小时"
        }

if __name__ == "__main__":
    manager = RedditAccountManager()
    stats = manager.get_stats()

    print("=" * 80)
    print("📊 Reddit账号状态")
    print("=" * 80)
    for key, value in stats.items():
        print(f"{key}: {value}")

    can_post, reason = manager.can_post_now()
    print(f"\n当前状态: {'✅ 可以发帖' if can_post else '❌ 暂不可发帖'}")
    print(f"原因: {reason}")
