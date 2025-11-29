#!/usr/bin/env python3
"""
生成Build in Public风格的Twitter内容
高质量原创，真实经验分享，数据驱动，启发性观点
"""
import os
from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_build_in_public_tweet():
    """生成单条build in public风格的tweet"""

    prompt = """You are the founder of HireMeAI (https://interviewasssistant.com), building in public on Twitter.

Generate a high-quality original tweet in ENGLISH with these requirements:
1. **Real experience sharing** - Share genuine stories about product development, user feedback, or technical challenges
2. **Data or insights** - Include specific numbers, test results, or valuable findings
3. **Thought-provoking perspective** - Provide new angles, counter-intuitive discoveries, or useful insights
4. **Natural product mention** - Don't hard-sell, make readers interested through context
5. **MUST include URL** - Naturally include https://interviewasssistant.com in the tweet

Topic ideas (choose one):
- Technical discoveries while building an AI interview assistant
- Real user feedback data and insights
- Interesting AI applications in interview preparation
- Startup failures and learnings
- Product iteration decisions and reasoning
- Observations about the interview industry

Style examples:
✅ "Just analyzed 100 users' interview prep data. Found something counter-intuitive: prep time ≠ success rate. The real key is..."
✅ "Week 3 of HireMeAI launch: conversion jumped from 2% to 15%. Changed only ONE thing: removed all fancy features, focused on solving one problem..."
✅ "Why do most AI interview assistants fail? Spent 3 months finding out. Hint: it's not a tech problem..."

❌ Avoid:
- Pure advertising "Our product is great, try it now!"
- Empty motivation "Just keep going"
- Claims without data

Format:
- **CRITICAL: Max 260 characters total (leaving buffer for safety)**
- MUST include https://interviewasssistant.com
- Use emoji sparingly (1-2 max)
- Add 1-2 relevant hashtags ONLY if they fit within character limit
- Be concise and impactful

Output ONLY the tweet text in ENGLISH, no title or extra explanation:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=150
    )

    tweet = response.choices[0].message.content.strip()

    # 确保包含URL
    if 'https://interviewasssistant.com' not in tweet:
        tweet += "\n\n👉 https://interviewasssistant.com"

    return tweet

def generate_daily_tweets(count=4):
    """生成一天的tweets"""
    tweets = []

    print(f"📝 生成 {count} 条Build in Public风格tweets...\n")

    for i in range(count):
        print(f"生成第 {i+1}/{count} 条...")
        tweet = generate_build_in_public_tweet()
        tweets.append(tweet)
        print(f"✅ 完成 ({len(tweet)} 字符)")
        print(f"内容: {tweet[:100]}...")
        print("-" * 80)

    return tweets

def save_tweets_schedule(tweets):
    """保存tweets到调度文件"""
    schedule = {
        "generated_at": datetime.now().isoformat(),
        "schedule": [
            {
                "time_slot": "09:00-10:00",
                "tweet": tweets[0],
                "posted": False
            },
            {
                "time_slot": "11:00-13:00",
                "tweet": tweets[1],
                "posted": False
            },
            {
                "time_slot": "13:00-15:00",
                "tweet": tweets[2],
                "posted": False
            },
            {
                "time_slot": "17:00-19:00",
                "tweet": tweets[3],
                "posted": False
            }
        ]
    }

    filename = f"twitter_schedule_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 调度文件已保存: {filename}")
    return filename

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 HireMeAI - Build in Public Tweet 生成器")
    print("=" * 80)
    print()

    # 生成4条tweets
    tweets = generate_daily_tweets(4)

    # 保存调度
    schedule_file = save_tweets_schedule(tweets)

    print("\n" + "=" * 80)
    print("📋 今日Tweet调度:")
    print("=" * 80)
    for i, tweet in enumerate(tweets, 1):
        time_slots = ["09:00-10:00", "11:00-13:00", "13:00-15:00", "17:00-19:00"]
        print(f"\n⏰ {time_slots[i-1]}")
        print(f"📝 {tweet}")
        print()

    print("=" * 80)
    print("✅ 准备完成！使用以下命令启动自动发布：")
    print(f"   python3 auto_tweet_scheduler.py {schedule_file}")
    print("=" * 80)
