#!/usr/bin/env python3
"""
LinkedIn DM发送 - 使用已有用户列表
跳过搜索，直接发送私信
"""

import sys
sys.path.append('src')

import json
import time
import random
from datetime import datetime
from linkedin_dm_sender import LinkedInDMSender

print("=" * 70)
print("💼 LinkedIn DM Sender - From User List")
print("=" * 70)

# ==================== 配置 ====================

# 产品信息
PRODUCT_NAME = "HireMeAI"
PRODUCT_URL = "https://interviewasssistant.com"
PRODUCT_DESCRIPTION = "AI-powered interview preparation platform"

# 消息模板
MESSAGE_TEMPLATE = """Hi {name},

I came across your profile and wanted to reach out.

I'm building {product_name} ({product_url}), an {product_description}.

{custom_message}

Would love to get your thoughts if you're open to a quick chat!

Best regards"""

# 目标用户列表文件
USERS_FILE = "linkedin_target_users.json"
PROGRESS_FILE = "linkedin_dm_progress.json"

# DM配置
DM_DELAY = (120, 180)  # 2-3分钟延迟（更保守）
BATCH_SIZE = 3  # 每次运行发送3个

# ==================== 辅助函数 ====================

def load_target_users():
    """加载目标用户列表"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"\n⚠️  找不到文件: {USERS_FILE}")
        print("\n💡 创建示例文件...")

        # 创建示例文件
        example_users = [
            {
                "name": "John Doe",
                "profile_url": "https://www.linkedin.com/in/johndoe/",
                "headline": "Recruiting Manager at TechCorp",
                "custom_message": "I noticed you work in tech recruiting. Our platform helps candidates prepare better for technical interviews.",
                "sent_dm": False
            },
            {
                "name": "Jane Smith",
                "profile_url": "https://www.linkedin.com/in/janesmith/",
                "headline": "Talent Acquisition Lead",
                "custom_message": "I saw your background in talent acquisition. Would love to hear your thoughts on AI-assisted interview prep.",
                "sent_dm": False
            }
        ]

        with open(USERS_FILE, 'w') as f:
            json.dump(example_users, f, indent=2, ensure_ascii=False)

        print(f"✅ 已创建示例文件: {USERS_FILE}")
        print("\n📝 请编辑这个文件，添加你的目标用户：")
        print(f"   1. 打开 {USERS_FILE}")
        print("   2. 替换示例用户为真实的LinkedIn URLs")
        print("   3. 重新运行此脚本")
        return None

def load_progress():
    """加载进度"""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'total_sent': 0,
            'total_failed': 0,
            'last_run': None,
            'sent_urls': []
        }

def save_progress(progress):
    """保存进度"""
    progress['last_run'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def save_users(users):
    """保存用户列表"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# ==================== 主流程 ====================

def main():
    """主流程"""

    # 加载用户列表
    users = load_target_users()
    if users is None:
        return

    # 加载进度
    progress = load_progress()

    print(f"\n📊 统计信息:")
    print(f"   总用户数: {len(users)}")

    # 筛选未发送的用户
    unsent_users = [u for u in users if not u.get('sent_dm', False)]
    print(f"   待发送: {len(unsent_users)}")
    print(f"   历史成功: {progress['total_sent']}")
    print(f"   历史失败: {progress['total_failed']}")

    if not unsent_users:
        print("\n✅ 所有用户都已发送DM!")
        return

    # 本次批量
    batch = unsent_users[:BATCH_SIZE]
    print(f"\n📬 本次发送: {len(batch)} 个用户")

    # 确认
    print("\n" + "=" * 70)
    print("将要发送给以下用户:")
    for i, user in enumerate(batch, 1):
        print(f"\n[{i}] {user['name']}")
        print(f"    职位: {user.get('headline', 'N/A')}")
        print(f"    链接: {user['profile_url']}")

    print("\n" + "=" * 70)
    confirm = input("\n确认发送? (输入 'yes' 继续): ")

    if confirm.lower() != 'yes':
        print("\n❌ 已取消")
        return

    # 初始化DM发送器
    print("\n🚀 启动LinkedIn DM发送器...")
    sender = LinkedInDMSender("linkedin_auth.json")

    # 发送DM
    print("\n" + "=" * 70)
    print("💬 开始发送DM")
    print("=" * 70)

    for i, user in enumerate(batch, 1):
        print(f"\n[{i}/{len(batch)}] {user['name']}")

        # 构建消息
        custom_msg = user.get('custom_message',
            f"I noticed your background in {user.get('headline', 'your field')}.")

        message = MESSAGE_TEMPLATE.format(
            name=user['name'].split()[0],  # 使用名字
            product_name=PRODUCT_NAME,
            product_url=PRODUCT_URL,
            product_description=PRODUCT_DESCRIPTION,
            custom_message=custom_msg
        )

        print(f"   📝 消息预览:")
        print(f"   {'-' * 60}")
        for line in message.split('\n')[:3]:  # 显示前3行
            print(f"   {line}")
        print(f"   ...")
        print(f"   {'-' * 60}")

        # 发送
        try:
            success = sender.send_message(
                user_profile_url=user['profile_url'],
                message=message
            )

            if success:
                print(f"   ✅ 发送成功!")
                user['sent_dm'] = True
                user['sent_date'] = datetime.now().isoformat()
                progress['total_sent'] += 1
                progress['sent_urls'].append(user['profile_url'])
            else:
                print(f"   ❌ 发送失败")
                progress['total_failed'] += 1

        except Exception as e:
            print(f"   ❌ 错误: {e}")
            progress['total_failed'] += 1

        # 保存进度
        save_users(users)
        save_progress(progress)

        # 延迟（最后一个不需要）
        if i < len(batch):
            delay = random.randint(*DM_DELAY)
            print(f"\n   ⏳ 等待 {delay//60}分{delay%60}秒...")
            time.sleep(delay)

    # 清理
    sender.cleanup()

    # 最终统计
    print("\n" + "=" * 70)
    print("✅ 发送完成!")
    print("=" * 70)
    print(f"\n📊 本次统计:")
    print(f"   成功: {sum(1 for u in batch if u.get('sent_dm', False))}")
    print(f"   失败: {len(batch) - sum(1 for u in batch if u.get('sent_dm', False))}")

    print(f"\n📊 总体进度:")
    print(f"   已发送: {progress['total_sent']}/{len(users)}")
    print(f"   剩余: {len([u for u in users if not u.get('sent_dm', False)])}")

    print(f"\n📁 文件保存:")
    print(f"   用户列表: {USERS_FILE}")
    print(f"   进度记录: {PROGRESS_FILE}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
