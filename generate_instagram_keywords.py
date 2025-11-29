#!/usr/bin/env python3
"""
用AI根据产品介绍自动生成Instagram关键词
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

product_description = """
HireMeAI (https://interviewasssistant.com) - AI-powered interview preparation platform.
Helps job seekers with mock interviews, real-time feedback, and career coaching.

Target audience:
- Job seekers preparing for interviews
- Career changers
- Recent graduates
- Professionals looking to improve interview skills
"""

prompt = f"""Based on this product description, generate 10 Instagram hashtags/keywords that will help find potential customers.

Product: {product_description}

Requirements:
1. Keywords should be popular on Instagram (high search volume)
2. Keywords should attract job seekers and career-focused users
3. Use single words or concatenated phrases (no spaces, like "jobsearch" not "job search")
4. Mix of broad and specific keywords
5. Focus on people actively looking for jobs or career advice

Return ONLY a Python list format, nothing else:
["keyword1", "keyword2", ...]
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

keywords_text = response.choices[0].message.content.strip()

# 提取列表
if keywords_text.startswith('['):
    print(keywords_text)
else:
    # 尝试提取```python```包裹的内容
    if '```python' in keywords_text:
        start = keywords_text.find('```python') + 9
        end = keywords_text.find('```', start)
        print(keywords_text[start:end].strip())
    elif '```' in keywords_text:
        start = keywords_text.find('```') + 3
        end = keywords_text.find('```', start)
        print(keywords_text[start:end].strip())
    else:
        print(keywords_text)

