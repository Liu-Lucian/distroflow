#!/bin/bash
################################################################################
# GitHub 发布系统 - 一键完整设置
#
# 功能:
# 1. 收集 GitHub token
# 2. 通过 API 创建仓库（如果不存在）
# 3. 配置 Git 认证
# 4. 推送第一个 commit
# 5. 启动永久发布系统
################################################################################

set -e

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  GitHub 挤牙膏式发布系统 - 一键完整设置"
echo "════════════════════════════════════════════════════════════"
echo ""

# ===== 第 1 步：获取 Token =====
echo "📋 第 1 步：GitHub Personal Access Token"
echo ""
echo "如果你还没有 token，请访问："
echo "  https://github.com/settings/tokens"
echo ""
echo "点击 'Generate new token (classic)'，权限勾选："
echo "  ✓ repo (完整仓库访问)"
echo "  ✓ delete_repo (可选，用于删除/重建仓库)"
echo ""
read -p "请输入你的 GitHub Token: " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token 不能为空"
    exit 1
fi

echo ""
echo "✅ Token 已收集"

# ===== 第 2 步：检查/创建仓库 =====
echo ""
echo "📦 第 2 步：检查 GitHub 仓库是否存在..."

REPO_NAME="interview_assistant"
REPO_OWNER="q1q1-spefic"

# 检查仓库是否存在
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ 仓库已存在: https://github.com/$REPO_OWNER/$REPO_NAME"
elif [ "$HTTP_STATUS" = "404" ]; then
    echo "📝 仓库不存在，正在创建..."

    # 创建仓库
    CREATE_RESPONSE=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/user/repos" \
        -d "{
            \"name\": \"$REPO_NAME\",
            \"description\": \"AI-Powered Interview Assistant - Your Personal Interview Coach\",
            \"private\": false,
            \"auto_init\": false
        }")

    # 检查是否创建成功
    if echo "$CREATE_RESPONSE" | grep -q "\"full_name\""; then
        echo "✅ 仓库创建成功: https://github.com/$REPO_OWNER/$REPO_NAME"
    else
        echo "❌ 仓库创建失败"
        echo "响应: $CREATE_RESPONSE"
        echo ""
        echo "可能的原因："
        echo "  1. Token 权限不足（需要 'repo' 权限）"
        echo "  2. 仓库名已被占用"
        echo "  3. 网络问题"
        echo ""
        echo "请手动创建仓库："
        echo "  https://github.com/new"
        echo "  仓库名: $REPO_NAME"
        echo ""
        read -p "仓库创建完成后按回车继续..."
    fi
else
    echo "⚠️  无法检查仓库状态 (HTTP $HTTP_STATUS)"
    echo "Token 可能无效或权限不足"
    echo ""
    read -p "如果仓库已存在，按回车继续。否则按 Ctrl+C 退出..."
fi

# ===== 第 3 步：配置 Git 认证 =====
echo ""
echo "🔐 第 3 步：配置 Git 认证..."

cd interview_assistant

# 配置远程 URL (包含 token)
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/$REPO_OWNER/$REPO_NAME.git"

echo "✅ Git 认证配置完成"

# ===== 第 4 步：测试推送 =====
echo ""
echo "🚀 第 4 步：推送第一个 commit 到 GitHub..."

# 检查是否有未推送的 commits
UNPUSHED_COUNT=$(git log --oneline 2>/dev/null | wc -l | tr -d ' ')

if [ "$UNPUSHED_COUNT" -gt 0 ]; then
    echo "📦 发现 $UNPUSHED_COUNT 个未推送的 commit"

    # 尝试推送
    if git push -u origin main 2>&1; then
        echo ""
        echo "🎉 推送成功！"
        echo ""
        echo "查看仓库："
        echo "  https://github.com/$REPO_OWNER/$REPO_NAME"
        echo ""
    else
        echo ""
        echo "❌ 推送失败"
        echo ""
        echo "可能的原因："
        echo "  1. Token 权限不足"
        echo "  2. 仓库不存在或无访问权限"
        echo "  3. 网络问题"
        echo ""
        echo "请检查并重试"
        exit 1
    fi
else
    echo "ℹ️  没有本地 commits 需要推送"
    echo "系统将在下次运行时创建第一个 commit"
fi

cd ..

# ===== 第 5 步：保存 Token 到环境变量文件 =====
echo ""
echo "💾 第 5 步：保存配置..."

cat > GITHUB_TOKEN.env << EOF
# GitHub Personal Access Token 配置
# 自动生成于: $(date)

export GITHUB_TOKEN=$GITHUB_TOKEN

# 使用方法：
# source GITHUB_TOKEN.env
# python3 github_gradual_publisher.py --forever
EOF

echo "✅ Token 已保存到 GITHUB_TOKEN.env"

# ===== 第 6 步：启动发布系统 =====
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ 设置完成！"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "下一步："
echo ""
echo "选项 1: 立即启动永久运行模式"
echo "  python3 github_gradual_publisher.py --forever"
echo ""
echo "选项 2: 先查看状态"
echo "  python3 github_gradual_publisher.py --status"
echo ""
echo "选项 3: 手动提交一次"
echo "  python3 github_gradual_publisher.py --once"
echo ""

read -p "是否立即启动永久运行模式？(y/N): " START_NOW

if [ "$START_NOW" = "y" ] || [ "$START_NOW" = "Y" ]; then
    echo ""
    echo "🤖 启动发布系统..."
    echo ""
    export GITHUB_TOKEN=$GITHUB_TOKEN
    exec python3 github_gradual_publisher.py --forever
else
    echo ""
    echo "使用以下命令启动："
    echo "  source GITHUB_TOKEN.env"
    echo "  python3 github_gradual_publisher.py --forever"
    echo ""
fi
