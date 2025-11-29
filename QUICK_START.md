# Instagram营销系统 - 快速开始

## 📝 步骤1: 编辑产品介绍

```bash
nano product_description.txt
```

**在这个文件里写你的完整产品介绍**（可以写很多内容）

包括：
- 产品功能
- 目标用户
- 解决的痛点
- 竞争优势
- 使用场景

AI会读取这个文件来自动生成Instagram关键词并分析用户。

---

## 🚀 步骤2: 运行营销系统

```bash
python3 run_instagram_campaign_v2.py
```

**自动完成**：
1. 读取 `product_description.txt`
2. AI生成30个Instagram关键词
3. 搜索帖子 → 爬评论 → AI分析 → 发DM
4. 无限循环

---

## ⚙️ 可选：调整设置

编辑 `product_config.json` 来修改配置。

---

## 🎯 工作原理

```
你编辑 product_description.txt（产品介绍）
              ↓
运行脚本 → AI读取产品介绍 → 自动生成30个关键词
              ↓
搜索Instagram → 爬评论 → AI分析用户匹配度
              ↓
自动发送个性化DM → 追踪已发送用户
              ↓
换下一个关键词 → 无限循环
```

---

## ⏸️ 停止/继续

**停止**：按 `Ctrl+C`

**继续**：重新运行脚本（会自动跳过已发送用户）
