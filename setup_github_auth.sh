#!/bin/bash
################################################################################
# GitHub 认证设置脚本
#
# 帮助配置 GitHub 推送认证
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

cd "$(dirname "$0")"

echo ""
echo "================================================================================"
echo -e "${GREEN}🔐 GitHub 认证设置${NC}"
echo "================================================================================"
echo ""

echo "选择认证方式："
echo ""
echo "1. SSH 密钥 (推荐 - 最安全)"
echo "2. Personal Access Token (简单但需要保存 token)"
echo "3. GitHub CLI (需要安装 gh)"
echo ""
read -p "请选择 (1-3): " choice

case $choice in
    1)
        # SSH 方式
        echo ""
        echo "================================================================================"
        echo "SSH 密钥认证"
        echo "================================================================================"
        echo ""

        # 检查 SSH 密钥
        if [ -f ~/.ssh/id_rsa.pub ] || [ -f ~/.ssh/id_ed25519.pub ]; then
            print_success "SSH 密钥已存在"
            echo ""
            echo "你的公钥："
            if [ -f ~/.ssh/id_ed25519.pub ]; then
                cat ~/.ssh/id_ed25519.pub
            else
                cat ~/.ssh/id_rsa.pub
            fi
            echo ""
        else
            print_info "生成新的 SSH 密钥..."
            ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519 -N ""
            print_success "SSH 密钥已生成"
            echo ""
            echo "你的公钥："
            cat ~/.ssh/id_ed25519.pub
            echo ""
        fi

        echo "请按照以下步骤操作："
        echo "1. 复制上面的公钥"
        echo "2. 访问 https://github.com/settings/keys"
        echo "3. 点击 'New SSH key'"
        echo "4. 粘贴公钥并保存"
        echo ""
        read -p "完成后按 Enter 继续..."

        # 更改远程 URL 为 SSH
        cd interview_assistant 2>/dev/null || { print_error "interview_assistant 目录不存在"; exit 1; }
        git remote set-url origin git@github.com:q1q1-spefic/interview_assistant.git
        print_success "远程 URL 已更改为 SSH"

        # 测试连接
        echo ""
        print_info "测试 SSH 连接..."
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            print_success "SSH 连接成功！"
        else
            print_warning "SSH 连接测试失败，但可能是正常的（GitHub 会拒绝 shell 访问）"
        fi
        ;;

    2)
        # Personal Access Token
        echo ""
        echo "================================================================================"
        echo "Personal Access Token 认证"
        echo "================================================================================"
        echo ""

        echo "请按照以下步骤操作："
        echo "1. 访问 https://github.com/settings/tokens"
        echo "2. 点击 'Generate new token' -> 'Generate new token (classic)'"
        echo "3. 设置权限：至少勾选 'repo' (完整仓库访问权限)"
        echo "4. 点击 'Generate token' 并复制 token"
        echo ""
        echo "⚠️  重要：token 只显示一次，请妥善保存！"
        echo ""
        read -p "请输入 Personal Access Token: " token

        if [ -z "$token" ]; then
            print_error "Token 不能为空"
            exit 1
        fi

        # 更改远程 URL 包含 token
        cd interview_assistant 2>/dev/null || { print_error "interview_assistant 目录不存在"; exit 1; }
        git remote set-url origin "https://${token}@github.com/q1q1-spefic/interview_assistant.git"
        print_success "远程 URL 已配置 Token"

        # 保存 token 到 git credential
        echo ""
        read -p "是否保存 token 到 Git credential helper? (y/N): " save_cred
        if [[ $save_cred =~ ^[Yy]$ ]]; then
            git config --global credential.helper store
            print_success "Token 将被保存（存储在 ~/.git-credentials）"
        fi
        ;;

    3)
        # GitHub CLI
        echo ""
        echo "================================================================================"
        echo "GitHub CLI 认证"
        echo "================================================================================"
        echo ""

        # 检查 gh 是否安装
        if ! command -v gh &> /dev/null; then
            print_error "GitHub CLI (gh) 未安装"
            echo ""
            echo "安装方法："
            echo "  macOS: brew install gh"
            echo "  Linux: 参考 https://github.com/cli/cli#installation"
            exit 1
        fi

        print_info "启动 GitHub CLI 认证..."
        gh auth login

        # 配置 git 使用 gh
        gh auth setup-git

        print_success "GitHub CLI 认证完成！"
        ;;

    *)
        print_error "无效选择"
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo -e "${GREEN}✅ 认证设置完成！${NC}"
echo "================================================================================"
echo ""
echo "现在可以测试推送："
echo "  cd interview_assistant"
echo "  git push -u origin main"
echo ""
