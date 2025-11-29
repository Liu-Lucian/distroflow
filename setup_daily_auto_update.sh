#!/bin/bash
# Product Hunt 每日自动更新 - 定时任务设置脚本

echo "=================================================="
echo "🤖 Product Hunt 每日自动更新 - 定时任务设置"
echo "=================================================="

# 获取当前目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "✅ 工作目录: $SCRIPT_DIR"
echo ""

# 检查环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 创建运行脚本
cat > "$SCRIPT_DIR/run_daily_update.sh" << 'EOF'
#!/bin/bash

# 设置工作目录
cd "$(dirname "$0")"

# 设置 API Key（请替换为实际的 key）
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'

# 记录日志
echo "=================================================="
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始每日产品列表更新"
echo "=================================================="

# 运行更新脚本
python3 auto_update_product_list_daily.py

# 记录完成
echo "=================================================="
echo "$(date '+%Y-%m-%d %H:%M:%S') - 更新完成"
echo "=================================================="
EOF

chmod +x "$SCRIPT_DIR/run_daily_update.sh"

echo "✅ 已创建运行脚本: run_daily_update.sh"
echo ""

# 显示 crontab 配置示例
echo "📋 定时任务配置（选择一种方式）:"
echo ""
echo "方式 1: 使用 crontab（推荐）"
echo "----------------------------------------"
echo "1. 编辑 crontab:"
echo "   crontab -e"
echo ""
echo "2. 添加以下行（每天早上 9 点更新）:"
echo "   0 9 * * * cd \"$SCRIPT_DIR\" && ./run_daily_update.sh >> daily_update.log 2>&1"
echo ""
echo "   或者（每天下午 2 点更新）:"
echo "   0 14 * * * cd \"$SCRIPT_DIR\" && ./run_daily_update.sh >> daily_update.log 2>&1"
echo ""
echo "3. 保存并退出"
echo ""

echo "方式 2: 使用 launchd（macOS）"
echo "----------------------------------------"
echo "1. 创建 plist 文件:"
echo "   ~/Library/LaunchAgents/com.producthunt.daily-update.plist"
echo ""
echo "2. 内容如下:"
cat << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.producthunt.daily-update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>SCRIPT_DIR/run_daily_update.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>SCRIPT_DIR/daily_update.log</string>
    <key>StandardErrorPath</key>
    <string>SCRIPT_DIR/daily_update_error.log</string>
</dict>
</plist>
PLIST
echo ""
echo "   （记得替换 SCRIPT_DIR 为实际路径）"
echo ""
echo "3. 加载任务:"
echo "   launchctl load ~/Library/LaunchAgents/com.producthunt.daily-update.plist"
echo ""

echo "方式 3: 手动运行（测试用）"
echo "----------------------------------------"
echo "   ./run_daily_update.sh"
echo ""

echo "=================================================="
echo "✅ 设置完成！"
echo ""
echo "💡 提示:"
echo "   • 确保 run_daily_update.sh 中的 API Key 正确"
echo "   • 建议先手动运行测试一次"
echo "   • 日志会保存到 daily_update.log"
echo ""
echo "=================================================="
