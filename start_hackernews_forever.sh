#!/bin/bash
################################################################################
# HN 自动化永久运行脚本
#
# 功能：一个命令搞定 Hacker News 自动发帖 + 评论
#
# 使用方法：
#   chmod +x start_hackernews_forever.sh
#   ./start_hackernews_forever.sh
#
# 或者后台运行：
#   screen -S hackernews
#   ./start_hackernews_forever.sh
#   # 按 Ctrl+A, D 分离会话
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
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

# 进入脚本所在目录
cd "$(dirname "$0")"

print_header "🤖 HN 自动化系统 - 永久运行模式"

# 1. 检查 API Key
print_info "检查 ANTHROPIC_API_KEY..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_warning "ANTHROPIC_API_KEY 未设置，尝试从环境变量加载..."

    # 尝试从 .env 文件加载
    if [ -f .env ]; then
        export $(cat .env | grep ANTHROPIC_API_KEY | xargs)
        print_success "从 .env 加载 API Key"
    else
        # 使用默认 API Key
        export ANTHROPIC_API_KEY='sk-ant-YOUR_ANTHROPIC_API_KEY_HERE'
        print_success "使用默认 API Key"
    fi
else
    print_success "ANTHROPIC_API_KEY 已设置"
fi

# 2. 检查登录状态
print_info "检查 HN 登录状态..."
if [ ! -f hackernews_auth.json ]; then
    print_error "未找到 hackernews_auth.json"
    print_info "请先运行: python3 hackernews_login_and_save_auth.py"
    exit 1
else
    print_success "登录凭证已存在"
fi

# 3. 检查 Python 依赖
print_info "检查 Python 依赖..."
if ! python3 -c "import anthropic" 2>/dev/null; then
    print_warning "anthropic 库未安装，正在安装..."
    pip3 install anthropic
fi

if ! python3 -c "import playwright" 2>/dev/null; then
    print_warning "playwright 库未安装，正在安装..."
    pip3 install playwright
    playwright install chromium
fi

print_success "依赖检查完成"

# 4. 创建必要目录
print_info "创建必要目录..."
mkdir -p schedules
mkdir -p logs
print_success "目录创建完成"

# 5. 显示当前状态
print_header "📊 当前系统状态"
python3 hackernews_master.py --status || true

# 6. 确认启动
echo ""
echo "================================================================================"
echo -e "${YELLOW}⚠️  准备启动永久运行模式${NC}"
echo "================================================================================"
echo ""
echo "系统将会："
echo "  • 每月自动发布 5 篇帖子（1 Show HN + 4 Ask HN）"
echo "  • 每天自动发布 2-3 条技术评论"
echo "  • 每 2 小时检查一次是否需要执行任务"
echo "  • 智能控制频率，避免被检测"
echo ""
echo "日志保存位置："
echo "  • 主日志: hackernews_master.log"
echo "  • 实时输出: 终端显示"
echo ""
echo "停止方法："
echo "  • 按 Ctrl+C 停止"
echo "  • 如果在 screen 中: Ctrl+A, K 或 screen -X -S hackernews quit"
echo ""
read -p "确认启动？(y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "已取消启动"
    exit 0
fi

# 7. 启动系统
print_header "🚀 启动 HN 自动化系统"

print_info "启动时间: $(date '+%Y-%m-%d %H:%M:%S')"
print_info "进程 PID: $$"
print_info "日志文件: hackernews_master.log"
echo ""

# 捕获 Ctrl+C 信号
trap 'echo -e "\n${YELLOW}⚠️  收到中断信号，正在优雅关闭...${NC}"; exit 0' INT TERM

# 启动主程序
print_success "系统已启动，进入永久运行模式..."
echo ""
echo "================================================================================"
echo ""

# 运行主程序
python3 hackernews_master.py --forever

# 如果程序退出
echo ""
print_warning "系统已停止"
