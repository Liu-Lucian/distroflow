# Instagram Build in Public 自动发布系统 - 快速开始

## 📋 系统概述

自动生成并发布Instagram **Build in Public**风格帖子：
- 🎨 **AI生成图片**：专业的"Day X"风格视觉设计（1080x1080）
- ✍️ **AI生成Caption**：3段式结构，真实有价值的内容
- 🏷️ **智能Hashtags**：8-12个相关标签自动组合
- ⏰ **定时发布**：每周1-2次，自动化运行
- 🔄 **永久运行**：本周完成后自动生成下周内容

## 🚀 快速开始

### 1. 测试内容生成（不发布）

```bash
# 测试图片和Caption生成
python3 test_instagram_generation.py

# 查看生成的图片
open instagram_images/day_1.png
```

### 2. 准备Instagram登录

```bash
# 编辑认证文件
nano platforms_auth.json
```

添加Instagram sessionid：
```json
{
  "instagram": {
    "cookies": {
      "sessionid": "your_instagram_sessionid_here"
    }
  }
}
```

**获取sessionid**：浏览器登录Instagram → F12 → Application → Cookies → 复制sessionid

### 3. 运行完整系统

```bash
export OPENAI_API_KEY='your-key'
python3 auto_instagram_forever.py
```

## 📊 生成内容示例

### Caption结构（3段式）

**第1段（背景/问题）**：设定背景，2-3句
**第2段（正在做的事）**：分享进展，3-4句，包含数据
**第3段（进度和CTA）**：当前状态，提问互动

### Hashtags
```
#buildinpublic #AIstartup #founderjourney #indiehacker
#techcareers #ProductDevelopment #AItools #职场 #求职
```

## ⏰ 发布时间表

| 时间 | 发布窗口 |
|------|----------|
| 周三 | 10:00-12:00 |
| 周日 | 15:00-17:00 |

每周1-2个帖子，随机延迟0-10分钟

## 🗂️ 文件说明

- `auto_instagram_forever.py` - 主系统（永久运行）
- `test_instagram_generation.py` - 测试脚本
- `instagram_images/` - 生成的图片
- `instagram_build_progress.json` - 进度追踪
- `instagram_schedule_*.json` - 每周调度

## 🔧 常见问题

**Q: 登录失败？**
A: 更新 platforms_auth.json 中的sessionid

**Q: 图片生成失败？**
A: 运行 `pip3 install --break-system-packages Pillow`

**Q: 想修改发布时间？**
A: 编辑 `auto_instagram_forever.py` 中的 schedule_slots

## ✅ 运行前检查清单

- [ ] Pillow已安装
- [ ] OpenAI API key已设置
- [ ] Instagram sessionid已保存
- [ ] 测试脚本运行成功
- [ ] 生成的图片效果满意

全部完成后：`python3 auto_instagram_forever.py`

系统将每周自动发布1-2个高质量的Build in Public帖子！🚀
