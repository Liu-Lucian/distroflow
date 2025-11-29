#!/usr/bin/env python3
"""
测试 Hacker News 自动回答系统的设置
验证：
1. Anthropic API key 是否设置
2. HN 认证是否有效
3. 能否获取首页帖子
4. Claude API 是否正常工作
"""
import sys
sys.path.insert(0, 'src')

from hackernews_commenter import HackerNewsCommenter
import os
from anthropic import Anthropic

print("=" * 80)
print("🧪 Hacker News 自动回答系统 - 设置测试")
print("=" * 80)
print()

# 1. 检查 API key
print("1️⃣  检查 Anthropic API key...")
api_key = os.environ.get('ANTHROPIC_API_KEY')
if api_key:
    print(f"   ✅ API key 已设置: {api_key[:20]}...")
else:
    print("   ❌ API key 未设置")
    print("\n请先设置:")
    print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'")
    exit(1)

# 2. 测试 Claude API
print("\n2️⃣  测试 Claude API 连接...")
try:
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'API test successful' in 3 words"}]
    )
    response = message.content[0].text
    print(f"   ✅ Claude API 正常: {response}")
except Exception as e:
    print(f"   ❌ Claude API 错误: {str(e)}")
    exit(1)

# 3. 测试 HN 认证
print("\n3️⃣  测试 Hacker News 认证...")
commenter = HackerNewsCommenter()

try:
    commenter.setup_browser(headless=True)

    if commenter.verify_login():
        print("   ✅ HN 登录验证成功")
    else:
        print("   ❌ HN 登录验证失败")
        print("\n请先运行:")
        print("  python3 hackernews_login_and_save_auth.py")
        commenter.close_browser()
        exit(1)

    # 4. 测试获取首页帖子
    print("\n4️⃣  测试获取 HN 首页帖子...")
    stories = commenter.get_frontpage_stories(limit=5)

    if stories:
        print(f"   ✅ 成功获取 {len(stories)} 个帖子")
        print("\n   示例帖子:")
        for i, story in enumerate(stories[:3], 1):
            print(f"      {i}. {story['title'][:60]}...")
            print(f"         👍 {story['points']} | 💬 {story['comments']}")
    else:
        print("   ❌ 获取帖子失败")
        commenter.close_browser()
        exit(1)

    print("\n" + "=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)
    print("\n可以开始运行:")
    print("  python3 hackernews_auto_reply.py")
    print()

except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    commenter.close_browser()
