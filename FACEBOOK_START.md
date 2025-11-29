# Facebook营销 - 快速开始

## 🎯 系统说明

**Facebook系统使用群组而不是搜索关键词**（避免搜索页面崩溃）

类似其他平台：
- Reddit: 从subreddit抓取
- TikTok: 从hashtag抓取
- **Facebook: 从群组抓取**

---

## 🚀 3步开始

### Step 1: 登录Facebook

```bash
python3 facebook_login_and_save_auth.py
```

浏览器会自动打开，手动登录后cookies自动保存。

---

### Step 2: 准备Facebook群组

**重要**：你需要先在Facebook上做以下准备：

1. **在Facebook搜索相关群组**
   - 例如搜索："job search", "career advice"
   - 点击"Groups"标签

2. **加入相关群组**
   - 选择活跃的、公开的群组
   - 点击"Join Group"
   - 等待审核通过（如果需要）

3. **获取群组URL**
   - 打开群组页面
   - 复制完整URL
   - 格式：`https://www.facebook.com/groups/群组名或ID/`

**示例群组**（Job Interview产品）：
- Job Search Support
- Career Advice & Networking
- Interview Preparation Tips
- LinkedIn Job Seekers

---

### Step 3: 测试URL

运行测试脚本，输入你加入的群组URL：

```bash
python3 test_facebook_url.py
```

输入示例：
```
URL: https://www.facebook.com/groups/jobsearchsupport/
```

**如果成功**，会显示找到的帖子数。

**如果失败**：
- 确认是群组成员
- 确认群组是公开或已通过审核
- 尝试其他群组

---

## 💡 关键点

### ❌ 不能用的方式：
```python
# 这不会工作（搜索会崩溃）
KEYWORDS = ["job interview"]
```

### ✅ 正确的方式：
```python
# 使用你已加入的群组
GROUP_IDS = [
    "jobsearchsupport",  # 从URL提取的群组ID
    "careeradvicenetwork",
]
```

---

## 📋 完整流程

```
1. 在Facebook加入相关群组
   ↓
2. 运行 python3 facebook_login_and_save_auth.py 登录
   ↓
3. 运行 python3 test_facebook_url.py 测试群组
   ↓
4. 编辑 run_facebook_campaign.py 添加群组IDs
   ↓
5. 运行 python3 run_facebook_campaign.py
   ↓
6. 系统自动：访问群组 → 抓帖子 → 抓评论 → AI分析 → 发DM
```

---

## 🔍 如何找群组ID

从群组URL提取：

```
URL: https://www.facebook.com/groups/jobsearchsupport/
ID: jobsearchsupport

URL: https://www.facebook.com/groups/123456789/
ID: 123456789
```

然后在代码中使用：

```python
GROUP_IDS = [
    "jobsearchsupport",
    "123456789",
]
```

---

## 🧪 测试选项

### 选项1：测试任意URL（推荐）
```bash
python3 test_facebook_url.py
# 输入群组或帖子URL
```

### 选项2：测试群组IDs
```bash
python3 test_facebook_groups.py
# 输入群组IDs
```

### 选项3：直接运行Campaign
```bash
# 编辑 run_facebook_campaign.py 添加 GROUP_IDS
python3 run_facebook_campaign.py
```

---

## ⚠️ 常见问题

### Q: 为什么找不到帖子？

A: 可能的原因：
1. **不是群组成员** - 必须先加入群组
2. **群组ID错误** - 检查URL是否正确
3. **群组是私密的** - 选择公开群组
4. **需要审核** - 等待群组管理员批准

### Q: 如何知道是否加入成功？

A: 在浏览器中：
1. 访问群组页面
2. 如果能看到帖子 → 已加入
3. 如果显示"Join Group" → 还未加入

### Q: 群组ID在哪里？

A: 在浏览器地址栏：
```
facebook.com/groups/{这里就是ID}/
```

---

## 📊 预期效果

**成功的测试输出**：
```
✅ Found 5 posts
📋 Sample posts:
[1] https://www.facebook.com/groups/.../posts/...
[2] https://www.facebook.com/groups/.../posts/...
...
```

**如果看到这个** → 系统工作正常，可以运行完整campaign

---

## 🎯 推荐工作流

```bash
# 1. 登录（一次性）
python3 facebook_login_and_save_auth.py

# 2. 在Facebook加入2-3个相关群组
# （在浏览器中操作）

# 3. 测试第一个群组
python3 test_facebook_url.py
# 输入群组URL

# 4. 如果成功，测试完整流程
# 编辑 run_facebook_campaign.py
GROUP_IDS = ["你的群组ID"]
DM_BATCH_SIZE = 1  # 先测试1个

# 运行
export OPENAI_API_KEY='your_key'
python3 run_facebook_campaign.py

# 5. 确认DM发送成功后，扩大规模
DM_BATCH_SIZE = 3
GROUP_IDS = ["群组1", "群组2", "群组3"]
```

---

## 📚 文件说明

| 文件 | 用途 | 何时使用 |
|------|------|----------|
| `facebook_login_and_save_auth.py` | 登录保存cookies | 首次使用 |
| `test_facebook_url.py` | 测试任意URL | 验证群组可用 |
| `test_facebook_groups.py` | 测试群组IDs | 已知群组ID |
| `run_facebook_campaign.py` | 完整Campaign | 准备好开始 |

---

## ✅ 检查清单

开始前确认：

- [ ] 已运行 `facebook_login_and_save_auth.py`
- [ ] 已在Facebook加入2-3个相关群组
- [ ] 确认能在浏览器中看到群组帖子
- [ ] 已复制群组URLs
- [ ] 已运行 `test_facebook_url.py` 测试成功
- [ ] 已设置 `OPENAI_API_KEY`
- [ ] 已在 `run_facebook_campaign.py` 中配置 `GROUP_IDS`

---

## 💡 提示

1. **选择活跃群组** - 每天有新帖子的群组
2. **公开群组优先** - 避免需要审核的私密群组
3. **相关性最重要** - 群组话题要匹配你的产品
4. **先小规模测试** - 用1-2个群组，1个DM测试
5. **观察浏览器** - headless=False 可以看到浏览器操作

---

**现在开始吧！** 🚀

```bash
# 第一步
python3 facebook_login_and_save_auth.py

# 然后在Facebook加入群组，再继续测试
```
