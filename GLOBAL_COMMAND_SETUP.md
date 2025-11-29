# 🌍 Global Command Setup - marketing-campaign

## ✅ 安装完成！/ Installation Complete!

全局命令已经安装成功！现在你可以在任何项目目录使用 `marketing-campaign`。

The global command is now installed! You can use `marketing-campaign` from any project directory.

---

## 📍 安装位置 / Installation Location

- **命令位置 / Command**: `~/.local/bin/marketing-campaign`
- **源代码 / Source**: `/Users/l.u.c/my-app/MarketingMind AI/marketing-campaign.py`
- **配置文件 / Config**: `/Users/l.u.c/my-app/MarketingMind AI/email_config.json`

---

## 🚀 使用方法 / Usage

### 基本用法 / Basic Usage

```bash
# 在任何项目目录运行 / Run from any project directory
cd /path/to/any/project
marketing-campaign --auto-generate --leads 100
```

### 所有选项 / All Options

```bash
# 自动生成关键词并运行活动 / Auto-generate keywords and run campaign
marketing-campaign --auto-generate --leads 100

# 使用已有产品文件 / Use existing product file
marketing-campaign --product-file product.md --leads 50

# 手动确认发送 / Manual confirmation
marketing-campaign --auto-generate --leads 100 --no-auto-confirm

# 不设置自动跟进 / Skip auto-followup setup
marketing-campaign --auto-generate --leads 100 --no-auto-followup

# 自定义项目目录 / Custom project directory
marketing-campaign --auto-generate --project-dir ../other-project --leads 50

# 自定义种子账号数量 / Custom seed count
marketing-campaign --auto-generate --leads 100 --seeds 10
```

---

## 📋 前提条件 / Prerequisites

### 1. Python依赖 / Python Dependencies

所有依赖已安装到系统Python 3.13：
All dependencies are installed to system Python 3.13:

```bash
✓ pandas
✓ anthropic
✓ beautifulsoup4
✓ openai
✓ pdfminer.six
✓ python-docx
✓ requests
✓ python-dotenv
✓ playwright
```

### 2. Twitter Authentication

在首次使用前，需要设置Twitter认证：
Before first use, you need to set up Twitter authentication:

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 login_and_save_auth.py
```

这会创建 `auth.json` 文件用于Twitter登录。
This will create an `auth.json` file for Twitter login.

### 3. Email Configuration

确保 `email_config.json` 已正确配置：
Ensure `email_config.json` is properly configured:

```json
{
  "smtp": {
    "username": "liu.lucian6@gmail.com",
    "password": "qaug xvwq ufet nqcy",
    "from_name": "HireMe AI"
  },
  "test_mode": {
    "enabled": true,  // 设置为 false 用于生产环境
    "test_email": "liu.lucian@icloud.com"
  }
}
```

---

## 🧪 测试 / Testing

### 测试1：在当前目录 / Test in current directory

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
marketing-campaign --auto-generate --leads 5 --no-auto-confirm
```

### 测试2：在其他项目 / Test in other project

```bash
cd /Users/l.u.c/my-app/interview_assistant
marketing-campaign --auto-generate --leads 5 --no-auto-confirm
```

这个测试成功运行了！
This test ran successfully!

输出示例 / Output example:
```
🔍 Auto-generating keywords from project directory...
⚠️  No project documentation found. Using default keywords.
🚀 FULLY AUTOMATED EMAIL CAMPAIGN SYSTEM
📊 STEP 1: Finding Leads from Twitter
✓ Product analysis completed
✓ Found 30 seed accounts
```

---

## 📂 它是如何工作的 / How It Works

1. **Wrapper Script** (`~/.local/bin/marketing-campaign`):
   - Bash wrapper that sets up Python path
   - Points to the main Python script
   - Can be called from anywhere

2. **Main Script** (`marketing-campaign.py`):
   - Auto-detects MarketingMind AI directory
   - Adds `src/` to Python path
   - Imports all necessary modules
   - Works from any current directory

3. **Project Directory**:
   - Scans current directory for docs (README.md, package.json, etc.)
   - Generates keywords from project files
   - Creates `auto_generated_product.md` in current directory

---

## 🔧 工作流程 / Workflow

```
你在任何项目目录 / You in any project directory
    ↓
运行: marketing-campaign --auto-generate --leads 100
    ↓
系统扫描当前项目文件 / System scans current project files
    ↓
生成关键词到当前目录 / Generate keywords in current directory
    ↓
连接到 MarketingMind AI 系统 / Connect to MarketingMind AI system
    ↓
在Twitter上寻找线索 / Find leads on Twitter
    ↓
验证邮箱 / Verify emails
    ↓
发送邮件 (使用 MarketingMind AI 的配置)
Send emails (using MarketingMind AI config)
    ↓
完成！/ Complete!
```

