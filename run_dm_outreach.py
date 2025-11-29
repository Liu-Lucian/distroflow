#!/usr/bin/env python3
"""
批量DM发送系统 - 读取qualified_users.json并批量发送
"""

import sys
sys.path.append('src')

import json
import os
import time
import random
from datetime import datetime

from reddit_dm_sender import RedditDMSender
from twitter_dm_sender import TwitterDMSender

print("=" * 70)
print("📬 Batch DM Outreach System")
print("=" * 70)

# ==================== 配置 ====================

QUALIFIED_USERS_FILE = "qualified_users.json"

MESSAGE_TEMPLATE = """Hey {{name}}, I saw your comment about {{topic}} — really insightful!

I'm building HireMeAI (https://interviewasssistant.com), it helps with interview prep using AI feedback and practice simulations.

{{pain_point_mention}}

Would love to get your thoughts if you're open to it!"""

# 每个平台每次发送的数量
BATCH_SIZE = {
    'reddit': 5,  # Reddit每次发5条
    'twitter': 3,  # Twitter每次发3条
}

# 发送间隔
DELAY_BETWEEN_MESSAGES = (60, 180)  # 1-3分钟随机
DELAY_BETWEEN_PLATFORMS = (300, 600)  # 5-10分钟

# ==================== 辅助函数 ====================

def log(message):
    """带时间戳的日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def load_users():
    """加载用户列表"""
    if not os.path.exists(QUALIFIED_USERS_FILE):
        log(f"❌ {QUALIFIED_USERS_FILE} not found")
        log("   Run `python3 run_smart_campaign.py` first to find users")
        return []

    with open(QUALIFIED_USERS_FILE, 'r') as f:
        return json.load(f)


def save_users(users):
    """保存用户列表"""
    with open(QUALIFIED_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def format_message(template: str, user: dict) -> str:
    """格式化消息"""
    name = user.get('username', 'there')
    topic = user.get('pain_points', ['interview prep'])[0] if user.get('pain_points') else 'interview prep'

    # Pain point mention
    pain_point_mention = ""
    if user.get('pain_points') and len(user['pain_points']) > 0:
        pain_point_mention = f"I noticed you mentioned challenges with {user['pain_points'][0]}. Our AI tool specifically helps with that!"

    message = template.replace('{{name}}', name)
    message = template.replace('{{topic}}', topic)
    message = template.replace('{{pain_point_mention}}', pain_point_mention)

    return message


# ==================== 主流程 ====================

def main():
    """主DM发送流程"""

    log("Loading users...")

    all_users = load_users()

    if not all_users:
        log("❌ No users to process")
        return

    # 过滤未发送的用户
    unsent_users = [u for u in all_users if not u.get('sent_dm', False)]

    log(f"📋 Total users: {len(all_users)}")
    log(f"📬 Unsent DMs: {len(unsent_users)}")

    if not unsent_users:
        log("✅ All users have been contacted!")
        return

    # 按平台分组
    users_by_platform = {}
    for user in unsent_users:
        platform = user.get('platform', 'reddit')
        if platform not in users_by_platform:
            users_by_platform[platform] = []
        users_by_platform[platform].append(user)

    log("\n📊 Users by platform:")
    for platform, users in users_by_platform.items():
        log(f"   {platform}: {len(users)} users")

    # 按优先级排序
    for platform in users_by_platform:
        users_by_platform[platform].sort(
            key=lambda u: (
                0 if u.get('priority') == 'high' else
                1 if u.get('priority') == 'medium' else 2,
                -u.get('intent_score', 0)
            )
        )

    log("\n🚀 Starting DM outreach...")

    # 初始化senders
    senders = {}
    if 'reddit' in users_by_platform:
        try:
            senders['reddit'] = RedditDMSender()
            log("✅ Reddit sender initialized")
        except Exception as e:
            log(f"⚠️ Reddit sender failed: {e}")

    if 'twitter' in users_by_platform:
        try:
            senders['twitter'] = TwitterDMSender()
            log("✅ Twitter sender initialized")
        except Exception as e:
            log(f"⚠️ Twitter sender failed: {e}")

    # 统计
    total_sent = 0
    total_failed = 0

    try:
        # 遍历每个平台
        for platform, users in users_by_platform.items():
            if platform not in senders:
                log(f"\n⏭️ Skipping {platform} (sender not available)")
                continue

            log(f"\n📱 Platform: {platform.upper()}")

            # 获取这次要发送的用户（按batch size限制）
            batch_size = BATCH_SIZE.get(platform, 5)
            users_to_send = users[:batch_size]

            log(f"   Sending to {len(users_to_send)} users (batch size: {batch_size})")

            sender = senders[platform]

            for i, user in enumerate(users_to_send, 1):
                username = user.get('username')
                log(f"\n   [{i}/{len(users_to_send)}] Sending to @{username}...")
                log(f"      Priority: {user.get('priority', 'N/A')}")
                log(f"      Intent Score: {user.get('intent_score', 0):.2f}")

                # 格式化消息
                message = format_message(MESSAGE_TEMPLATE, user)

                log(f"      Message preview: {message[:80]}...")

                try:
                    # 发送DM
                    success = sender.send_dm(user, message)

                    if success:
                        log(f"      ✅ Sent successfully")
                        user['sent_dm'] = True
                        user['sent_date'] = datetime.now().isoformat()
                        total_sent += 1

                        # 立即保存进度
                        save_users(all_users)
                    else:
                        log(f"      ❌ Failed to send")
                        total_failed += 1

                    # 随机延迟
                    if i < len(users_to_send):
                        delay = random.randint(*DELAY_BETWEEN_MESSAGES)
                        log(f"      ⏳ Waiting {delay}s before next message...")
                        time.sleep(delay)

                except Exception as e:
                    log(f"      ❌ Error: {e}")
                    total_failed += 1

            # 清理sender
            try:
                sender.cleanup()
            except:
                pass

            # 平台之间的延迟
            remaining_platforms = list(users_by_platform.keys())
            current_index = remaining_platforms.index(platform)
            if current_index < len(remaining_platforms) - 1:
                delay = random.randint(*DELAY_BETWEEN_PLATFORMS)
                log(f"\n⏸️ Switching platform in {delay//60} minutes...")
                time.sleep(delay)

    except KeyboardInterrupt:
        log("\n\n⚠️ Outreach stopped by user (Ctrl+C)")
        log("Progress has been saved")

    except Exception as e:
        log(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 最终统计
        log("\n" + "=" * 70)
        log("📊 FINAL STATISTICS")
        log("=" * 70)
        log(f"Total Sent: {total_sent}")
        log(f"Total Failed: {total_failed}")

        remaining = len([u for u in all_users if not u.get('sent_dm', False)])
        log(f"Remaining: {remaining}")

        log("=" * 70)
        log("\n✅ Outreach session completed")


if __name__ == "__main__":
    main()
