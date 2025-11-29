#!/bin/bash
# Ultimate Email Finder - 终极优化版
# 解决核心问题：激进的网站提取

echo "🎯 Ultimate Email Finder - 终极优化版"
echo "==========================================="
echo ""

# 激活环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 找不到venv"
    exit 1
fi

if [ ! -f "auth.json" ]; then
    echo "❌ 未找到auth.json"
    exit 1
fi

echo "✓ 准备就绪"
echo ""

# 参数
PRODUCT_DOC="${1:-saas_product_optimized.md}"
FOLLOWERS="${2:-50}"
SEEDS="${3:-3}"

echo "📄 配置:"
echo "   产品文档: $PRODUCT_DOC"
echo "   每账号粉丝: $FOLLOWERS"
echo "   种子账号数: $SEEDS"
echo "   预计总leads: $((FOLLOWERS * SEEDS))"
echo ""

echo "🔥 核心改进（解决缺少网站问题）:"
echo "   ✅ 7层网站提取策略"
echo "      1. Bio中的URL（多种模式）"
echo "      2. 访问用户主页提取网站链接"
echo "      3. 从最近推文中提取URL"
echo "      4. 从用户名推断网站"
echo "      5. 从Bio中的公司名推断"
echo "      6. 短链接展开"
echo "      7. Linktree解析"
echo ""
echo "   ✅ 激进的邮箱发现"
echo "      - 网站多页面爬取（/contact, /about, /team）"
echo "      - 模式推测（10种格式）"
echo "      - LLM智能推断"
echo "      - 混淆邮箱识别（name[at]domain[dot]com）"
echo ""

read -p "开始运行? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 启动Ultimate Email Finder..."
    echo "==========================================="

    python src/ultimate_email_finder.py "$PRODUCT_DOC" "$FOLLOWERS" "$SEEDS"

    if [ $? -eq 0 ]; then
        echo ""
        echo "==========================================="
        echo "✅ 运行完成！"
        echo "==========================================="

        # 诊断
        LATEST_JSON=$(ls -t ultimate_leads/leads_*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_JSON" ]; then
            echo ""
            echo "📊 运行诊断..."
            python diagnose_results.py "$LATEST_JSON"

            echo ""
            echo "📁 查看结果:"
            echo "   open ultimate_leads/"
        fi
    else
        echo "❌ 运行失败"
    fi
else
    echo "已取消"
fi
