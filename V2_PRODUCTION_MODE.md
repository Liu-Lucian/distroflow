# Instagram营销系统 V2 - 生产模式

## ✅ 已升级为生产模式

### 延迟配置（避免Instagram检测）

**消息间隔**: 60-120秒（1-2分钟）
**关键词间隔**: 300-600秒（5-10分钟）
**帖子间隔**: 30-60秒（每个帖子之间冷却）

### 重试机制

- 每个帖子访问失败后等待10秒重试
- 共2次尝试机会
- 自动跳过失败的帖子

### AI Helper集成

- 如果标准选择器失败，会使用AI Vision分析页面
- 自动截图并让GPT-4识别正确的元素

---

## 🚀 运行方式

```bash
python3 run_instagram_campaign_v2.py
```

**自动完成**：
1. 读取 `product_description.txt`
2. AI生成30个关键词
3. 搜索帖子（帖子之间延迟30-60秒）
4. 爬评论并AI分析
5. 发送DM（DM之间延迟60-120秒）
6. 换关键词（延迟5-10分钟）
7. 无限循环

---

## 📊 性能指标

**预期速度**：
- 每个帖子：~40秒（访问+爬评论）
- 10个帖子：~7分钟
- AI分析：~5秒
- 发送20个DM：~30分钟（含延迟）
- **每轮总计**：~40分钟

**每小时**：约1-2个关键词，20-40个DM

---

## ⚙️ 调整延迟

如果想要更快（测试模式）：

编辑 `product_config.json`:
```json
{
  "campaign_settings": {
    "delay_between_messages_seconds": [5, 10],
    "delay_between_keywords_seconds": [10, 20],
    "delay_between_posts_seconds": [5, 10]
  }
}
```

---

## 🔍 监控运行

观察日志中的：
- `⏸️ Cooling down Xs` - 帖子间冷却
- `✅ Post loaded` - 帖子成功访问
- `⚠️ HTTP/ABORTED error` - 帖子被删除/限制（自动跳过）
- `⏸️ Next cycle in X minutes` - 关键词间休息

---

## 💡 如果还是遇到访问错误

Instagram可能检测到自动化。建议：

1. **增加延迟** - 改为更长的冷却时间
2. **使用V3版本** - 不访问单个帖子，只在hashtag页面收集用户
3. **手动登录** - 在浏览器中先手动浏览几个页面
4. **换IP** - 如果被临时封禁

---

## 🎯 V2 vs V3

**V2（当前）**: 访问帖子 → 爬评论 → AI分析 → 高质量用户
- 优点：用户质量高（有评论内容供AI分析）
- 缺点：可能被Instagram检测

**V3（备选）**: 只在hashtag页面滚动 → 提取用户 → 发DM
- 优点：更难被检测（不访问单个帖子）
- 缺点：用户质量未知（没有评论内容）

如果V2频繁失败，可以切换到V3：
```bash
python3 run_instagram_campaign_v3.py
```
