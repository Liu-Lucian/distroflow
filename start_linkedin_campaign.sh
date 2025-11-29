#!/bin/bash
# LinkedIn DM Campaign启动脚本

cd "/Users/l.u.c/my-app/MarketingMind AI"

echo "======================================================================"
echo "💼 LinkedIn DM Campaign"
echo "======================================================================"
echo ""
echo "请选择操作："
echo ""
echo "1. 编辑用户列表 (linkedin_target_users.json)"
echo "2. 运行DM发送脚本"
echo "3. 查看进度"
echo "4. 查看使用指南"
echo "5. 测试DM发送（手动模式）"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
  1)
    echo ""
    echo "📝 打开用户列表文件..."
    if [ -f "linkedin_target_users.json" ]; then
      open linkedin_target_users.json
    else
      echo "⚠️  文件不存在，先运行选项2创建示例文件"
    fi
    ;;

  2)
    echo ""
    echo "🚀 启动DM发送..."
    python3 linkedin_dm_from_list.py
    ;;

  3)
    echo ""
    echo "📊 当前进度:"
    echo "======================================================================"
    if [ -f "linkedin_dm_progress.json" ]; then
      cat linkedin_dm_progress.json | python3 -m json.tool
    else
      echo "⚠️  还没有进度记录"
    fi
    echo ""
    if [ -f "linkedin_target_users.json" ]; then
      total=$(python3 -c "import json; f=open('linkedin_target_users.json'); users=json.load(f); print(len(users))")
      sent=$(python3 -c "import json; f=open('linkedin_target_users.json'); users=json.load(f); print(len([u for u in users if u.get('sent_dm', False)]))")
      echo "总用户数: $total"
      echo "已发送: $sent"
      echo "待发送: $((total - sent))"
    fi
    echo "======================================================================"
    ;;

  4)
    echo ""
    echo "📖 打开使用指南..."
    open LINKEDIN_DM_GUIDE.md
    ;;

  5)
    echo ""
    echo "🧪 启动测试模式（你需要手动操作浏览器）..."
    python3 linkedin_manual_test.py
    ;;

  *)
    echo "❌ 无效选项"
    ;;
esac

echo ""
echo "✅ 完成"
