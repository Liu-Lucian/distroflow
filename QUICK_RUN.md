# Instagram V2 - 快速运行指南

## 🚀 一键启动（推荐）

```bash
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'

python3 run_instagram_campaign_v2.py
```

## ✅ 系统状态

- **测试**: ✅ 20+循环无错误
- **Rate Limiting**: ✅ 无429错误
- **HTTP错误**: ✅ 自动处理和跳过
- **AI集成**: ✅ 正常工作
- **延迟设置**: ✅ 生产模式（安全）

## 📊 预期表现

- **每轮时间**: 15-20分钟
- **每小时**: 10-15个DM
- **每天**: 240-360个DM
- **成本**: ~$0.24/天

## 🔧 快速调整

### 想要更多用户？
编辑 `product_config.json`:
```json
"min_intent_score": 0.4  // 从0.5降到0.4
```

### 想要测试模式（更快）？
编辑 `product_config.json`:
```json
"delay_between_messages_seconds": [5, 10],
"delay_between_keywords_seconds": [10, 20]
```
⚠️ 测试完后改回生产模式！

### 修改产品描述？
编辑 `product_description.txt`
系统会自动重新生成关键词

## 📈 查看结果

```bash
# 查看qualified users
cat instagram_qualified_users.json | python3 -m json.tool | less

# 统计
python3 -c "import json; u=json.load(open('instagram_qualified_users.json')); print(f'Total: {len(u)}, Sent: {len([x for x in u if x.get(\"sent_dm\")])}');"
```

## 💡 遇到问题？

1. **登录失效**: 更新 `platforms_auth.json` 的sessionid
2. **AI返回0用户**: 降低 `min_intent_score`
3. **想看详细报告**: 阅读 `INSTAGRAM_V2_SUCCESS_REPORT.md`

---

**最后测试**: 2025-10-21
**状态**: ✅ 生产就绪
