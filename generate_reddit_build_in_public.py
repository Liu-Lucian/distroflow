#!/usr/bin/env python3
"""
生成Reddit Build in Public风格的帖子
适合r/Startups, r/ArtificialIntelligence, r/EntrepreneurRideAlong等板块
"""
import os
from openai import OpenAI
import json
from datetime import datetime
import random

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_reddit_post(post_type="progress"):
    """生成单个Reddit Build in Public帖子

    post_type可以是：
    - progress: 进展更新
    - technical: 技术挑战
    - story: 创业故事
    - learning: 经验教训
    - milestone: 里程碑
    """

    # 根据类型选择不同的prompt
    prompts = {
        "progress": """Generate a Reddit post for r/Startups in "build in public" style about HireMeAI (https://interviewasssistant.com).

Post Type: Weekly/Monthly Progress Update

Requirements:
1. **Title**: Hook that mentions progress/milestone (40-80 chars)
   Example: "Week 5 building an AI interview coach - here's what I learned"

2. **Body Structure**:
   - Hook (1-2 sentences): Grab attention with a result or insight
   - Background (2-3 sentences): Why building this / what problem solving
   - This Week's Progress (3-5 bullet points): Concrete accomplishments with metrics
   - Challenges (2-3 bullet points): Real problems faced
   - Next Steps (1-2 bullet points): What's coming
   - Call to Action: Ask for feedback/advice (friendly, not salesy)

3. **Style**:
   - Honest and transparent
   - Use specific numbers/data
   - Show both wins and struggles
   - Conversational tone
   - NO promotional language
   - MUST include https://interviewasssistant.com naturally

4. **About HireMeAI**:
   - AI-powered real-time interview assistant
   - Uses speech recognition + NLP + ChromaDB
   - Provides real-time answer suggestions during interviews
   - Goal: boost confidence through AI-powered practice

Output format:
TITLE: [your title]

BODY:
[your body text]

SUBREDDIT: r/Startups""",

        "technical": """Generate a Reddit post for r/ArtificialIntelligence in "build in public" style about HireMeAI (https://interviewasssistant.com).

Post Type: Technical Challenge & Solution

Requirements:
1. **Title**: Specific technical problem (50-90 chars)
   Example: "How I reduced real-time speech recognition latency to <1s in my AI app"

2. **Body Structure**:
   - The Problem (2-3 sentences): What technical challenge you faced
   - Why It Matters (1-2 sentences): Impact on product/users
   - Solution Approach (4-6 bullet points): What you tried, what worked
   - Results (2-3 sentences): Metrics/improvements
   - Lessons Learned (2-3 sentences): Key takeaways
   - Ask for Input: Invite technical discussion

3. **Style**:
   - Technical but accessible
   - Show your learning process
   - Admit mistakes/iterations
   - Include specific tech stack details
   - MUST include https://interviewasssistant.com

4. **Tech Stack to Reference**:
   - Azure Speech SDK / OpenAI Whisper
   - GPT-4o for answer generation
   - ChromaDB for semantic matching
   - Real-time streaming architecture

Output format:
TITLE: [your title]

BODY:
[your body text]

SUBREDDIT: r/ArtificialIntelligence""",

        "story": """Generate a Reddit post for r/EntrepreneurRideAlong in "build in public" style about HireMeAI (https://interviewasssistant.com).

Post Type: Founder Story / Journey

Requirements:
1. **Title**: Personal hook with emotion (40-80 chars)
   Example: "From interview anxiety to building an AI coach - my journey"

2. **Body Structure**:
   - Personal Hook (2-3 sentences): Your story/pain point
   - The Idea (2-3 sentences): How solution came about
   - Building Journey (4-5 sentences): Key moments, pivots, learnings
   - Current State (2-3 bullet points): Where you are now
   - Reflection (2-3 sentences): What you've learned about yourself/entrepreneurship
   - Invitation: Ask others to share their journeys

3. **Style**:
   - Authentic and vulnerable
   - Story-driven, not feature-driven
   - Show personal growth
   - Relatable struggles
   - MUST include https://interviewasssistant.com

4. **Story Elements**:
   - Job interview struggles
   - Decided to solve it with AI
   - Technical challenges met with persistence
   - Small wins that kept you going

Output format:
TITLE: [your title]

BODY:
[your body text]

SUBREDDIT: r/EntrepreneurRideAlong""",

        "learning": """Generate a Reddit post for r/Startups in "build in public" style about HireMeAI (https://interviewasssistant.com).

Post Type: Lessons Learned / Mistakes Made

Requirements:
1. **Title**: Counterintuitive lesson (50-90 chars)
   Example: "3 mistakes I made building my AI SaaS (and what I'd do differently)"

2. **Body Structure**:
   - Context (1-2 sentences): What you were building
   - Mistake #1-3 (each with):
     * What I did wrong (2-3 sentences)
     * Why it was wrong (1-2 sentences)
     * What I learned (1-2 sentences)
   - Current Approach (2-3 sentences): How you do things now
   - Advice (1-2 sentences): What you'd tell others

3. **Style**:
   - Self-deprecating but constructive
   - Specific examples, not generic advice
   - Show growth mindset
   - Help others avoid same mistakes
   - MUST include https://interviewasssistant.com

4. **Common Startup Mistakes**:
   - Building features users don't need
   - Over-engineering early on
   - Not talking to users enough
   - Focusing on perfection vs. shipping

Output format:
TITLE: [your title]

BODY:
[your body text]

SUBREDDIT: r/Startups""",

        "milestone": """Generate a Reddit post for r/SaaS in "build in public" style about HireMeAI (https://interviewasssistant.com).

Post Type: Milestone Celebration

Requirements:
1. **Title**: Milestone achievement with context (50-90 chars)
   Example: "Just hit 1,000 AI-generated interview answers - some reflections"

2. **Body Structure**:
   - The Milestone (1-2 sentences): What you achieved
   - The Journey (3-4 sentences): How you got here (time, challenges)
   - Key Metrics (3-5 bullet points): Data that tells the story
   - What Surprised You (2-3 sentences): Unexpected learnings
   - What's Next (2-3 sentences): Future goals
   - Gratitude/Ask (1-2 sentences): Thank community, ask for input

3. **Style**:
   - Celebratory but humble
   - Data-driven
   - Share the real numbers (good and bad)
   - Give credit to others
   - MUST include https://interviewasssistant.com

4. **Milestone Ideas**:
   - First 100 users
   - X number of interviews processed
   - Technical breakthrough (latency, accuracy)
   - Revenue milestone

Output format:
TITLE: [your title]

BODY:
[your body text]

SUBREDDIT: r/SaaS"""
    }

    prompt = prompts.get(post_type, prompts["progress"])

    # 添加JSON格式要求
    json_instruction = """

Output the post in JSON format:
{
  "title": "your title here",
  "body": "your body text here",
  "subreddit": "r/SubredditName"
}"""

    full_prompt = prompt + json_instruction

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.85,
        max_tokens=800,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content.strip()

    try:
        post_data = json.loads(content)
        title = post_data.get("title", "")
        body = post_data.get("body", "")
        subreddit = post_data.get("subreddit", "r/Startups")
    except:
        # Fallback解析
        title = ""
        body = content
        subreddit = "r/Startups"

    # 确保包含URL
    if 'https://interviewasssistant.com' not in body:
        body += f"\n\nCheck it out: https://interviewasssistant.com"

    return {
        "title": title,
        "body": body,
        "subreddit": subreddit,
        "post_type": post_type
    }

