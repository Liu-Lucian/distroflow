#!/usr/bin/env python3
"""
Product Hunt 账号养号脚本（7天计划）

目标：
1. 建立社区信誉和活跃度
2. 熟悉 Product Hunt 文化和风格
3. 为正式 Launch 做准备

策略：
- 每天 2-3 次真诚互动
- 100% 专注于社区贡献（不提及自己的产品）
- 逐步增加活跃度（第1天少，第7天多）
- 只与相关类别产品互动（AI Tools, Productivity, Career）
"""

import sys
sys.path.insert(0, 'src')
from producthunt_commenter import ProductHuntCommenter
import os
from openai import OpenAI
import json
import time
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class ProductHuntAccountWarmup:
    def __init__(self):
        self.commenter = None
        self.warmup_progress_file = "producthunt_warmup_progress.json"
        self.progress = self._load_progress()

    def _load_progress(self) -> dict:
        """加载养号进度"""
        try:
            with open(self.warmup_progress_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # 初始化 7 天计划
            start_date = datetime.now()
            return {
                "start_date": start_date.isoformat(),
                "target_launch_date": (start_date + timedelta(days=7)).isoformat(),
                "daily_plan": [
                    {"day": 1, "target_interactions": 2, "completed": 0, "products": []},
                    {"day": 2, "target_interactions": 2, "completed": 0, "products": []},
                    {"day": 3, "target_interactions": 3, "completed": 0, "products": []},
                    {"day": 4, "target_interactions": 3, "completed": 0, "products": []},
                    {"day": 5, "target_interactions": 3, "completed": 0, "products": []},
                    {"day": 6, "target_interactions": 4, "completed": 0, "products": []},
                    {"day": 7, "target_interactions": 4, "completed": 0, "products": []},
                ],
                "total_interactions": 0,
                "total_upvotes": 0,
                "total_comments": 0,
            }

    def _save_progress(self):
        """保存养号进度"""
        with open(self.warmup_progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def get_current_day(self) -> int:
        """获取当前是第几天"""
        start_date = datetime.fromisoformat(self.progress['start_date'])
        current_date = datetime.now()
        days_passed = (current_date - start_date).days + 1
        return min(days_passed, 7)  # 最多 7 天

    def generate_warmup_comment(self, product_info: dict) -> str:
        """
        生成养号评论（100% 社区风格，0% 推销）

        与正式评论的区别：
        - 绝对不提及 HireMeAI 或自己的产品
        - 更加热情和支持
        - 专注于帮助和学习
        """

        prompt = f"""You are an enthusiastic tech enthusiast exploring Product Hunt for the first time. You're genuinely excited about discovering new products and want to contribute to the community.

**Product you're commenting on**:
- Name: {product_info.get('name', 'N/A')}
- Tagline: {product_info.get('tagline', 'N/A')}
- Category: {product_info.get('category', 'N/A')}

**Your role**:
- NEW Product Hunt member (first week)
- Excited to discover cool products
- Want to contribute genuine value
- NOT promoting anything (you have no product)

**Comment style**:
1. **Be genuinely enthusiastic** - This is exciting stuff!
2. **Ask thoughtful questions** - Show real curiosity
3. **Share insights** - About the problem space (NOT your product)
4. **Use internet slang** - ngl, tbh, fr, lol, gg (1-2 per comment)
5. **Be supportive** - Encourage makers
6. **100% about THEIR product** - Never mention you're building anything

**Good examples**:
✅ "Yooo this looks amazing 🔥 I've been searching for something like this fr. Quick Q - does it integrate with [tool]? That'd be perfect for my workflow"
✅ "Love this! The [feature] is exactly what the market needs tbh. Congrats on the launch 🎉 How'd you come up with this idea?"
✅ "This solves a real problem ngl. I've struggled with [problem] forever. Does it work on mobile too?"
✅ "gg on the launch! The design is clean af. Curious - what was your biggest challenge building this?"

**Bad examples** (DON'T do this):
❌ "As someone building similar tools..." (don't mention you're a builder)
❌ "We faced this problem too..." (no "we")
❌ "Check out my product..." (absolutely not)
❌ "Great product!" (too generic)

**Rules**:
- Max 280 characters
- Use 1-2 internet slang terms
- 1-2 emoji max (🔥💯🎉👀✨)
- Ask a genuine question OR share enthusiasm
- Be specific about what you like
- Sound like a curious community member

Output ONLY the comment text in ENGLISH, nothing else:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,  # 更高创意性
            max_tokens=120
        )

        comment = response.choices[0].message.content.strip().strip('"').strip("'")
        return comment

    def get_todays_target_products(self) -> list:
        """
        获取今天要互动的产品

        养号策略：
        - 优先选择今日发布的产品（Today）
        - 选择相关类别（AI Tools, Productivity, Career）
        - 避免重复互动同一产品
        """

        # 从文件加载今日产品
        try:
            with open('todays_producthunt_products.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                todays_products = data.get('products', [])
        except FileNotFoundError:
            logger.warning("⚠️  未找到 todays_producthunt_products.json")
            logger.info("   请运行: python3 fetch_todays_producthunt_products.py")
            todays_products = []

        # 过滤掉已经互动过的产品
        interacted = []
        for day in self.progress['daily_plan']:
            interacted.extend(day['products'])

        available = [p for p in todays_products if p['url'] not in interacted]

        return available

    def show_warmup_status(self):
        """显示养号进度"""
        current_day = self.get_current_day()
        start_date = datetime.fromisoformat(self.progress['start_date'])
        target_date = datetime.fromisoformat(self.progress['target_launch_date'])

        logger.info("\n" + "=" * 80)
        logger.info("📊 Product Hunt 账号养号进度")
        logger.info("=" * 80)

        print(f"\n⏰ 时间线:")
        print(f"   开始日期: {start_date.strftime('%Y-%m-%d')}")
        print(f"   目标发布: {target_date.strftime('%Y-%m-%d')}")
        print(f"   当前进度: 第 {current_day}/7 天")
        print(f"   剩余时间: {7 - current_day} 天")

        print(f"\n📈 互动统计:")
        print(f"   总互动次数: {self.progress['total_interactions']}")
        print(f"   总点赞数: {self.progress['total_upvotes']}")
        print(f"   总评论数: {self.progress['total_comments']}")

        print(f"\n📅 每日计划:")
        for day_plan in self.progress['daily_plan']:
            day_num = day_plan['day']
            target = day_plan['target_interactions']
            completed = day_plan['completed']
            status = "✅" if completed >= target else ("🔄" if day_num == current_day else "⏳")

            print(f"   Day {day_num}: {status} {completed}/{target} 次互动")

        if current_day <= 7:
            today_plan = self.progress['daily_plan'][current_day - 1]
            remaining = today_plan['target_interactions'] - today_plan['completed']
            if remaining > 0:
                print(f"\n🎯 今日任务: 还需完成 {remaining} 次互动")
            else:
                print(f"\n✅ 今日任务已完成！")

        logger.info("=" * 80)

    def run_daily_warmup(self):
        """执行今日养号任务"""
        current_day = self.get_current_day()

        if current_day > 7:
            logger.info("\n🎉 养号计划已完成！")
            logger.info("   可以准备发布产品了")
            logger.info("   运行: python3 producthunt_launcher.py")
            return

        logger.info(f"\n🚀 开始 Day {current_day} 养号任务...")

        today_plan = self.progress['daily_plan'][current_day - 1]
        target = today_plan['target_interactions']
        completed = today_plan['completed']

        if completed >= target:
            logger.info(f"✅ Day {current_day} 任务已完成 ({completed}/{target})")
            return

        # 获取今日目标产品
        products = self.get_todays_target_products()

        if not products:
            logger.warning("⚠️  未找到可互动的产品，请手动配置产品列表")
            return

        # 需要完成的互动次数
        remaining = target - completed

        # 设置浏览器
        if not self.commenter:
            self.commenter = ProductHuntCommenter()
            self.commenter.setup_browser(headless=False)

            if not self.commenter.verify_login():
                logger.error("❌ Product Hunt 未登录")
                return

        # 执行互动
        for i in range(remaining):
            if i >= len(products):
                logger.warning("⚠️  产品数量不足，请添加更多产品")
                break

            product = products[i]

            logger.info(f"\n互动 {i+1}/{remaining}: {product['name']}")

            # 生成评论
            comment = self.generate_warmup_comment(product)
            logger.info(f"   评论预览: {comment[:80]}...")

            # 发布评论（点赞 + 评论）
            success = self.commenter.comment_on_product(
                product_url=product['url'],
                comment_text=comment,
                upvote=True
            )

            if success:
                # 更新进度
                today_plan['completed'] += 1
                today_plan['products'].append(product['url'])
                self.progress['total_interactions'] += 1
                self.progress['total_upvotes'] += 1
                self.progress['total_comments'] += 1
                self._save_progress()

                logger.info("   ✅ 互动成功")
            else:
                logger.warning("   ⚠️  互动失败")

            # 随机延迟（避免被检测为机器人）
            if i < remaining - 1:
                delay = random.randint(300, 600)  # 5-10 分钟
                logger.info(f"   ⏳ 等待 {delay//60} 分钟后继续...")
                time.sleep(delay)

        logger.info(f"\n✅ Day {current_day} 任务完成！")
        self.show_warmup_status()

        # 关闭浏览器
        if self.commenter:
            self.commenter.close_browser()


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 账号养号脚本（7天计划）                          ║
╚════════════════════════════════════════════════════════════════╝

🎯 目标：
  • 建立社区信誉和活跃度
  • 熟悉 Product Hunt 文化
  • 为正式 Launch 做准备

📅 7天养号计划：
  Day 1-2: 每天 2 次互动（探索期）
  Day 3-5: 每天 3 次互动（活跃期）
  Day 6-7: 每天 4 次互动（冲刺期）

💬 互动策略：
  • 100% 真诚评论（不推销）
  • 点赞 + 评论组合
  • 专注相关类别产品
  • 建立社区存在感

⚠️  注意：
  • 新账号需等待 7 天才能发布产品
  • 或订阅 newsletter 可立即发布
  • 养号期间专注学习和贡献

🚀 完成养号后可以发布产品！
""")

    warmup = ProductHuntAccountWarmup()

    print("\n请选择操作：")
    print("  1. 查看养号进度")
    print("  2. 执行今日养号任务")
    print("  3. 退出")

    choice = input("\n请输入选项 (1-3): ")

    if choice == "1":
        warmup.show_warmup_status()

    elif choice == "2":
        warmup.run_daily_warmup()

    else:
        print("退出")
