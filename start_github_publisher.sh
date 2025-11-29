#!/bin/bash
################################################################################
# GitHub 挤牙膏式发布 - 一键启动脚本
#
# 自动将 interview_assistant 项目逐步发布到 GitHub
# 增加 activity 和 commit 频率，提高曝光度
#
# 使用方法：
#   chmod +x start_github_publisher.sh
#   ./start_github_publisher.sh
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}$1${NC}"
    echo "================================================================================"
    echo ""
}

cd "$(dirname "$0")"

print_header "🚀 GitHub 挤牙膏式发布系统"

# 检查源代码目录
SOURCE_DIR="/Users/l.u.c/my-app/interview_assistant"
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "源代码目录不存在: $SOURCE_DIR"
    exit 1
fi
print_success "源代码目录: $SOURCE_DIR"

# 检查 Git
if ! command -v git &> /dev/null; then
    print_error "Git 未安装"
    exit 1
fi
print_success "Git 已安装"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 未安装"
    exit 1
fi
print_success "Python 3 已安装"

# 显示状态
print_header "📊 当前状态"
python3 github_gradual_publisher.py --status || true

echo ""
echo "================================================================================"
echo -e "${YELLOW}选择操作模式${NC}"
echo "================================================================================"
echo ""
echo "1. 初始化仓库 (首次运行)"
echo "2. 执行一次提交"
echo "3. 永久运行 (自动定期提交)"
echo "4. 查看状态"
echo "5. 退出"
echo ""
read -p "请选择 (1-5): " choice

case $choice in
    1)
        print_header "📦 初始化 Git 仓库"
        python3 github_gradual_publisher.py --init
        ;;
    2)
        print_header "📤 执行一次提交"
        python3 github_gradual_publisher.py --once
        ;;
    3)
        print_header "🔄 启动永久运行模式"
        echo ""
        echo "系统将："
        echo "  • 每天提交 1-3 次"
        echo "  • 每 6 小时检查一次"
        echo "  • 智能选择提交时间窗口"
        echo "  • 按逻辑顺序逐步发布模块"
        echo ""
        echo "预计完成时间: 15-30 天"
        echo ""
        read -p "确认启动？(y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            print_success "系统已启动..."
            python3 github_gradual_publisher.py --forever
        else
            print_warning "已取消"
        fi
        ;;
    4)
        print_header "📊 查看状态"
        python3 github_gradual_publisher.py --status
        ;;
    5)
        print_info "再见！"
        exit 0
        ;;
    *)
        print_error "无效选择"
        exit 1
        ;;
esac

print_success "完成！"
