#!/bin/bash
# Quick test for Substack publishing

cd "/Users/l.u.c/my-app/MarketingMind AI"

# Check if venv exists
if [ -d "venv" ]; then
    echo "Using venv..."
    source venv/bin/activate
fi

# Set API key
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'

echo "Running Substack publish test..."
echo ""
echo "When prompted:"
echo "  1. Choose mode: 2 (Publish immediately)"
echo "  2. Confirm warning: yes"
echo "  3. Confirm proceed: yes"
echo ""

python3 test_substack_auto_post.py
