# 🚀 开始使用 - 真正的 1 步到位

## ⭐ 推荐：一键完整设置

```bash
./setup_and_launch.sh
```

**这个脚本会自动完成所有操作**:
- ✅ 创建 GitHub 仓库（如不存在）
- ✅ 配置认证
- ✅ 推送第一个 commit
- ✅ 启动发布系统

**详细说明**: 查看 `一键完整设置.md`

---

## 🔄 或者：传统 2 步方式

### 系统已就绪 ✅

所有代码已调试完成，只需配置认证即可启动！

### 第 1 步：获取 GitHub Token (1 分钟)

1. 访问：https://github.com/settings/tokens
2. 点击："Generate new token (classic)"
3. 权限勾选："**repo**" (完整仓库访问权限)
4. 点击："Generate token"
5. **复制 token**（类似：`ghp_xxxxxxxxxxxx...`）

---

## 第 2 步：启动系统 (30 秒)

### 方式 A: 自动配置（推荐）

```bash
./quick_auth.sh
```

输入 token，完成！

### 方式 B: 手动配置

```bash
# 编辑配置文件
nano GITHUB_TOKEN.env

# 取消注释并填写 token：
GITHUB_TOKEN=ghp_your_token_here

# 加载并启动
source GITHUB_TOKEN.env
./run_publisher.sh
```

---

## ✅ 验证成功

启动后，几秒钟内应该看到：

```
✅ 未推送的 commits 已成功推送
🎉 第一个 commit 已推送到 GitHub
⏰ 下次检查时间: ...
```

查看 GitHub：https://github.com/q1q1-spefic/interview_assistant

应该能看到第一个 commit！🎉

---

## 📊 之后系统会自动

- ✅ 每天提交 1-3 次
- ✅ 15-30 天完成 40 个模块
- ✅ Contributions graph 持续绿色
- ✅ 完全自动，无需干预

---

## 📝 监控

```bash
# 查看日志
tail -f github_publisher.log

# 查看状态
python3 github_gradual_publisher.py --status
```

---

## 🎯 选择你的方式

### 方式 A: 一键完整设置（最简单）⭐
```bash
./setup_and_launch.sh
```
自动创建仓库、配置认证、推送代码、启动系统

### 方式 B: 快速认证（仓库已创建）
```bash
./quick_auth.sh
```
仅配置认证并推送（需手动创建仓库）

---

**推荐从方式 A 开始！** 🚀
