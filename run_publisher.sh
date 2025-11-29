#!/bin/bash
################################################################################
# GitHub 发布系统启动包装脚本
# 自动检查认证并启动发布系统
################################################################################

set -e

cd "$(dirname "$0")"

echo "🚀 启动 GitHub 挤牙膏式发布系统"
echo ""

# 1. 检查 GITHUB_TOKEN 环境变量
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ 检测到 GITHUB_TOKEN 环境变量"
    echo "🔐 配置 Git 认证..."

    cd interview_assistant
    git remote set-url origin "https://${GITHUB_TOKEN}@github.com/q1q1-spefic/interview_assistant.git"
    cd ..

    echo "✅ 认证配置完成"
    echo ""
else
    echo "⚠️  未检测到 GITHUB_TOKEN 环境变量"
    echo ""

    # 2. 检查是否有 GITHUB_TOKEN.env 文件
    if [ -f "GITHUB_TOKEN.env" ]; then
        # 检查文件中是否有未注释的 token
        if grep -q "^GITHUB_TOKEN=" GITHUB_TOKEN.env; then
            echo "📄 发现 GITHUB_TOKEN.env 文件，自动加载..."
            source GITHUB_TOKEN.env

            if [ -n "$GITHUB_TOKEN" ]; then
                echo "✅ Token 加载成功"
                cd interview_assistant
                git remote set-url origin "https://${GITHUB_TOKEN}@github.com/q1q1-spefic/interview_assistant.git"
                cd ..
                echo "✅ 认证配置完成"
                echo ""
            fi
        else
            echo "⚠️  GITHUB_TOKEN.env 文件存在但未配置"
            echo ""
            echo "请编辑 GITHUB_TOKEN.env 文件并填写 token，然后重新运行。"
            echo ""
            exit 1
        fi
    else
        echo "❌ 未找到认证配置"
        echo ""
        echo "请选择一种方式配置 GitHub 认证："
        echo "  1. ./quick_auth.sh (最快)"
        echo "  2. ./setup_github_auth.sh (完整配置)"
        echo "  3. 手动配置 GITHUB_TOKEN.env"
        echo ""
        exit 1
    fi
fi

# 3. 测试 Git 推送
echo "🧪 测试 Git 推送权限..."
cd interview_assistant

# 尝试 fetch 来测试权限
if git ls-remote origin &>/dev/null; then
    echo "✅ Git 认证测试成功"
    echo ""
else
    echo "❌ Git 认证测试失败"
    echo ""
    echo "请检查："
    echo "  1. Token 权限是否包含 'repo'"
    echo "  2. Token 是否仍然有效"
    echo "  3. 仓库是否存在"
    echo ""
    cd ..
    exit 1
fi

cd ..

# 4. 启动发布系统
echo "================================================================================"
echo "🤖 启动发布系统（永久运行模式）"
echo "================================================================================"
echo ""

exec python3 github_gradual_publisher.py --forever
