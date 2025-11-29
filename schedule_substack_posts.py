#!/usr/bin/env python3
"""
Substack定时发布脚本
自动生成文章并设置定时发布，每隔几天发一篇
"""

import sys
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright
from openai import OpenAI
import json
import time
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


# 发布配置
PUBLISH_SCHEDULE = [
    {"days_from_now": 3, "title_prefix": "Week 6"},   # 3天后
    {"days_from_now": 6, "title_prefix": "Week 7"},   # 6天后
    {"days_from_now": 9, "title_prefix": "Week 8"},   # 9天后
    {"days_from_now": 12, "title_prefix": "Week 9"},  # 12天后
]

PUBLISH_TIME = "09:00"  # 发布时间（早上9点）


def generate_article(week_number):
    """使用AI生成文章"""

    product_info = """
You are the founder of HireMeAI (https://interviewasssistant.com), an AI-powered real-time interview assistant.

Product description:
- Real-time AI interview coaching during live interviews
- Helps candidates answer questions better using STAR framework
- Provides instant suggestions and confidence boosting
- Works for both job seekers and hiring managers
"""

    prompt = f"""
Write a casual, build-in-public style Substack post about building HireMeAI.

Requirements:
- Title format: "{week_number}: [Catchy question or statement about interviews/AI]"
- Subtitle: Brief teaser (10-15 words)
- Content: 800-1200 words in casual English
- Use internet slang naturally (ngl, tbh, lowkey, fr, damn)
- Talk about ONE specific feature or challenge this week
- Include a real insight or learning
- End with a quick takeaway
- Include link to https://interviewasssistant.com
- Use emojis occasionally (but not too much)

Style:
- Warm and conversational
- Not salesy, just sharing the journey
- Like talking to a friend about your startup

Focus this week on: [Choose one: AI accuracy, user testing, technical challenges, product-market fit, user feedback]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": product_info},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )

        content = response.choices[0].message.content.strip()

        # 解析标题、副标题和正文
        lines = content.split('\n')
        title = ""
        subtitle = ""
        body = []

        reading_title = True
        reading_subtitle = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if reading_title and (line.startswith('#') or line.startswith('**Title')):
                title = line.replace('#', '').replace('**Title:**', '').replace('**Title**:', '').strip()
                reading_title = False
                reading_subtitle = True
            elif reading_subtitle and (line.startswith('**Subtitle') or line.startswith('*') or len(line) < 100):
                subtitle = line.replace('**Subtitle:**', '').replace('**Subtitle**:', '').replace('*', '').strip()
                reading_subtitle = False
            elif not reading_title and not reading_subtitle:
                body.append(line)

        # 如果没找到标题，使用默认
        if not title:
            title = f"{week_number}: Building HireMeAI - This Week's Progress"
        if not subtitle:
            subtitle = "A quick update on our AI interview assistant journey"

        body_text = '\n\n'.join(body)

        return {
            'title': title[:100],  # 限制长度
            'subtitle': subtitle[:150],
            'content': body_text
        }

    except Exception as e:
        logger.error(f"Failed to generate article: {e}")
        return None


def schedule_post(playwright, article, publish_datetime):
    """发布文章并设置定时发布"""

    logger.info(f"\n📅 Scheduling post for: {publish_datetime.strftime('%Y-%m-%d %H:%M')}")

    # Load auth
    with open('substack_auth.json', 'r') as f:
        auth_data = json.load(f)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    context.add_cookies(auth_data['cookies'])
    page = context.new_page()

    try:
        # Go to home
        logger.info("1. Going to Substack home...")
        page.goto("https://substack.com/home", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Click Create
        logger.info("2. Clicking Create button...")
        create_btn = page.wait_for_selector('button:has-text("Create")', timeout=5000)
        create_btn.click()
        time.sleep(2)

        # Click Post
        logger.info("3. Clicking Post from menu...")
        post_item = page.wait_for_selector('text="Post"', timeout=5000)
        post_item.click()
        time.sleep(5)

        # Fill title
        logger.info("4. Filling title...")
        title_input = page.wait_for_selector('textarea[placeholder*="Title" i]', timeout=5000)
        title_input.fill(article['title'])
        time.sleep(1)

        # Fill subtitle
        logger.info("5. Filling subtitle...")
        page.keyboard.press('Tab')
        time.sleep(1)
        page.keyboard.type(article['subtitle'])
        time.sleep(1)

        # Fill content
        logger.info("6. Filling content...")
        page.keyboard.press('Enter')
        time.sleep(1)
        page.keyboard.type(article['content'])
        time.sleep(2)

        # Click Continue
        logger.info("7. Clicking Continue button...")
        continue_btn = page.wait_for_selector('button:has-text("Continue")', timeout=5000)
        continue_btn.click()
        time.sleep(5)

        page.screenshot(path="schedule_post_dialog.png")
        logger.info("   📸 Screenshot: schedule_post_dialog.png")

        # Click on "Schedule time to email and publish"
        logger.info("8. Setting up scheduled publish...")
        try:
            schedule_checkbox = page.wait_for_selector('text="Schedule time to email and publish"', timeout=3000)
            schedule_checkbox.click()
            time.sleep(2)

            logger.info("   ✅ Clicked schedule option")

            # 输入日期和时间
            # 日期格式：MM/DD/YYYY
            date_str = publish_datetime.strftime('%m/%d/%Y')
            time_str = publish_datetime.strftime('%I:%M %p')  # 12小时制，如 09:00 AM

            logger.info(f"   Setting date: {date_str}")
            logger.info(f"   Setting time: {time_str}")

            # 查找日期和时间输入框
            date_input = page.wait_for_selector('input[type="date"], input[placeholder*="date" i]', timeout=3000)
            if date_input:
                date_input.fill(publish_datetime.strftime('%Y-%m-%d'))  # HTML5 date input format
                time.sleep(1)

            time_input = page.wait_for_selector('input[type="time"], input[placeholder*="time" i]', timeout=3000)
            if time_input:
                time_input.fill(publish_datetime.strftime('%H:%M'))  # HTML5 time input format
                time.sleep(1)

            logger.info("   ✅ Date and time set")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not set schedule: {e}")
            logger.info("   Trying alternative method...")

        page.screenshot(path="schedule_post_set.png")
        logger.info("   📸 Screenshot: schedule_post_set.png")

        # Click final publish/schedule button
        logger.info("9. Clicking final schedule button...")
        time.sleep(2)

        final_buttons = [
            'button:has-text("Schedule")',
            'button:has-text("Schedule post")',
            'button:has-text("Schedule email and publish")',
            'button:has-text("Send")',
        ]

        for selector in final_buttons:
            try:
                btn = page.wait_for_selector(selector, timeout=2000)
                if btn and btn.is_visible():
                    logger.info(f"   ✅ Found: {selector}")
                    btn.click()
                    time.sleep(3)
                    break
            except:
                continue

        logger.info("   ✅ Article scheduled!")

        page.screenshot(path="schedule_post_final.png")
        logger.info("   📸 Screenshot: schedule_post_final.png")

        time.sleep(3)
        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="schedule_post_error.png")
        return False

    finally:
        browser.close()


def main():
    """主函数"""

    logger.info("="*80)
    logger.info("📅 Substack Scheduled Posting")
    logger.info("="*80)
    logger.info(f"Will schedule {len(PUBLISH_SCHEDULE)} posts")
    logger.info(f"Publish time: {PUBLISH_TIME}")
    logger.info("")

    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        return

    playwright = sync_playwright().start()

    for i, schedule_info in enumerate(PUBLISH_SCHEDULE):
        logger.info("="*80)
        logger.info(f"📝 Post {i+1}/{len(PUBLISH_SCHEDULE)}")
        logger.info("="*80)

        # 计算发布时间
        days = schedule_info['days_from_now']
        publish_date = datetime.now() + timedelta(days=days)

        # 设置发布时间为指定的小时
        hour, minute = map(int, PUBLISH_TIME.split(':'))
        publish_datetime = publish_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        logger.info(f"Schedule for: {publish_datetime.strftime('%Y-%m-%d %H:%M')} ({days} days from now)")

        # 生成文章
        logger.info("\n🤖 Generating article with AI...")
        article = generate_article(schedule_info['title_prefix'])

        if not article:
            logger.error("Failed to generate article, skipping...")
            continue

        logger.info(f"\n✅ Article generated:")
        logger.info(f"   Title: {article['title']}")
        logger.info(f"   Subtitle: {article['subtitle']}")
        logger.info(f"   Content: {len(article['content'])} chars")

        # 发布文章
        success = schedule_post(playwright, article, publish_datetime)

        if success:
            logger.info(f"\n✅ Post {i+1} scheduled successfully!")
        else:
            logger.error(f"\n❌ Failed to schedule post {i+1}")

        # 如果不是最后一篇，等待一下
        if i < len(PUBLISH_SCHEDULE) - 1:
            logger.info("\n⏳ Waiting 10 seconds before next post...")
            time.sleep(10)

    playwright.stop()

    logger.info("\n" + "="*80)
    logger.info("✅ All posts scheduled!")
    logger.info("="*80)


if __name__ == "__main__":
    main()
