#!/usr/bin/env python3
"""
生成每条tweet都带URL的内容
"""
import json

# 读取原始内容
with open('test_brand_no_chinese.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 修改每条tweet，都加上URL
original_tweets = data['twitter']['tweets']
modified_tweets = []

url = "https://interviewasssistant.com"

for i, tweet in enumerate(original_tweets, 1):
    # 如果tweet里没有URL，就加上
    if url not in tweet:
        # 在tweet末尾加上URL
        modified_tweet = f"{tweet}\n\n👉 {url}"
    else:
        modified_tweet = tweet

    modified_tweets.append(modified_tweet)
    print(f"Tweet {i}:")
    print(modified_tweet)
    print(f"长度: {len(modified_tweet)} 字符")
    print("-" * 80)

# 更新内容
data['twitter']['tweets'] = modified_tweets

# 保存
with open('tweets_all_with_url.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ 已生成 {len(modified_tweets)} 条tweets，每条都包含URL")
print(f"✅ 保存到: tweets_all_with_url.json")
print(f"\n🔍 验证:")
for i, tweet in enumerate(modified_tweets, 1):
    has_url = url in tweet
    print(f"   Tweet {i}: {'✅' if has_url else '❌'} 包含URL")
