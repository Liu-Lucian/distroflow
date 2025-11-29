#!/usr/bin/env python3
"""
Instagram自动发布系统 - Build in Public永久运行版
每周自动生成1-2条Build in Public风格Instagram帖子并发布
包含AI生成的图片和3段式Caption
"""
import sys
sys.path.insert(0, 'src')
from instagram_poster import InstagramPoster
import os
from openai import OpenAI
import json
import time
import logging
from datetime import datetime, timedelta
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class InstagramForeverBot:
    def __init__(self):
        self.poster = None
        self.images_dir = "instagram_images"
        os.makedirs(self.images_dir, exist_ok=True)

        # 统计发布天数
        self.progress_file = "instagram_build_progress.json"
        self.load_progress()

    def load_progress(self):
        """加载Build in Public进度"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self.days_count = data.get('days_count', 0)
                self.start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        else:
            self.days_count = 0
            self.start_date = datetime.now().strftime('%Y-%m-%d')
            self.save_progress()

    def save_progress(self):
        """保存进度"""
        with open(self.progress_file, 'w') as f:
            json.dump({
                'days_count': self.days_count,
                'start_date': self.start_date,
                'last_post': datetime.now().isoformat()
            }, f, indent=2)

    def increment_day(self):
        """增加天数计数"""
        self.days_count += 1
        self.save_progress()
        return self.days_count

    def generate_post_image(self, day_number, title_text="Building HireMeAI"):
        """
        生成Instagram帖子图片 - 简洁的"Day X"风格

        Args:
            day_number: 第几天
            title_text: 标题文本

        Returns:
            图片路径
        """
        logger.info(f"🎨 生成第 {day_number} 天的图片...")

        # Instagram推荐尺寸: 1080x1080 (正方形)
        width, height = 1080, 1080

        # 创建渐变背景（深蓝到紫色）
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # 添加渐变效果
        for i in range(height):
            # 从深蓝 #1a1a2e 渐变到深紫 #16213e
            r = int(26 + (22 - 26) * i / height)
            g = int(26 + (33 - 26) * i / height)
            b = int(46 + (62 - 46) * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        # 加载字体（尝试使用系统字体）
        try:
            # macOS系统字体
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 120)
            day_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 180)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 48)
        except:
            try:
                # 尝试其他字体
                title_font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 120)
                day_font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 180)
                subtitle_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 48)
            except:
                # 使用默认字体
                logger.warning("   ⚠️  未找到系统字体，使用默认字体")
                title_font = ImageFont.load_default()
                day_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

        # 绘制"DAY X"（中心大字）
        day_text = f"DAY {day_number}"

        # 获取文本边界框（使用getbbox而不是废弃的textsize）
        day_bbox = draw.textbbox((0, 0), day_text, font=day_font)
        day_width = day_bbox[2] - day_bbox[0]
        day_height = day_bbox[3] - day_bbox[1]

        day_x = (width - day_width) // 2
        day_y = height // 2 - 150

        # 添加文字阴影
        shadow_offset = 4
        draw.text((day_x + shadow_offset, day_y + shadow_offset), day_text,
                 font=day_font, fill='#000000')
        # 主文字（白色）
        draw.text((day_x, day_y), day_text, font=day_font, fill='#ffffff')

        # 绘制标题
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = day_y + day_height + 40

        draw.text((title_x + 3, title_y + 3), title_text, font=title_font, fill='#000000')
        draw.text((title_x, title_y), title_text, font=title_font, fill='#00d9ff')

        # 绘制副标题
        subtitle = "AI-Powered Interview Assistant"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 140

        draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill='#aaaaaa')

        # 添加URL（底部）
        url_text = "interviewasssistant.com"
        url_bbox = draw.textbbox((0, 0), url_text, font=subtitle_font)
        url_width = url_bbox[2] - url_bbox[0]
        url_x = (width - url_width) // 2
        url_y = height - 100

        draw.text((url_x, url_y), url_text, font=subtitle_font, fill='#ffffff')

        # 保存图片
        image_path = os.path.join(self.images_dir, f"day_{day_number}.png")
        img.save(image_path)
        logger.info(f"   ✅ 图片已保存: {image_path}")

        return image_path

    def generate_build_in_public_caption(self):
        """生成Build in Public风格的Instagram caption（3段式）"""

        prompt = """You are the founder of HireMeAI (https://interviewasssistant.com), sharing your Build in Public journey on Instagram.

Generate an authentic, engaging Instagram caption in ENGLISH using the 3-paragraph structure:

**Paragraph 1 (Background/Problem):**
- Set the context or share the problem you're solving
- Make it relatable to job seekers, tech professionals, or founders
- 2-3 sentences

**Paragraph 2 (What I'm Doing):**
- Share what you're building/testing/learning this week
- Include specific details, numbers, or insights
- Show the process, not just the result
- 3-4 sentences

**Paragraph 3 (Current Progress & CTA):**
- Share current metrics, wins, or challenges
- End with a question or call-to-action to boost engagement
- 2-3 sentences

**Requirements:**
1. Tone: Authentic, humble, relatable (not salesy)
2. Length: 400-800 characters (Instagram sweet spot)
3. Must include: HireMeAI, https://interviewasssistant.com
4. Use 1-2 emojis max (natural placement)
5. End with engaging question to encourage comments

**Topic ideas** (choose one):
- Weekly progress update (users, features, insights)
- Technical challenge and how you solved it
- User feedback that changed your roadmap
- Startup life reality check (failure/learning)
- Industry observation about interviews/hiring
- Behind-the-scenes of building AI product

**Caption Style Examples:**

✅ Good:
"Most AI interview tools fail because they optimize for the wrong thing.

We spent 2 weeks analyzing 500+ user sessions on HireMeAI. Found something surprising: users who practiced LESS but got better feedback scored 40% higher in real interviews.

So we're rebuilding our feedback engine from scratch. It's painful, but necessary.

If you could fix ONE thing about interview prep, what would it be? 🤔

👉 https://interviewasssistant.com"

❌ Avoid:
- Pure promotion
- Fake motivational quotes
- Vague updates without specifics

Output ONLY the caption text (no hashtags - I'll add them separately):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=400
        )

        caption = response.choices[0].message.content.strip()

        # 确保包含URL
        if 'https://interviewasssistant.com' not in caption:
            caption += "\n\n👉 https://interviewasssistant.com"

        return caption

    def generate_hashtags(self):
        """生成Instagram hashtags（8-12个）"""
        # 固定的核心hashtags
        core_hashtags = [
            '#buildinpublic',
            '#AIstartup',
            '#founderjourney',
            '#indiehacker'
        ]

        # 可选的相关hashtags（随机选择4-8个）
        optional_hashtags = [
            '#技术创业',
            '#AI面试',
            '#职场',
            '#求职',
            '#startuplife',
            '#techfounder',
            '#ProductDevelopment',
            '#AItools',
            '#careeradvice',
            '#interviewprep',
            '#techcareers',
            '#创业者'
        ]

        # 随机选择4-8个可选hashtags
        selected = random.sample(optional_hashtags, random.randint(4, 8))

        all_hashtags = core_hashtags + selected

        return ' '.join(all_hashtags)

    def generate_weekly_schedule(self, target_week_start=None):
        """
        生成一周的Instagram帖子调度（1-2个帖子）

        Args:
            target_week_start: 目标周的开始日期（周一）

        Returns:
            (filename, schedule)
        """
        if target_week_start is None:
            # 计算本周一
            today = datetime.now()
            days_since_monday = today.weekday()  # 0=Monday, 6=Sunday
            target_week_start = today - timedelta(days=days_since_monday)

        week_str = target_week_start.strftime('%Y%m%d')
        logger.info(f"📝 生成第 {week_str} 周的Instagram Build in Public帖子...")

        # 生成1-2个帖子
        num_posts = random.choice([1, 2])  # 随机1或2个
        logger.info(f"   本周计划发布 {num_posts} 个帖子")

        posts = []
        for i in range(num_posts):
            logger.info(f"   生成第 {i+1}/{num_posts} 个帖子...")

            # 增加天数计数
            day_number = self.increment_day()

            # 生成图片
            image_path = self.generate_post_image(day_number)

            # 生成caption
            caption = self.generate_build_in_public_caption()

            # 生成hashtags
            hashtags = self.generate_hashtags()

            logger.info(f"   ✅ 帖子 {i+1} 完成 (Day {day_number})")

            posts.append({
                'day_number': day_number,
                'image_path': image_path,
                'caption': caption,
                'hashtags': hashtags
            })

            time.sleep(1)  # 避免API限流

        # 创建调度（周三和周日）
        schedule_slots = []

        if num_posts >= 1:
            # 第一个帖子：周三 10:00-12:00
            wednesday = target_week_start + timedelta(days=2)  # 周三
            schedule_slots.append({
                'date': wednesday.strftime('%Y-%m-%d'),
                'time_slot': '10:00-12:00',
                'post': posts[0],
                'posted': False
            })

        if num_posts >= 2:
            # 第二个帖子：周日 15:00-17:00
            sunday = target_week_start + timedelta(days=6)  # 周日
            schedule_slots.append({
                'date': sunday.strftime('%Y-%m-%d'),
                'time_slot': '15:00-17:00',
                'post': posts[1],
                'posted': False
            })

        schedule = {
            'generated_at': datetime.now().isoformat(),
            'week_start': target_week_start.strftime('%Y-%m-%d'),
            'schedule': schedule_slots
        }

        filename = f"instagram_schedule_{week_str}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ 调度文件已保存: {filename}")
        return filename, schedule

    def load_or_generate_this_week_schedule(self):
        """加载或生成本周的调度"""
        today = datetime.now()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_str = week_start.strftime('%Y%m%d')

        filename = f"instagram_schedule_{week_str}.json"

        if os.path.exists(filename):
            logger.info(f"📖 加载已有调度文件: {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                schedule = json.load(f)
            return filename, schedule
        else:
            logger.info(f"🆕 未找到本周调度，生成新的...")
            return self.generate_weekly_schedule(week_start)

    def save_schedule(self, filename, schedule):
        """保存调度文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

    def is_in_time_slot(self, date_str, time_slot_str):
        """检查当前时间是否在指定日期和时间段内"""
        now = datetime.now()

        # 检查日期
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if now.date() != target_date:
            return False

        # 检查时间
        current_time = now.time()
        start_str, end_str = time_slot_str.split('-')
        start_hour, start_min = map(int, start_str.split(':'))
        end_hour, end_min = map(int, end_str.split(':'))

        start_time = datetime.now().replace(hour=start_hour, minute=start_min, second=0).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_min, second=0).time()

        return start_time <= current_time <= end_time

    def post_single_instagram(self, post_data):
        """发布单个Instagram帖子"""
        try:
            if not self.poster:
                self.poster = InstagramPoster()
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    raise Exception("Instagram登录验证失败")

            # 构造Instagram content格式
            content = {
                'caption': post_data['caption'],
                'hashtags': post_data['hashtags']
            }

            # 发布
            success = self.poster.create_post(content, image_paths=[post_data['image_path']])

            if success:
                logger.info(f"✅ Instagram帖子发布成功！(Day {post_data['day_number']})")
                logger.info(f"   Caption: {post_data['caption'][:100]}...")
                return True
            else:
                logger.error("❌ Instagram发布失败")
                return False

        except Exception as e:
            logger.error(f"❌ 发布错误: {str(e)}")
            return False

    def run_week_schedule(self, filename, schedule):
        """运行本周的调度"""
        logger.info("\n📋 本周调度:")
        for item in schedule['schedule']:
            status = "✅ 已发布" if item['posted'] else "⏳ 待发布"
            logger.info(f"   {item['date']} {item['time_slot']}: {status}")
            logger.info(f"      Day {item['post']['day_number']}")
            logger.info(f"      {item['post']['caption'][:80]}...")

        logger.info("\n⏰ 开始监控，将在指定时间段自动发布...")

        while True:
            now = datetime.now()

            # 检查是否已经进入下周
            days_since_monday = now.weekday()
            current_week_start = now - timedelta(days=days_since_monday)
            current_week_str = current_week_start.strftime('%Y%m%d')
            expected_filename = f"instagram_schedule_{current_week_str}.json"

            if filename != expected_filename:
                logger.info("\n" + "=" * 80)
                logger.info("📅 已进入新的一周，退出当前调度...")
                logger.info("=" * 80)
                break

            # 检查每个时间段
            for item in schedule['schedule']:
                if not item['posted'] and self.is_in_time_slot(item['date'], item['time_slot']):
                    logger.info(f"\n{'='*80}")
                    logger.info(f"⏰ 时间到！{item['date']} {item['time_slot']}")
                    logger.info(f"{'='*80}")

                    # 在时间段内随机延迟
                    random_delay = random.randint(1, 600)  # 0-10分钟
                    logger.info(f"⏳ 随机延迟 {random_delay//60} 分钟，使发布更自然...")
                    time.sleep(random_delay)

                    logger.info(f"📤 发布Instagram帖子 (Day {item['post']['day_number']})...")
                    success = self.post_single_instagram(item['post'])

                    if success:
                        item['posted'] = True
                        item['posted_at'] = datetime.now().isoformat()
                        self.save_schedule(filename, schedule)
                        logger.info("✅ 状态已保存")

                    # 发布后等待
                    time.sleep(120)

            # 检查是否所有都已发布
            all_posted = all(item['posted'] for item in schedule['schedule'])
            if all_posted:
                logger.info("\n" + "=" * 80)
                logger.info("🎉 本周所有Instagram帖子已发布完成！")
                logger.info("=" * 80)
                break

            # 每10分钟检查一次
            time.sleep(600)

    def run_forever(self):
        """永久运行"""
        logger.info("=" * 80)
        logger.info("🚀 Instagram Build in Public自动发布系统")
        logger.info("=" * 80)
        logger.info("功能:")
        logger.info("  • 每周自动生成1-2条Build in Public风格帖子")
        logger.info("  • AI生成图片（Day X风格）")
        logger.info("  • AI生成Caption（3段式结构）")
        logger.info("  • 自动添加8-12个hashtags")
        logger.info("  • 在指定时间段自动发布（周三、周日）")
        logger.info("  • 本周发布完成后自动生成下周内容")
        logger.info("=" * 80)
        logger.info(f"当前进度: Day {self.days_count}")
        logger.info(f"开始日期: {self.start_date}")
        logger.info("=" * 80)
        logger.info("按Ctrl+C停止\n")

        try:
            while True:
                # 加载或生成本周的调度
                filename, schedule = self.load_or_generate_this_week_schedule()

                # 运行本周的调度
                self.run_week_schedule(filename, schedule)

                # 本周发完了，等待到下周一
                now = datetime.now()
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7

                next_monday = (now + timedelta(days=days_until_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                wait_seconds = (next_monday - now).total_seconds()

                logger.info(f"\n⏳ 本周任务完成，等待 {wait_seconds/3600:.1f} 小时到下周...")
                logger.info(f"   将在 {next_monday.strftime('%Y-%m-%d %H:%M:%S')} 生成新的帖子\n")

                time.sleep(wait_seconds + 60)  # 多等1分钟确保进入新周

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断...")
        finally:
            if self.poster:
                logger.info("🔒 关闭浏览器...")
                try:
                    self.poster.close_browser()
                except Exception as e:
                    if "Connection closed" not in str(e):
                        logger.warning(f"⚠️  关闭浏览器时出现错误（已忽略）: {str(e)}")

            logger.info("\n✅ 系统已停止")

if __name__ == "__main__":
    bot = InstagramForeverBot()
    bot.run_forever()
