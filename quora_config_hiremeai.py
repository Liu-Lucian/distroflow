#!/usr/bin/env python3
"""
HireMeAI (即答侠) - Quora专属配置
策略：热情回答相关领域问题，自然提及产品
"""

# ============ 产品信息 ============
PRODUCT_CONFIG = {
    "name": "HireMeAI",
    "chinese_name": "即答侠",
    "url": "https://interviewasssistant.com",
    "tagline": "AI-powered interview preparation assistant",
    "founder_identity": "founder building an AI interview assistant",

    # 核心功能（用于自然提及）
    "key_features": [
        "实时语音面试辅助",
        "智能简历优化（ATS评分）",
        "个性化问答模版生成",
        "STAR框架回答优化",
        "面试焦虑实时缓解"
    ],

    # 核心数据（用于回答中的具体数字）
    "metrics": {
        "users_helped": "200+",
        "success_rate_improvement": "30%",
        "preparation_time_saved": "从数天到数小时",
        "response_time": "<1秒",
        "accuracy": ">95%"
    }
}

# ============ 关键词策略 ============
# 核心理念：回答相关领域问题，而非产品本身
# ❌ 不要搜索："AI interview tool", "interview assistant software"
# ✅ 要搜索：看似无关但相关的广泛问题

SEARCH_KEYWORDS = [
    # 1. 面试焦虑/心理类（高搜索量，emotional pain point）
    "job interview anxiety",
    "nervous about interview",
    "interview stress tips",
    "how to calm down before interview",
    "fear of job interviews",

    # 2. 面试准备技巧类（practical advice）
    "how to prepare for interview",
    "interview preparation tips",
    "behavioral interview questions",
    "tell me about yourself answer",
    "common interview mistakes",

    # 3. 简历优化类（upstream问题）
    "resume tips",
    "ATS friendly resume",
    "how to optimize resume",
    "resume keywords",
    "resume gets rejected",

    # 4. 职业发展/转型类（broader context）
    "career change advice",
    "how to switch careers",
    "first job interview",
    "entry level interview tips",

    # 5. 具体面试问题类（long-tail SEO）
    "how to answer why should we hire you",
    "how to answer weakness question",
    "STAR method examples",
    "how to talk about gaps in resume",

    # 6. 技术面试类（如果适用）
    "technical interview preparation",
    "coding interview tips",
    "how to explain technical projects",

    # 7. 求职心态/动力类（motivational）
    "job search motivation",
    "dealing with job rejection",
    "how long does job search take",
    "unemployment stress"
]

# 按优先级分组
KEYWORD_PRIORITY = {
    "high_priority": [
        # 高搜索量 + 高相关度 + 情感pain point
        "job interview anxiety",
        "how to prepare for interview",
        "tell me about yourself answer",
        "nervous about interview",
        "common interview mistakes"
    ],

    "medium_priority": [
        # 中等搜索量 + 具体问题
        "behavioral interview questions",
        "STAR method examples",
        "resume tips",
        "how to answer weakness question",
        "interview stress tips"
    ],

    "long_tail": [
        # 低竞争 + 高转化
        "how to talk about gaps in resume",
        "first remote interview tips",
        "interview preparation checklist",
        "how to follow up after interview"
    ]
}

# ============ 回答风格配置 ============
ANSWER_STYLE_CONFIG = {
    # 核心原则
    "principles": [
        "先提供真正价值（解决用户问题）",
        "分享真实经验和数据",
        "自然提及产品（作为工具之一，不是唯一解决方案）",
        "热情、empathetic语气",
        "避免任何sales pitch"
    ],

    # 产品提及方式（自然的context）
    "product_mention_examples": [
        "While building {product_name}, we discovered...",
        "We tested this with {number} users on {product_name} and found...",
        "This is why we added [feature] to {product_name} ({url})...",
        "I've been working on an AI tool ({product_name}) to help with this...",
        "Our data from {product_name} shows..."
    ],

    # 避免的表达
    "avoid_phrases": [
        "Our product is the best...",
        "You should try {product_name}...",
        "Download {product_name} now...",
        "{product_name} solves all your problems..."
    ]
}

