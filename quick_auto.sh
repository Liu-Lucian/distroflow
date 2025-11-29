#!/bin/bash
# 快速启动自动化Lead生成
# Quick start automated lead generation

echo "🤖 MarketingMind AI - 自动化Lead生成系统"
echo "=========================================="
echo ""

# 激活环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ 已激活Python环境"
else
    echo "❌ 找不到venv，请先运行: python -m venv venv"
    exit 1
fi

# 检查auth.json
if [ ! -f "auth.json" ]; then
    echo "⚠️  未找到auth.json"
    echo "请先运行: python create_auth_manual.py"
    exit 1
fi

echo "✓ 已找到登录信息"
echo ""

# 检查是否提供了产品文档
if [ -z "$1" ]; then
    echo "使用示例产品文档..."
    PRODUCT_DOC="example_product.md"
else
    PRODUCT_DOC="$1"
fi

# 检查文档是否存在
if [ ! -f "$PRODUCT_DOC" ] && [[ ! "$PRODUCT_DOC" =~ ^https?:// ]]; then
    echo "❌ 找不到文档: $PRODUCT_DOC"
    echo ""
    echo "用法: ./quick_auto.sh [产品文档路径]"
    echo "示例: ./quick_auto.sh my_product.md"
    echo "      ./quick_auto.sh product.pdf"
    echo "      ./quick_auto.sh https://myproduct.com/about"
    exit 1
fi

echo "📄 产品文档: $PRODUCT_DOC"
echo ""

# 设置参数
FOLLOWERS_PER="${2:-100}"
MAX_SEEDS="${3:-10}"

echo "⚙️  配置:"
echo "   - 每个账号爬取: $FOLLOWERS_PER 个粉丝"
echo "   - 最多种子账号: $MAX_SEEDS 个"
echo "   - 预计leads数: $((FOLLOWERS_PER * MAX_SEEDS))"
echo "   - 预计时间: $((MAX_SEEDS * 5 + 10))-$((MAX_SEEDS * 8 + 15)) 分钟"
echo ""

read -p "开始运行? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 启动自动化系统..."
    echo "=========================================="
    python src/auto_lead_generator.py "$PRODUCT_DOC" "$FOLLOWERS_PER" "$MAX_SEEDS"

    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "✅ 完成！"
        echo ""
        echo "📁 查看结果:"
        echo "   open auto_leads/"
        echo ""
        echo "或查看最新文件:"
        LATEST_CSV=$(ls -t auto_leads/leads_*.csv 2>/dev/null | head -1)
        if [ -n "$LATEST_CSV" ]; then
            echo "   open \"$LATEST_CSV\""
        fi
    else
        echo ""
        echo "❌ 运行失败"
    fi
else
    echo "已取消"
fi
