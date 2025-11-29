#!/bin/bash

# Reddit Build in Public Automation - Quick Start Script
# For HireMeAI (https://interviewasssistant.com)

echo "================================================================================"
echo "🚀 Reddit Build in Public Automation System"
echo "================================================================================"
echo ""

# Set working directory
cd "/Users/l.u.c/my-app/MarketingMind AI"

# Check if authentication exists
if [ ! -f "reddit_auth.json" ]; then
    echo "⚠️  No Reddit authentication found"
    echo ""
    echo "First-time setup required:"
    echo "1. Browser will open to Reddit login page"
    echo "2. Login with your Reddit account"
    echo "3. Press Enter when done"
    echo "4. Cookies will be saved automatically"
    echo ""
    read -p "Press Enter to start authentication setup..."
    
    python3 reddit_login_and_save_auth.py
    
    if [ ! -f "reddit_auth.json" ]; then
        echo ""
        echo "❌ Authentication setup failed or cancelled"
        echo "Please run this script again when ready"
        exit 1
    fi
    
    echo ""
    echo "✅ Authentication setup complete!"
    echo ""
fi

# Check account status
echo "📊 Checking account status..."
echo ""
python3 reddit_account_manager.py
echo ""

# Ask if user wants to start automation
read -p "Start Reddit automation now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "================================================================================"
    echo "🚀 Starting Reddit Automation"
    echo "================================================================================"
    echo ""
    echo "The system will now:"
    echo "  • Check account age and posting limits"
    echo "  • Generate Build in Public content (AI)"
    echo "  • Post to Reddit automatically"
    echo "  • Run forever (press Ctrl+C to stop)"
    echo ""
    echo "Target subreddits:"
    echo "  • r/Startups"
    echo "  • r/ArtificialIntelligence"
    echo "  • r/EntrepreneurRideAlong"
    echo "  • r/SaaS"
    echo ""
    echo "================================================================================"
    echo ""
    
    # Set OpenAI API key and run
    export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'
    python3 auto_reddit_scheduler.py
else
    echo ""
    echo "✅ Setup complete. Run this script again when ready to start."
    echo ""
    echo "To start manually:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  python3 auto_reddit_scheduler.py"
    echo ""
fi
