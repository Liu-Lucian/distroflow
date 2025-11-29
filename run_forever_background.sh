#!/bin/bash
# 后台运行发布系统

cd "$(dirname "$0")"

# 加载 token
if [ -f GITHUB_TOKEN.env ]; then
    source GITHUB_TOKEN.env
fi

# 后台运行，输出重定向到日志
nohup python3 github_gradual_publisher.py --forever >> github_publisher.log 2>&1 &

PID=$!
echo "🚀 发布系统已在后台启动"
echo "进程 ID: $PID"
echo ""
echo "查看日志:"
echo "  tail -f github_publisher.log"
echo ""
echo "停止系统:"
echo "  kill $PID"
echo ""
echo "PID 已保存到 publisher.pid"
echo $PID > publisher.pid