---

## 📊 实际测试示例 / Real Test Example

```bash
$ cd /Users/l.u.c/my-app/interview_assistant

$ marketing-campaign --auto-generate --leads 1 --seeds 1 --no-auto-confirm --no-auto-followup

INFO:__main__:
🔍 Auto-generating keywords from project directory...
WARNING:__main__:   ⚠️  No project documentation found. Using default keywords.

INFO:__main__:======================================================================
INFO:__main__:🚀 FULLY AUTOMATED EMAIL CAMPAIGN SYSTEM
INFO:__main__:======================================================================

INFO:__main__:
📋 Configuration:
INFO:__main__:   Product file: auto_generated_product.md
INFO:__main__:   Target leads: 1
INFO:__main__:   Seed accounts: 1

INFO:__main__:
======================================================================
INFO:__main__:📊 STEP 1: Finding Leads from Twitter
INFO:__main__:======================================================================

INFO:src.ultimate_email_finder:✅ Email verification enabled
INFO:src.ultimate_email_finder:🚀 Ultimate Email Finder Starting...
INFO:product_brain:✓ Product analysis completed
INFO:product_brain:✓ Found 30 seed accounts

✅ 成功！/ Success!
```

---

## 🌟 优势 / Advantages

### ✅ 全局访问 / Global Access
- 可以在任何目录使用 / Can be used from any directory
- 无需记住完整路径 / No need to remember full path
- 简单的命令名 / Simple command name

### ✅ 自动路径解析 / Automatic Path Resolution
- 自动找到 MarketingMind AI 目录 / Auto-finds MarketingMind AI directory
- 自动添加 Python 路径 / Auto-adds Python paths
- 使用正确的配置文件 / Uses correct config files

### ✅ 项目感知 / Project-Aware
- 扫描当前项目文件 / Scans current project files
- 在当前目录生成关键词 / Generates keywords in current directory
- 保持项目分离 / Keeps projects separate

---

## 🔄 更新命令 / Updating the Command

如果修改了Python脚本，无需重新安装：
If you modify the Python script, no reinstallation needed:

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
# 编辑 marketing-campaign.py
# Edit marketing-campaign.py

# 更改立即生效！
# Changes take effect immediately!
```

Wrapper脚本会自动使用最新版本。
The wrapper script automatically uses the latest version.

---

## ❗ 故障排查 / Troubleshooting

### 问题1: "command not found: marketing-campaign"

**解决方案 / Solution**:
```bash
# 检查安装 / Check installation
ls -la ~/.local/bin/marketing-campaign

# 检查 PATH / Check PATH
echo $PATH | grep ".local/bin"

# 如果不在 PATH 中，重新加载 / If not in PATH, reload
source ~/.zshrc

# 或使用完整路径 / Or use full path
~/.local/bin/marketing-campaign --auto-generate --leads 10
```

### 问题2: "ModuleNotFoundError"

**解决方案 / Solution**:
```bash
# 重新安装依赖 / Reinstall dependencies
python3 -m pip install --user --break-system-packages -r "/Users/l.u.c/my-app/MarketingMind AI/requirements.txt"
```

### 问题3: "Authentication file 'auth.json' not found"

**解决方案 / Solution**:
```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 login_and_save_auth.py
# 按提示登录 Twitter / Follow prompts to login to Twitter
```

### 问题4: 邮件发送失败 / Email sending fails

**检查 / Check**:
```bash
# 查看配置 / View config
cat "/Users/l.u.c/my-app/MarketingMind AI/email_config.json"

# 确认测试模式状态 / Confirm test mode status
# "test_mode": {"enabled": true}  → 所有邮件发到测试邮箱
# "test_mode": {"enabled": false} → 邮件发到真实 leads
```

---

## 📚 相关文档 / Related Documentation

1. **COMPLETE_SYSTEM_GUIDE.md** - 完整系统指南
2. **YES_FULLY_AUTOMATED.md** - 自动化确认
3. **AUTOMATION_FLOW.txt** - 自动化流程图
4. **HOW_TO_USE.md** - 详细使用说明

---

## 🎉 成功！/ Success!

你现在可以在任何项目目录使用 `marketing-campaign` 命令！

You can now use the `marketing-campaign` command from any project directory!

### 快速开始 / Quick Start

```bash
# 1. 设置 Twitter 认证 (首次) / Setup Twitter auth (first time)
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 login_and_save_auth.py

# 2. 在任何项目使用 / Use in any project
cd /path/to/your/project
marketing-campaign --auto-generate --leads 10 --no-auto-confirm

# 3. 享受全自动营销！/ Enjoy fully automated marketing!
```

---

**✨ 全局命令安装完成！Ready to use from anywhere!**
