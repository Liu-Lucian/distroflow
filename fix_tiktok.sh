#!/bin/bash
# TikTok评论修复工具启动脚本

echo "========================================================================"
echo "🔧 TikTok Comment Scraper Fix Tool"
echo "========================================================================"
echo ""

# 检查OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo ""
    read -p "Enter your OpenAI API Key: " api_key
    export OPENAI_API_KEY="$api_key"
fi

echo "✅ API Key set"
echo ""
echo "🤖 AI Healer will:"
echo "   1. Load a TikTok video"
echo "   2. Take a screenshot"
echo "   3. Analyze the page structure"
echo "   4. Generate correct comment selectors"
echo ""
read -p "Press Enter to start..."

python3 fix_tiktok_comments.py

echo ""
echo "✅ Done!"
