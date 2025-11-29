#!/bin/bash
# Substack Autopilot - 一键启动脚本

set -e

echo "================================================================================"
echo "🚀 Substack Autopilot - 永不停息的增长引擎"
echo "================================================================================"
echo ""

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查环境
echo "📋 检查环境..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY 未设置${NC}"
    echo ""
    echo "请先设置API key:"
    echo "export OPENAI_API_KEY='sk-proj-...'"
    exit 1
fi

echo -e "${GREEN}✅ API key 已设置${NC}"

# 检查文件
if [ ! -f "substack_auth.json" ]; then
    echo -e "${YELLOW}⚠️  substack_auth.json 不存在${NC}"
    echo "请先登录Substack并保存cookies"
    echo ""
fi

# 显示菜单
echo ""
echo "请选择运行模式:"
echo ""
echo "1) 🔄 测试运行一次 (推荐先测试)"
echo "2) ⚡ 持续运行 (需要保持终端开启) - 推荐!"
echo "3) 🤖 设置后台服务 (launchd - 永久运行)"
echo "4) 📅 仅安排文章发布"
echo "5) 💬 仅运行评论系统"
echo "6) 📊 查看统计信息"
echo "7) 📖 查看帮助文档"
echo ""
read -p "输入选项 (1-7): " choice

case $choice in
    1)
        echo ""
        echo "================================================================================"
        echo "🔄 测试运行一次"
        echo "================================================================================"
        echo ""
        echo "这将运行:"
        echo "  ✅ 检查是否需要安排新文章（每7天一次）"
        echo "  ✅ 运行一次评论养号"
        echo ""
        python3 substack_master.py --once
        echo ""
        echo -e "${GREEN}✅ 测试完成！${NC}"
        ;;

    2)
        echo ""
        echo "================================================================================"
        echo "⚡ 持续运行模式 - 推荐！"
        echo "================================================================================"
        echo ""
        echo "系统将自动:"
        echo "  📅 每7天自动安排新文章发布"
        echo "  💬 每天3次自动评论（09:00、14:00、20:00）"
        echo "  🔄 完全自动化，无需手动干预"
        echo ""
        echo -e "${YELLOW}⚠️  注意: 需要保持此终端窗口开启${NC}"
        echo "按 Ctrl+C 可以停止"
        echo ""
        read -p "按Enter继续，或Ctrl+C取消..."

        python3 substack_master.py --continuous
        ;;

    3)
        echo ""
        echo "================================================================================"
        echo "🤖 设置后台服务 (launchd)"
        echo "================================================================================"
        echo ""
        echo "这将设置macOS后台服务，即使关闭终端或重启电脑也会继续运行"
        echo ""
        read -p "继续? (y/n): " confirm

        if [ "$confirm" = "y" ]; then
            PLIST_FILE=~/Library/LaunchAgents/com.substack.autopilot.plist

            # 创建plist文件
            cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.substack.autopilot</string>

    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$(pwd)/substack_master.py</string>
        <string>--once</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$(pwd)</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>${OPENAI_API_KEY}</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>14</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>20</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>

    <key>StandardOutPath</key>
    <string>/tmp/substack_autopilot.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/substack_autopilot_error.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

            # 加载服务
            echo ""
            echo "正在加载launchd服务..."
            launchctl unload "$PLIST_FILE" 2>/dev/null || true
            launchctl load "$PLIST_FILE"

            echo ""
            echo -e "${GREEN}✅ 后台服务已设置！${NC}"
            echo ""
            echo "服务功能:"
            echo "  📅 自动安排文章发布（每7天）"
            echo "  💬 自动评论养号（每天3次：09:00、14:00、20:00）"
            echo "  🔄 完全自动化，永久运行"
            echo ""
            echo "管理命令:"
            echo "  查看日志: tail -f /tmp/substack_autopilot.log"
            echo "  停止服务: launchctl stop com.substack.autopilot"
            echo "  卸载服务: launchctl unload ~/Library/LaunchAgents/com.substack.autopilot.plist"
            echo ""
            echo "立即测试运行? (y/n): "
            read test
            if [ "$test" = "y" ]; then
                launchctl start com.substack.autopilot
                echo "等待3秒..."
                sleep 3
                tail -30 /tmp/substack_autopilot.log
            fi
        fi
        ;;

    4)
        echo ""
        echo "================================================================================"
        echo "📅 安排文章发布"
        echo "================================================================================"
        echo ""
        python3 schedule_substack_posts.py
        ;;

    5)
        echo ""
        echo "================================================================================"
        echo "💬 运行评论系统"
        echo "================================================================================"
        echo ""
        python3 substack_comment_farmer.py
        ;;

    6)
        echo ""
        echo "================================================================================"
        echo "📊 统计信息"
        echo "================================================================================"
        echo ""

        if [ -f "substack_commented_posts.json" ]; then
            echo "评论历史:"
            python3 <<EOF
import json
from datetime import datetime

try:
    with open('substack_commented_posts.json', 'r') as f:
        history = json.load(f)

    total = len(history)
    print(f"  总评论数: {total}")

    if total > 0:
        today = datetime.now().date()
        today_comments = [p for p in history if datetime.fromisoformat(p['commented_at']).date() == today]
        print(f"  今日评论: {len(today_comments)}")

        # 最近5条
        print("\n  最近5条评论:")
        for p in history[-5:]:
            dt = datetime.fromisoformat(p['commented_at'])
            print(f"    - {dt.strftime('%m/%d %H:%M')} - {p['title'][:50]}")
except FileNotFoundError:
    print("  还没有评论记录")
except Exception as e:
    print(f"  错误: {e}")
EOF
        else
            echo "  还没有评论记录"
        fi

        echo ""
        echo "文件状态:"
        echo "  substack_auth.json: $([ -f substack_auth.json ] && echo '✅ 存在' || echo '❌ 不存在')"
        echo "  substack_commented_posts.json: $([ -f substack_commented_posts.json ] && echo '✅ 存在' || echo '❌ 不存在')"
        echo ""
        ;;

    7)
        echo ""
        echo "================================================================================"
        echo "📖 帮助文档"
        echo "================================================================================"
        echo ""
        echo "主要文档:"
        echo "  - SUBSTACK_AUTOPILOT_SETUP.md    完整设置指南"
        echo "  - SUBSTACK_SCHEDULE_GUIDE.md     定时发布指南"
        echo "  - SUBSTACK_COMMENT_FARMING_GUIDE.md    评论系统指南"
        echo ""
        echo "快速开始:"
        echo "  1. 先运行选项4安排文章发布"
        echo "  2. 然后运行选项3设置后台服务"
        echo "  3. 系统将自动运行，永不停息！"
        echo ""
        ;;

    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo "完成！"
echo "================================================================================"
