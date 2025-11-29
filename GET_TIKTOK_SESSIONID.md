# 🎵 如何获取TikTok SessionID

TikTok不允许自动化浏览器登录，所以需要手动获取sessionid。

## 📋 步骤（只需3分钟）：

### 1️⃣ 在你的常用浏览器中登录TikTok

1. 打开 Chrome/Safari/Firefox
2. 访问 https://www.tiktok.com
3. 正常登录你的账号

### 2️⃣ 打开开发者工具

**Chrome/Edge:**
- 按 `Cmd + Option + I` (Mac)
- 或者右键 → "检查"

**Safari:**
- 先在设置中启用开发者菜单
- 然后按 `Cmd + Option + I`

**Firefox:**
- 按 `Cmd + Option + I`

### 3️⃣ 查找SessionID

1. 点击开发者工具顶部的 **"Application"** 标签 (Chrome)
   - Safari: "Storage" 标签
   - Firefox: "Storage" 标签

2. 左侧展开 **"Cookies"** → **"https://www.tiktok.com"**

3. 找到名为 **`sessionid`** 的cookie

4. 复制它的 **Value** (值)
   - 应该是一长串字母和数字
   - 类似: `d6bcb103d3892130b480269a17c26da8`

### 4️⃣ 保存到配置文件

运行以下命令：

```bash
python3 -c "
import json

# 输入你复制的sessionid
sessionid = input('请粘贴你的sessionid: ').strip()

# 加载现有配置
try:
    with open('platforms_auth.json', 'r') as f:
        config = json.load(f)
except:
    config = {}

# 更新TikTok配置
if 'tiktok' not in config:
    config['tiktok'] = {}

config['tiktok']['sessionid'] = sessionid

# 保存
with open('platforms_auth.json', 'w') as f:
    json.dump(config, f, indent=2)

print('✅ SessionID已保存到 platforms_auth.json')
"
```

或者直接编辑 `platforms_auth.json`：

```json
{
  "tiktok": {
    "sessionid": "你的sessionid粘贴到这里"
  },
  "instagram": {
    ...
  }
}
```

### 5️⃣ 验证

```bash
./start_tiktok_campaign.sh
```

如果能正常运行，说明sessionid有效！

---

## 🔄 SessionID过期了怎么办？

如果几天后TikTok又退出登录：
1. 重复上述步骤
2. 获取新的sessionid
3. 更新配置文件

---

## 📸 截图参考

### Chrome开发者工具：

```
Application
  ├─ Cookies
  │   └─ https://www.tiktok.com
  │       ├─ sessionid ← 复制这个的Value
  │       ├─ tt_csrf_token
  │       └─ ...
```

---

## ✅ 完成后

运行：
```bash
./start_tiktok_campaign.sh
```

系统会自动：
- 搜索视频
- 抓取评论
- AI分析
- 发送DM

**总成本: ~$0.01 每次运行**
