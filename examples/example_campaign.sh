#!/bin/bash

# Example campaign script for MarketingMind AI
# This demonstrates a complete lead generation workflow

echo "Starting example lead generation campaign..."

# Create a sample product description
cat > /tmp/sample_product.txt << 'EOF'
AI-powered marketing automation platform for SaaS startups.
Help B2B companies generate qualified leads through intelligent
social media engagement and personalized outreach.

Perfect for:
- Early-stage SaaS companies (Series A-B)
- Marketing teams of 5-20 people
- B2B products with $50K+ ACV
- Companies looking to scale outbound without hiring

Reduce lead gen costs by 40% while increasing pipeline by 3x.
EOF

echo "Product description created"

# Run lead generation
echo ""
echo "Finding leads..."
python ../main.py find-leads \
    --product /tmp/sample_product.txt \
    --count 100 \
    --find-emails \
    --format excel

echo ""
echo "Campaign completed!"
echo "Check the exports/ directory for results"
