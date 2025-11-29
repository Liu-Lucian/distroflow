#!/usr/bin/env python3
"""
Reddit 7天养号解锁计划
目标：账号年龄≥7天 + Karma≥50 → 解锁r/startups发帖
"""
import json
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Reddit7DayPlan:
    def __init__(self, state_file='reddit_7day_plan_state.json'):
        self.state_file = state_file
        self.load_state()

    def load_state(self):
        """加载养号进度"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            # 初始化7天计划
            self.state = {
                "plan_start_date": datetime.now().isoformat(),
                "target_unlock_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "current_day": 1,
                "total_comments_posted": 0,
                "estimated_karma": 0,
                "daily_log": [],
                "karma_milestones": {
                    "day_1_target": 5,
                    "day_2_target": 12,
                    "day_3_target": 20,
                    "day_4_target": 30,
                    "day_5_target": 40,
                    "day_6_target": 48,
                    "day_7_target": 55
                },
                "unlock_status": {
                    "account_age_ok": False,
                    "karma_ok": False,
                    "can_post_to_startups": False
                }
            }
            self.save_state()

    def save_state(self):
        """保存养号进度"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_current_day(self):
        """计算当前是第几天"""
        start = datetime.fromisoformat(self.state["plan_start_date"])
        now = datetime.now()
        days_passed = (now - start).days + 1
        return min(days_passed, 7)

    def get_daily_task(self, day):
        """获取每日任务"""
        tasks = {
            1: {
                "focus": "热身 - 熟悉社区",
                "subreddits": ["AskReddit", "todayilearned", "explainlikeimfive"],
                "comments_target": 3,
                "strategy": "发简单有用的评论，混脸熟",
                "karma_target": 5
            },
            2: {
                "focus": "活跃 - 提升曝光",
                "subreddits": ["AskReddit", "technology", "todayilearned"],
                "comments_target": 4,
                "strategy": "评论热门帖子，争取upvotes",
                "karma_target": 12
            },
            3: {
                "focus": "拓展 - 技术社区",
                "subreddits": ["programming", "webdev", "technology"],
                "comments_target": 4,
                "strategy": "发技术相关评论，显示专业性",
                "karma_target": 20
            },
            4: {
                "focus": "混圈 - 创业社区",
                "subreddits": ["Entrepreneur", "startups", "smallbusiness"],
                "comments_target": 5,
                "strategy": "在目标社区评论（不发帖），混脸熟",
                "karma_target": 30
            },
            5: {
                "focus": "巩固 - AI/ML社区",
                "subreddits": ["artificial", "MachineLearning", "technology"],
                "comments_target": 5,
                "strategy": "AI相关讨论，为发帖铺垫",
                "karma_target": 40
            },
            6: {
                "focus": "冲刺 - 多板块活跃",
                "subreddits": ["AskReddit", "startups", "Entrepreneur", "technology"],
                "comments_target": 5,
                "strategy": "保持活跃，确保karma达标",
                "karma_target": 48
            },
            7: {
                "focus": "准备 - 最后检查",
                "subreddits": ["startups", "Entrepreneur", "SaaS"],
                "comments_target": 3,
                "strategy": "在目标板块最后混脸熟，准备明天发帖",
                "karma_target": 55
            }
        }

        return tasks.get(day, tasks[7])

    def record_daily_progress(self, comments_posted, karma_gained):
        """记录每日进度"""
        current_day = self.get_current_day()

        log_entry = {
            "day": current_day,
            "date": datetime.now().isoformat(),
            "comments_posted": comments_posted,
            "karma_gained": karma_gained,
            "total_karma": self.state["estimated_karma"] + karma_gained
        }

        self.state["daily_log"].append(log_entry)
        self.state["total_comments_posted"] += comments_posted
        self.state["estimated_karma"] += karma_gained
        self.state["current_day"] = current_day

        # 更新解锁状态
        self.check_unlock_status()

        self.save_state()

    def check_unlock_status(self):
        """检查是否达到解锁条件"""
        current_day = self.get_current_day()
        current_karma = self.state["estimated_karma"]

        # 账号年龄检查
        self.state["unlock_status"]["account_age_ok"] = current_day >= 7

        # Karma检查
        self.state["unlock_status"]["karma_ok"] = current_karma >= 50

        # 综合判断
        self.state["unlock_status"]["can_post_to_startups"] = (
            self.state["unlock_status"]["account_age_ok"] and
            self.state["unlock_status"]["karma_ok"]
        )

    def show_progress(self):
        """显示养号进度"""
        current_day = self.get_current_day()
        today_task = self.get_daily_task(current_day)

        print("=" * 80)
        print("📊 Reddit 7天养号进度")
        print("=" * 80)
        print(f"\n📅 第 {current_day}/7 天")
        print(f"🎯 今日重点: {today_task['focus']}")
        print(f"💬 评论目标: {today_task['comments_target']} 条")
        print(f"👍 Karma目标: {today_task['karma_target']}")
        print(f"\n📍 推荐板块:")
        for sub in today_task['subreddits']:
            print(f"   • r/{sub}")
        print(f"\n💡 策略: {today_task['strategy']}")
        print(f"\n📈 累计进度:")
        print(f"   总评论数: {self.state['total_comments_posted']}")
        print(f"   预估Karma: {self.state['estimated_karma']}")
        print(f"\n🔓 解锁状态:")
        print(f"   账号年龄: {'✅ 已满7天' if self.state['unlock_status']['account_age_ok'] else f'❌ 还需 {7-current_day} 天'}")
        print(f"   Karma值: {'✅ 已达50' if self.state['unlock_status']['karma_ok'] else f'❌ 还需 {50-self.state['estimated_karma']} karma'}")
        print(f"   可发帖到r/startups: {'✅ 已解锁！' if self.state['unlock_status']['can_post_to_startups'] else '❌ 未解锁'}")

        if self.state["unlock_status"]["can_post_to_startups"]:
            print("\n🎉 恭喜！你已经可以在r/startups发帖了！")
            print("   运行 python3 auto_reddit_scheduler.py 开始Build in Public")
        else:
            days_left = 7 - current_day
            karma_left = max(0, 50 - self.state['estimated_karma'])
            print(f"\n⏳ 距离解锁还需:")
            if days_left > 0:
                print(f"   • {days_left} 天")
            if karma_left > 0:
                print(f"   • {karma_left} karma")

        print("=" * 80)

    def get_karma_estimate(self, comments_posted):
        """估算可获得的karma"""
        # 保守估计：每条评论平均获得1-3个upvote
        # 有些可能获得5-10个，有些可能0个
        # 平均下来：每条评论约1.5 karma
        return int(comments_posted * 1.5)

if __name__ == "__main__":
    plan = Reddit7DayPlan()

    # 显示当前进度
    plan.show_progress()

    print("\n" + "=" * 80)
    print("📝 使用说明")
    print("=" * 80)
    print("\n每天运行养号脚本:")
    print("  python3 reddit_karma_farmer.py")
    print("\n手动记录进度:")
    print("  python3 -c \"from reddit_7day_plan import Reddit7DayPlan; \\")
    print("    plan = Reddit7DayPlan(); \\")
    print("    plan.record_daily_progress(comments_posted=5, karma_gained=8); \\")
    print("    plan.show_progress()\"")
    print("\n查看当前进度:")
    print("  python3 reddit_7day_plan.py")
    print("=" * 80)
