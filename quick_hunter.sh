#!/bin/bash
# Hunter风格Lead生成快速启动
# Quick start for Hunter-style lead generation

echo "🎯 MarketingMind AI - Hunter风格系统"
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
    echo "请先运行: python create_auth_manual.py"
    exit 1
fi

# 检查依赖
echo ""
echo "检查依赖..."
python -c "import dnspython" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少 dnspython，正在安装..."
    pip install dnspython>=2.4.0
fi

echo "✓ 依赖检查完成"
echo ""

# 参数
PRODUCT_DOC="${1:-saas_product_optimized.md}"
FOLLOWERS="${2:-100}"
SEEDS="${3:-10}"
DEEP_LIMIT="${4:-50}"

# 检查文档
if [ ! -f "$PRODUCT_DOC" ] && [[ ! "$PRODUCT_DOC" =~ ^https?:// ]]; then
    echo "❌ 找不到产品文档: $PRODUCT_DOC"
    echo ""
    echo "用法: ./quick_hunter.sh [产品文档] [粉丝数] [种子数] [深度爬取数]"
    echo ""
    echo "示例:"
    echo "  ./quick_hunter.sh                                    # 使用默认配置"
    echo "  ./quick_hunter.sh saas_product_optimized.md         # 指定文档"
    echo "  ./quick_hunter.sh product.md 200 15 100              # 自定义所有参数"
    echo ""
    echo "推荐配置:"
    echo "  小规模测试:  ./quick_hunter.sh product.md 50 3 20"
    echo "  中等规模:    ./quick_hunter.sh product.md 100 10 50"
    echo "  大规模:      ./quick_hunter.sh product.md 200 20 100"
    exit 1
fi

# 显示配置
echo "📄 产品文档: $PRODUCT_DOC"
echo ""
echo "⚙️  Hunter系统配置:"
echo "   - 每个账号爬取: $FOLLOWERS 个粉丝"
echo "   - 种子账号数: $SEEDS 个"
echo "   - 深度爬取数: $DEEP_LIMIT 个最有潜力的leads"
echo "   - 总leads: $((FOLLOWERS * SEEDS))"
echo ""

# 计算预期
TOTAL_LEADS=$((FOLLOWERS * SEEDS))
EMAIL_LOW=$((TOTAL_LEADS * 30 / 100))
EMAIL_HIGH=$((TOTAL_LEADS * 50 / 100))
TIME_LOW=$((SEEDS * 8 + 15))
TIME_HIGH=$((SEEDS * 12 + 25))

echo "📊 预期结果:"
echo "   - 邮箱数: $EMAIL_LOW - $EMAIL_HIGH 个 (30-50%)"
echo "   - 预计时间: $TIME_LOW - $TIME_HIGH 分钟"
echo ""

echo "🎯 Hunter系统特性:"
echo "   ✓ 深度主页爬取 (进入用户主页，不只是followers列表)"
echo "   ✓ 外部资源发现 (Linktree, 个人网站, Medium等)"
echo "   ✓ 邮箱模式推断 (从已知邮箱学习，推测新邮箱)"
echo "   ✓ LLM辅助分析 (智能优先排序)"
echo "   ✗ SMTP验证 (默认关闭，太慢)"
echo ""

read -p "开始运行Hunter系统? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 启动Hunter风格Lead生成系统..."
    echo "==========================================="
    echo ""

    # 运行系统
    python src/hunter_style_lead_generator.py "$PRODUCT_DOC" "$FOLLOWERS" "$SEEDS" "$DEEP_LIMIT"

    if [ $? -eq 0 ]; then
        echo ""
        echo "==========================================="
        echo "✅ Hunter系统运行完成！"
        echo "==========================================="
        echo ""

        # 查找最新文件
        LATEST_CSV=$(ls -t hunter_leads/leads_*.csv 2>/dev/null | head -1)
        LATEST_SUMMARY=$(ls -t hunter_leads/summary_*.json 2>/dev/null | head -1)

        if [ -n "$LATEST_CSV" ]; then
            echo "📁 结果文件:"
            echo "   CSV: $LATEST_CSV"
            echo "   JSON: ${LATEST_CSV%.csv}.json"
            echo "   摘要: $LATEST_SUMMARY"
            echo ""

            # 显示摘要
            if [ -n "$LATEST_SUMMARY" ]; then
                echo "📊 结果摘要:"
                python -c "
import json
with open('$LATEST_SUMMARY', 'r') as f:
    summary = json.load(f)
    print(f\"   总Leads: {summary.get('total_leads', 0)}\")
    print(f\"   有邮箱: {summary.get('leads_with_email', 0)} ({summary.get('email_rate', 0):.1f}%)\")
    print(f\"   深度爬取: {summary.get('deep_scraped', 0)}\")
    print(f\"   推测邮箱: {summary.get('guessed_emails', 0)}\")
    print(f\"   高质量: {summary.get('high_quality_leads', 0)}\")
" 2>/dev/null || echo "   (无法读取摘要)"
                echo ""
            fi

            echo "🔍 查看结果:"
            echo "   Excel/Numbers: open \"$LATEST_CSV\""
            echo "   浏览器查看目录: open hunter_leads/"
            echo ""

            # 对比基础系统（如果有）
            BASIC_LATEST=$(ls -t auto_leads/leads_*.csv 2>/dev/null | head -1)
            if [ -n "$BASIC_LATEST" ]; then
                echo "📊 与基础系统对比:"
                echo "   基础系统: open \"$BASIC_LATEST\""
                echo "   Hunter系统: open \"$LATEST_CSV\""
                echo ""
                echo "   对比邮箱率提升!"
            fi
        else
            echo "⚠️  未找到结果文件，请检查日志"
        fi

        echo "==========================================="
        echo ""
        echo "💡 提示:"
        echo "   - 邮箱率低？检查 HUNTER_STYLE_GUIDE.md"
        echo "   - 想提高质量？启用SMTP验证"
        echo "   - 想了解差异？查看 SYSTEM_COMPARISON.md"
        echo ""

    else
        echo ""
        echo "❌ Hunter系统运行失败"
        echo ""
        echo "🔍 故障排除:"
        echo "   1. 查看上面的错误信息"
        echo "   2. 检查 TROUBLESHOOTING.md"
        echo "   3. 确认API密钥: cat .env | grep ANTHROPIC_API_KEY"
        echo "   4. 运行小规模测试:"
        echo "      ./quick_hunter.sh product.md 10 1 5"
        echo ""
    fi
else
    echo "已取消"
fi
