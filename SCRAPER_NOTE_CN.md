# Twitter爬虫说明

## ⚠️ 重要提示

Twitter现在需要登录才能查看大部分内容，包括粉丝列表。网页爬虫方案需要以下几种方式之一：

### 方案1：使用登录功能（推荐）

目前Twitter (X) 已经限制未登录用户访问大部分内容。要使用爬虫，您需要：

1. **提供Twitter账号登录**
2. **使用Cookie来保持登录状态**

### 方案2：使用第三方工具

几个替代方案：

1. **Nitter (Twitter镜像)**
   - 公开的Twitter镜像网站
   - 不需要登录
   - 访问: https://nitter.net

2. **Twitter API (已实现)**
   - 虽然有rate limit，但是官方支持
   - 已经在 `main.py` 中实现
   - 稳定可靠

3. **手动导出**
   - 手动访问粉丝页面
   - 使用浏览器扩展导出数据

### 方案3：优化现有API方式

我已经实现了human-like behavior来避免rate limit，建议：

```bash
# 使用API方式，但分批次运行
python main.py find-leads --product "你的产品" --count 50

# 等待20分钟后再运行下一批
python main.py find-leads --product "你的产品" --count 50
```

## 💡 最佳实践

考虑到Twitter的限制，我建议：

### 选项A：使用API (推荐)

虽然有rate limit，但配合human-like behavior，每天可以获取几百个leads：

```bash
# 每天运行3-4次，每次50-100个
python main.py find-leads --product "产品描述" --count 100 --find-emails
```

**优点：**
- ✅ 官方支持，稳定
- ✅ 已经有human-like延迟
- ✅ 自动处理rate limit
- ✅ 长期可用

**缺点：**
- ⏱️ 需要时间（但是自动化的）

### 选项B：添加登录功能到爬虫

如果您愿意提供Twitter登录信息，我可以更新爬虫代码来：

1. 自动登录您的Twitter账号
2. 然后爬取粉丝列表
3. 提取邮箱信息

**需要您提供：**
- Twitter用户名/邮箱
- 密码

**安全考虑：**
- 密码存储在本地.env文件
- 不会分享给任何第三方
- 仅用于爬虫登录

### 选项C：使用Nitter镜像

Nitter是Twitter的开源替代前端，不需要登录：

```python
# 我可以创建一个Nitter爬虫
# 访问 https://nitter.net/用户名/followers
# 爬取公开信息
```

**优点：**
- ✅ 不需要登录
- ✅ 没有rate limit
- ✅ 快速

**缺点：**
- ⚠️ Nitter实例可能不稳定
- ⚠️ 可能缺少某些信息

## 🤔 您想怎么做？

请告诉我您偏好哪种方案：

1. **继续使用API** - 慢但稳定，每天几百个leads
2. **添加登录功能** - 需要提供Twitter账号密码
3. **使用Nitter镜像** - 我创建新的爬虫
4. **混合方案** - API + 手动导出结合

我可以根据您的选择来实现相应的解决方案！

## 📝 当前状态

已实现的功能：
- ✅ Twitter API集成 (main.py)
- ✅ Human-like behavior (避免rate limit)
- ✅ 网页爬虫框架 (需要登录才能用)
- ✅ 邮箱提取功能
- ✅ 数据导出

需要您决定的：
- ⏳ 是否愿意提供登录信息
- ⏳ 或者接受API的rate limit
- ⏳ 或者尝试Nitter方案
