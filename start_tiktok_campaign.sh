#!/bin/bash
# TikTok智能营销系统 - 一键启动脚本

echo "======================================================================"
echo "🎵 TikTok Smart Marketing Campaign"
echo "======================================================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "run_tiktok_campaign_optimized.py" ]; then
    echo "❌ 错误: 请在 MarketingMind AI 目录下运行此脚本"
    exit 1
fi

# 检查 OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 环境变量未设置"
    echo ""
    read -p "请输入你的 OpenAI API Key: " api_key
    export OPENAI_API_KEY="$api_key"
fi

echo "✅ OpenAI API Key 已设置"
echo ""

# 检查 platforms_auth.json
if [ ! -f "platforms_auth.json" ]; then
    echo "❌ 错误: platforms_auth.json 文件不存在"
    echo ""
    echo "请创建 platforms_auth.json 文件，格式如下："
    echo '{'
    echo '  "tiktok": {'
    echo '    "sessionid": "your_tiktok_sessionid_here"'
    echo '  }'
    echo '}'
    echo ""
    exit 1
fi

echo "✅ TikTok 认证文件已找到"
echo ""

# 显示配置
echo "📊 运行配置:"
echo "  - 关键词: job interview, career advice, job search tips"
echo "  - AI 模型: GPT-4o-mini (批量处理)"
echo "  - 预估成本: ~\$0.006 首次运行, \$0 缓存命中"
echo "  - 每批次: 5 个用户"
echo "  - 延迟: 1-3 分钟/用户"
echo ""

read -p "按 Enter 开始运行，或 Ctrl+C 取消..."
echo ""

# 运行
python3 run_tiktok_campaign_optimized.py

echo ""
echo "======================================================================"
echo "✅ 运行完成!"
echo "======================================================================"
echo ""
echo "📋 查看结果:"
echo "  - 合格用户: tiktok_qualified_users.json"
echo "  - 缓存: cache/tiktok_analyzed_comments.json"
echo ""
echo "💡 提示:"
echo "  - 第二次运行相同关键词将使用缓存 (成本 = \$0)"
echo "  - 修改关键词请编辑 run_tiktok_campaign_optimized.py"
echo "  - 修改每批次DM数量: DM_BATCH_SIZE"
echo ""
