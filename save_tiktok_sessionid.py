#!/usr/bin/env python3
"""
保存TikTok SessionID到配置文件
"""

import json

print("=" * 70)
print("🎵 Save TikTok SessionID")
print("=" * 70)

print("\n📋 步骤：")
print("   1. 在你的浏览器中访问 https://www.tiktok.com 并登录")
print("   2. 按 Cmd+Option+I 打开开发者工具")
print("   3. 点击 'Application' (或 'Storage') 标签")
print("   4. 左侧: Cookies → https://www.tiktok.com")
print("   5. 找到 'sessionid'，复制它的 Value")
print("\n")

sessionid = input("请粘贴你的 sessionid: ").strip()

if not sessionid:
    print("\n❌ SessionID不能为空！")
    exit(1)

if len(sessionid) < 20:
    print("\n⚠️  警告: SessionID看起来太短了")
    confirm = input("确定要继续吗？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        exit(1)

# 加载现有配置
try:
    with open('platforms_auth.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# 更新TikTok配置
if 'tiktok' not in config:
    config['tiktok'] = {}

config['tiktok']['sessionid'] = sessionid

# 保存
with open('platforms_auth.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("\n✅ SessionID已保存到 platforms_auth.json")
print(f"   长度: {len(sessionid)} 字符")
print(f"   预览: {sessionid[:20]}...{sessionid[-10:]}")

print("\n🎯 下一步:")
print("   运行: ./start_tiktok_campaign.sh")
print("\n")
