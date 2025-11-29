#!/bin/bash

# DistroFlow - 一键推送到 GitHub
# 使用方法: bash push_to_github.sh

set -e  # 遇到错误立即停止

echo "🚀 DistroFlow - 推送到 GitHub"
echo "=============================="
echo ""

# 1. 初始化 git（如果还没有）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    echo "✅ Git 初始化完成"
else
    echo "✅ Git 仓库已存在"
fi
echo ""

# 2. 添加所有文件
echo "📝 添加文件到 Git..."
git add .
echo "✅ 文件添加完成"
echo ""

# 3. 提交
echo "💾 创建提交..."
git commit -m "Initial commit: DistroFlow v0.3.0

- Cross-platform distribution infrastructure
- Browser automation with Playwright
- AI-powered CAPTCHA solver
- FastAPI server + WebSocket
- Chrome browser extension
- Supports Twitter, Reddit, HackerNews, Instagram
- Technical deep dive documentation
- Ethics and responsible use guidelines

🤖 Generated with Claude Code
https://claude.com/claude-code"

echo "✅ 提交创建完成"
echo ""

# 4. 设置主分支名称
echo "🌿 设置主分支..."
git branch -M main
echo "✅ 主分支设置完成"
echo ""

# 5. 添加远程仓库
echo "🔗 添加远程仓库..."
if git remote | grep -q "^origin$"; then
    echo "⚠️  远程仓库已存在，删除旧的..."
    git remote remove origin
fi
git remote add origin https://github.com/Liu-Lucian/distroflow.git
echo "✅ 远程仓库添加完成"
echo ""

# 6. 推送
echo "🚀 推送到 GitHub..."
git push -u origin main

echo ""
echo "=============================="
echo "✅ 推送完成！"
echo ""
echo "🎉 你的仓库地址："
echo "   https://github.com/Liu-Lucian/distroflow"
echo ""
echo "📝 下一步："
echo "   1. 访问仓库页面"
echo "   2. 添加 Topics: automation, python, playwright, ai, browser-automation, infrastructure"
echo "   3. 检查 README 显示是否正常"
echo "   4. 开始 Week 1 的 Reddit 软启动！"
echo ""