def generate_weekly_posts(count=3):
    """生成一周的Reddit帖子（多样化类型）"""

    post_types = ["progress", "technical", "story", "learning", "milestone"]
    posts = []

    print("=" * 80)
    print("🚀 HireMeAI - Reddit Build in Public 帖子生成器")
    print("=" * 80)
    print(f"\n📝 生成 {count} 篇Build in Public风格Reddit帖子...\n")

    for i in range(count):
        # 随机选择帖子类型（避免重复）
        post_type = random.choice(post_types)

        print(f"生成第 {i+1}/{count} 篇 (类型: {post_type})...")
        post = generate_reddit_post(post_type)
        posts.append(post)

        print(f"✅ 完成")
        print(f"   标题: {post['title'][:60]}...")
        print(f"   板块: {post['subreddit']}")
        print(f"   字数: {len(post['body'])} 字符")
        print("-" * 80)

    return posts

def save_reddit_schedule(posts):
    """保存Reddit发帖调度"""
    schedule = {
        "generated_at": datetime.now().isoformat(),
        "posts": [
            {
                "day": f"Day {i+1}",
                "title": post["title"],
                "body": post["body"],
                "subreddit": post["subreddit"],
                "post_type": post["post_type"],
                "posted": False
            }
            for i, post in enumerate(posts)
        ]
    }

    filename = f"reddit_schedule_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 调度文件已保存: {filename}")
    return filename

if __name__ == "__main__":
    # 生成3篇不同类型的帖子
    posts = generate_weekly_posts(3)

    # 保存调度
    schedule_file = save_reddit_schedule(posts)

    # 显示预览
    print("\n" + "=" * 80)
    print("📋 本周Reddit发帖计划:")
    print("=" * 80)

    for i, post in enumerate(posts, 1):
        print(f"\n📌 Day {i} - {post['subreddit']}")
        print(f"🏷️  类型: {post['post_type']}")
        print(f"📝 标题: {post['title']}")
        print(f"📄 正文预览: {post['body'][:150]}...")
        print()

    print("=" * 80)
    print("✅ 准备完成！")
    print(f"   调度文件: {schedule_file}")
    print("=" * 80)
