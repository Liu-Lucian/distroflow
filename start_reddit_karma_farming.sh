#!/bin/bash

# Reddit Karma Farming - Quick Start Script
# 自动养号，7天解锁r/startups发帖

echo "================================================================================"
echo "🌱 Reddit Karma Farming System - let's farm some karma lol"
echo "================================================================================"
echo ""

# Set working directory
cd "/Users/l.u.c/my-app/MarketingMind AI"

# Check if authentication exists
if [ ! -f "reddit_auth.json" ]; then
    echo "⚠️  yo no Reddit auth found"
    echo ""
    echo "First-time setup (ez don't worry):"
    echo "1. Browser gonna open Reddit login"
    echo "2. Just login with your Reddit account"
    echo "3. Hit Enter when you're done"
    echo "4. Cookies saved automatically"
    echo ""
    read -p "Press Enter to start setup..."

    python3 reddit_login_and_save_auth.py

    if [ ! -f "reddit_auth.json" ]; then
        echo ""
        echo "❌ Setup failed or cancelled rip"
        echo "Run this again when you're ready"
        exit 1
    fi

    echo ""
    echo "✅ Auth setup complete gg!"
    echo ""
fi

# Show current 7-day plan progress
echo "📊 Where we at rn:"
echo ""
python3 reddit_7day_plan.py
echo ""

# Ask if user wants to start karma farming
read -p "Wanna start farming now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "================================================================================"
    echo "🚀 Let's gooo - starting karma farming"
    echo "================================================================================"
    echo ""
    echo "What's gonna happen:"
    echo "  • Browse hot posts in popular subreddits"
    echo "  • AI generates genuine comments (not spam fr)"
    echo "  • Auto-post comments for you"
    echo "  • 3 sessions per day (9 comments total ngl)"
    echo "  • Random wait times (so we look human lol)"
    echo ""
    echo "Target subreddits we hitting:"
    echo "  • r/AskReddit (ez karma farm)"
    echo "  • r/technology (tech talk)"
    echo "  • r/programming (dev squad)"
    echo "  • r/startups (our main target tbh)"
    echo "  • r/Entrepreneur (startup vibes)"
    echo ""
    echo "Mission: 50+ karma in 7 days → unlock r/startups posting rights"
    echo ""
    echo "Press Ctrl+C to stop anytime btw"
    echo "================================================================================"
    echo ""
    
    # Set OpenAI API key and run
    export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'
    python3 reddit_karma_farmer.py

    echo ""
    echo "================================================================================"
    echo "✅ Session complete gg wp!"
    echo "================================================================================"
    echo ""
    echo "What's next:"
    echo "1. Run this again tomorrow same time"
    echo "2. Keep going for 7 days total"
    echo "3. Check progress anytime: python3 reddit_7day_plan.py"
    echo "4. Once unlocked, switch to: python3 auto_reddit_scheduler.py"
    echo ""
else
    echo ""
    echo "✅ Setup done. Run this when you're ready to farm lol"
    echo ""
    echo "Manual start command:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  python3 reddit_karma_farmer.py"
    echo ""
fi
