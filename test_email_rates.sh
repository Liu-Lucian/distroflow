#!/bin/bash
# 测试和对比不同产品文档的邮箱发现率
# Test and compare email discovery rates for different product documents

echo "📊 邮箱发现率对比测试 - Email Discovery Rate Comparison Test"
echo "=================================================================="
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
    echo "❌ 未找到auth.json，请先运行: python create_auth_manual.py"
    exit 1
fi

echo ""
echo "此脚本将进行小规模测试（3个账号，每个50粉丝）来对比邮箱率"
echo "This script will run small tests (3 accounts, 50 followers each) to compare email rates"
echo ""

# 测试配置
FOLLOWERS=50
SEEDS=3
TOTAL_LEADS=$((FOLLOWERS * SEEDS))

echo "⚙️  测试配置:"
echo "   - 每个账号: $FOLLOWERS 粉丝"
echo "   - 种子账号数: $SEEDS 个"
echo "   - 总leads: $TOTAL_LEADS"
echo "   - 预计时间: 15-20分钟/测试"
echo ""

# 创建测试结果目录
mkdir -p test_results
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=================================================================="
echo "测试 1: 默认产品文档 (example_product.md)"
echo "=================================================================="
echo "预期邮箱率: 5-15% (通用产品，未优化)"
echo ""
read -p "运行测试1? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 运行测试1..."
    python src/auto_lead_generator.py example_product.md $FOLLOWERS $SEEDS

    # 查找最新的CSV文件
    LATEST_CSV=$(ls -t auto_leads/leads_*.csv 2>/dev/null | head -1)

    if [ -n "$LATEST_CSV" ]; then
        # 统计邮箱数
        TOTAL_LINES=$(wc -l < "$LATEST_CSV")
        TOTAL_LINES=$((TOTAL_LINES - 1))  # 减去标题行

        # 统计有邮箱的行（all_emails列不为空）
        EMAIL_COUNT=$(awk -F',' 'NR>1 && $9!="" {count++} END {print count+0}' "$LATEST_CSV")

        if [ "$TOTAL_LINES" -gt 0 ]; then
            EMAIL_RATE=$(echo "scale=1; $EMAIL_COUNT * 100 / $TOTAL_LINES" | bc)
        else
            EMAIL_RATE=0
        fi

        echo ""
        echo "📊 测试1结果:"
        echo "   - 总leads: $TOTAL_LINES"
        echo "   - 有邮箱: $EMAIL_COUNT"
        echo "   - 邮箱率: ${EMAIL_RATE}%"
        echo ""

        # 保存结果
        echo "test1_default,$TOTAL_LINES,$EMAIL_COUNT,${EMAIL_RATE}%" >> "test_results/comparison_${TIMESTAMP}.csv"

        # 备份CSV
        cp "$LATEST_CSV" "test_results/test1_default_${TIMESTAMP}.csv"
    fi

    echo "等待60秒后进行下一个测试..."
    sleep 60
fi

echo ""
echo "=================================================================="
echo "测试 2: 优化后的SaaS产品文档 (saas_product_optimized.md)"
echo "=================================================================="
echo "预期邮箱率: 20-30% (B2B用户，优化的种子账号)"
echo ""
read -p "运行测试2? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 运行测试2..."
    python src/auto_lead_generator.py saas_product_optimized.md $FOLLOWERS $SEEDS

    # 查找最新的CSV文件
    LATEST_CSV=$(ls -t auto_leads/leads_*.csv 2>/dev/null | head -1)

    if [ -n "$LATEST_CSV" ]; then
        # 统计邮箱数
        TOTAL_LINES=$(wc -l < "$LATEST_CSV")
        TOTAL_LINES=$((TOTAL_LINES - 1))  # 减去标题行

        # 统计有邮箱的行
        EMAIL_COUNT=$(awk -F',' 'NR>1 && $9!="" {count++} END {print count+0}' "$LATEST_CSV")

        if [ "$TOTAL_LINES" -gt 0 ]; then
            EMAIL_RATE=$(echo "scale=1; $EMAIL_COUNT * 100 / $TOTAL_LINES" | bc)
        else
            EMAIL_RATE=0
        fi

        echo ""
        echo "📊 测试2结果:"
        echo "   - 总leads: $TOTAL_LINES"
        echo "   - 有邮箱: $EMAIL_COUNT"
        echo "   - 邮箱率: ${EMAIL_RATE}%"
        echo ""

        # 保存结果
        echo "test2_optimized,$TOTAL_LINES,$EMAIL_COUNT,${EMAIL_RATE}%" >> "test_results/comparison_${TIMESTAMP}.csv"

        # 备份CSV
        cp "$LATEST_CSV" "test_results/test2_optimized_${TIMESTAMP}.csv"
    fi
fi

echo ""
echo "=================================================================="
echo "📊 测试完成！对比结果"
echo "=================================================================="
echo ""

if [ -f "test_results/comparison_${TIMESTAMP}.csv" ]; then
    echo "测试名称          总Leads    有邮箱    邮箱率"
    echo "--------------------------------------------------------"
    cat "test_results/comparison_${TIMESTAMP}.csv" | while IFS=',' read -r name total emails rate; do
        printf "%-15s   %-8s   %-6s    %s\n" "$name" "$total" "$emails" "$rate"
    done

    echo ""
    echo "详细结果已保存到: test_results/"
    echo ""
    echo "查看详细数据:"
    echo "  open test_results/"
else
    echo "未找到测试结果"
fi

echo ""
echo "=================================================================="
echo "💡 分析和建议"
echo "=================================================================="
echo ""
echo "如果测试2的邮箱率明显高于测试1（预期 15-25个百分点），说明："
echo ""
echo "✅ 优化策略有效！"
echo "   1. 种子账号的选择很重要"
echo "   2. 目标用户画像要精准"
echo "   3. B2B社区的邮箱率远高于媒体账号"
echo ""
echo "下一步："
echo "   1. 使用 saas_product_optimized.md 进行大规模爬取"
echo "   2. 或者根据你的实际产品修改优化文档"
echo "   3. 扩大规模: python src/auto_lead_generator.py saas_product_optimized.md 200 15"
echo ""
echo "如果邮箱率仍然很低（<10%），可能原因："
echo "   ❌ Twitter账号被限制"
echo "   ❌ 网站爬取失败（检查日志）"
echo "   ❌ 种子账号选择仍不理想"
echo ""
echo "=================================================================="