# ============ 相关领域问题示例库 ============
# 这些是我们应该热情回答的"看似无关"但高价值的问题
RELATED_DOMAIN_QUESTIONS = {
    "anxiety_stress": [
        "Why do I get so nervous during interviews?",
        "How to stop shaking during an interview?",
        "Is it normal to blank out during interviews?",
        "How to deal with interview rejection?",
        "Why do I perform worse in real interviews than practice?"
    ],

    "preparation_strategy": [
        "How long should I prepare for an interview?",
        "What's the most important thing in interview prep?",
        "Should I memorize answers?",
        "How to prepare for behavioral questions?",
        "Is mock interview practice worth it?"
    ],

    "resume_upstream": [
        "Why is my resume getting rejected?",
        "How to make resume stand out?",
        "What is ATS and how does it work?",
        "Should I customize resume for each job?",
        "How many keywords should be in resume?"
    ],

    "specific_questions": [
        "How to answer 'Tell me about yourself'?",
        "How to explain job gap?",
        "How to answer 'Why did you leave your last job'?",
        "How to talk about weaknesses?",
        "How to answer 'Where do you see yourself in 5 years'?"
    ],

    "career_psychology": [
        "How to stay motivated during job search?",
        "Dealing with imposter syndrome?",
        "How to handle multiple interview rejections?",
        "Is it ok to cry after bad interview?",
        "How to build interview confidence?"
    ],

    "technical_specific": [
        "How to explain technical projects to non-technical interviewer?",
        "How to prepare for system design interview?",
        "STAR method for technical questions?",
        "How to showcase projects in interview?"
    ]
}

# ============ 回答钩子（Hook）模板 ============
# 用于开头吸引注意力
ANSWER_HOOKS = {
    "counter_intuitive": [
        "After analyzing {number} interviews, I found something surprising:",
        "Here's what most people get wrong about {topic}:",
        "The biggest interview mistake isn't what you think:"
    ],

    "personal_experience": [
        "I've helped {number}+ people prepare for interviews, and here's what actually works:",
        "While building an interview prep tool, we discovered:",
        "After conducting {number} mock interviews, one pattern became clear:"
    ],

    "data_driven": [
        "We tested this with {number} users and the results were clear:",
        "The data shows {surprising_finding}:",
        "Here's what the numbers actually say:"
    ],

    "empathetic": [
        "I know exactly how you feel - interview anxiety is real.",
        "You're not alone - {percentage} of people experience this.",
        "This is a common struggle, and here's why:"
    ]
}

# ============ 成功案例（用于回答中的具体例子）============
SUCCESS_STORIES = [
    {
        "scenario": "面试焦虑",
        "problem": "用户面试时极度紧张，大脑空白",
        "solution": "5分钟warm-up练习 + 实时AI反馈",
        "result": "信心分数提升35%，成功率从60%到85%"
    },
    {
        "scenario": "简历被拒",
        "problem": "ATS系统过滤掉简历",
        "solution": "关键词优化 + STAR框架重写",
        "result": "HR筛选通过率从20%到75%"
    },
    {
        "scenario": "回答结构差",
        "problem": "回答冗长、没重点",
        "solution": "STAR框架训练 + 200字标准化",
        "result": "面试官满意度提升40%"
    }
]

# ============ 每周发布计划 ============
PUBLISHING_SCHEDULE = {
    "answers_per_week": 3,  # 每周3条高质量回答
    "answer_days": [1, 3, 5],  # 周二、周四、周六
    "time_slot": "10:00-14:00",  # 发布时间段

    # 风格轮换（保持内容多样性）
    "style_rotation": [
        "experience",  # 经验分享
        "insight",     # 数据洞察
        "empathetic",  # 心理支持
        "development"  # 产品开发
    ]
}

# ============ 质量标准 ============
QUALITY_STANDARDS = {
    "min_question_views": 500,      # 最小浏览量
    "max_answer_count": 20,          # 最大回答数（避免过度竞争）
    "min_quality_score": 70,         # 最小质量分数

    # 回答质量要求
    "answer_requirements": {
        "min_words": 200,
        "max_words": 400,
        "must_include_data": True,    # 必须包含具体数据
        "must_include_story": True,   # 必须包含故事/例子
        "product_mentions": 1,         # 产品提及次数（只1次）
        "actionable_steps": True       # 必须有可行建议
    }
}

# ============ 互动策略 ============
ENGAGEMENT_STRATEGY = {
    "daily_interactions": 8,  # 每天互动次数

    "interaction_mix": {
        "upvotes": 0.70,      # 70%点赞
        "comments": 0.30      # 30%评论
    },

    # 评论模板（真诚、有价值）
    "comment_templates": [
        "This is a great point about {topic}. I'd also add that {insight}.",
        "Really helpful breakdown! Have you found that {question}?",
        "Thanks for sharing this. In my experience, {additional_tip}.",
        "Solid advice. One thing that worked for me was {example}."
    ]
}

# ============ 导出配置 ============
def get_config():
    """返回完整配置"""
    return {
        "product": PRODUCT_CONFIG,
        "keywords": SEARCH_KEYWORDS,
        "keyword_priority": KEYWORD_PRIORITY,
        "answer_style": ANSWER_STYLE_CONFIG,
        "related_questions": RELATED_DOMAIN_QUESTIONS,
        "hooks": ANSWER_HOOKS,
        "success_stories": SUCCESS_STORIES,
        "schedule": PUBLISHING_SCHEDULE,
        "quality": QUALITY_STANDARDS,
        "engagement": ENGAGEMENT_STRATEGY
    }

if __name__ == "__main__":
    import json
    config = get_config()
    print(json.dumps(config, indent=2, ensure_ascii=False))
