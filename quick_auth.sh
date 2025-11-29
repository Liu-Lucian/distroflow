#!/bin/bash
# 快速认证脚本 - 5秒搞定 GitHub 推送

echo ""
echo "🔐 GitHub 快速认证"
echo ""
echo "请输入你的 GitHub Personal Access Token:"
echo "(访问 https://github.com/settings/tokens 创建，权限勾选 'repo')"
echo ""
read -p "Token: " token

if [ -z "$token" ]; then
    echo "❌ Token 不能为空"
    exit 1
fi

# 配置远程 URL
cd interview_assistant
git remote set-url origin "https://${token}@github.com/q1q1-spefic/interview_assistant.git"

echo ""
echo "✅ 认证配置完成！"
echo ""
echo "测试推送..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 推送成功！系统已就绪。"
    echo ""
    echo "现在可以运行："
    echo "  python3 github_gradual_publisher.py --forever"
else
    echo ""
    echo "❌ 推送失败，请检查 token 权限"
fi
