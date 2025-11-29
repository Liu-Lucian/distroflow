#!/bin/bash
# Hunter Advanced 快速启动
# 基于Hunter.io完整流程的增强版

echo "🎯 Hunter Advanced - 增强版Lead生成"
echo "==========================================="
echo ""

# 激活环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Python环境已激活"
else
    echo "❌ 找不到venv"
    exit 1
fi

# 检查auth.json
if [ ! -f "auth.json" ]; then
    echo "❌ 未找到auth.json"
    exit 1
fi

echo "✓ 准备就绪"
echo ""

# 参数
PRODUCT_DOC="${1:-saas_product_optimized.md}"
FOLLOWERS="${2:-50}"  # 默认少一点，测试用
SEEDS="${3:-3}"

echo "📄 配置:"
echo "   产品文档: $PRODUCT_DOC"
echo "   每账号粉丝: $FOLLOWERS"
echo "   种子账号数: $SEEDS"
echo "   预计总leads: $((FOLLOWERS * SEEDS))"
echo ""

echo "🔬 增强功能:"
echo "   ✅ 立即深度爬取 (爬一个就深入一个)"
echo "   ✅ 外部资源爬取 (Linktree、个人网站)"
echo "   ✅ LLM辅助推断"
echo "   ✅ 模式推测 (即使没有已知邮箱也尝试)"
echo "   ✅ 多轮邮箱富化"
echo ""

read -p "开始运行? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 启动Hunter Advanced..."
    echo "==========================================="

    python src/hunter_advanced.py "$PRODUCT_DOC" "$FOLLOWERS" "$SEEDS"

    if [ $? -eq 0 ]; then
        echo ""
        echo "==========================================="
        echo "✅ 运行完成！"
        echo "==========================================="

        # 找到最新的JSON文件
        LATEST_JSON=$(ls -t hunter_advanced/leads_*.json 2>/dev/null | head -1)

        if [ -n "$LATEST_JSON" ]; then
            echo ""
            echo "📊 运行诊断分析..."
            python diagnose_results.py "$LATEST_JSON"

            echo ""
            echo "📁 查看结果:"
            echo "   open hunter_advanced/"
        fi
    else
        echo "❌ 运行失败"
    fi
else
    echo "已取消"
fi
