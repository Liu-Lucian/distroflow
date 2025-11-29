# DistroFlow Quick Start Guide

Get up and running in 5 minutes.

---

## Prerequisites

- Python 3.8 or higher
- Git
- 10 minutes of your time

---

## Step 1: Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/distroflow.git
cd distroflow

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install DistroFlow
pip install -e .

# Install Playwright browsers
playwright install chromium
```

**Verify installation**:
```bash
./distroflow-cli.sh --version
# Should output: python -m distroflow.cli, version 0.1.0
```

✅ **Installation complete!**

---

## Step 2: Set Up Authentication (2 minutes)

### Option A: Quick Setup (Recommended)

```bash
# Create auth directory
mkdir -p ~/.distroflow

# For Reddit (easiest to start with)
cat > ~/.distroflow/reddit_auth.json << 'EOF'
{
  "cookies": [
    {"name": "reddit_session", "value": "YOUR_SESSION_COOKIE"}
  ]
}
EOF
```

**How to get Reddit session cookie**:
1. Open Reddit in your browser
2. Login to your account
3. Open DevTools (F12 or Cmd+Option+I)
4. Go to Application → Cookies → https://www.reddit.com
5. Find `reddit_session` cookie
6. Copy its value
7. Paste into the JSON file above

### Option B: Automated Setup (Coming Soon)

```bash
./distroflow-cli.sh setup reddit
# Will guide you through browser login
```

---

## Step 3: Your First Post (1 minute)

Let's post to Reddit's test subreddit:

```bash
./distroflow-cli.sh launch \
  --platforms reddit \
  --title "Testing DistroFlow" \
  --content "This is my first automated post using DistroFlow!"
```

**What happens**:
1. DistroFlow opens a browser
2. Loads your Reddit cookies
3. Navigates to r/test
4. Creates a new post
5. Fills in title and content
6. Clicks submit

**You should see**:
```
🚀 Launching to: reddit
📝 Content: This is my first automated post...
✅ Posted to reddit successfully
```

✅ **Your first automated post!**

---

## Step 4: Multi-Platform Launch (Optional)

Once you've set up multiple platforms:

```bash
./distroflow-cli.sh launch \
  --platforms "twitter,reddit,hackernews" \
  --title "Show HN: My Cool Project" \
  --content "I built this amazing thing..." \
  --url "https://myproject.com"
```

**This posts to all 3 platforms simultaneously!**

---

## Step 5: Schedule Recurring Posts (Optional)

```bash
# Daily build-in-public updates
./distroflow-cli.sh schedule \
  --workflow build-in-public \
  --platforms "twitter,linkedin" \
  --frequency daily \
  --time "09:00" \
  --content "Day {day}: Working on DistroFlow..."

# Run the scheduler
./distroflow-cli.sh daemon
```

---

## Common Issues & Solutions

### Issue: "No module named 'openai'"

**Solution**: Install dependencies
```bash
pip install openai playwright click fastapi
```

### Issue: "Authentication failed for reddit"

**Solution**: Check your cookies
1. Cookies expire - get fresh ones
2. Verify JSON format is correct
3. Check cookie name matches platform

### Issue: "Browser not found"

**Solution**: Install Playwright browsers
```bash
playwright install chromium
```

### Issue: "Permission denied: ./distroflow-cli.sh"

**Solution**: Make script executable
```bash
chmod +x distroflow-cli.sh
```

---

## Next Steps

### Learn More
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - How DistroFlow works
- **[PLATFORMS.md](PLATFORMS.md)** - Platform-specific guides
- **[README.md](../README.md)** - Full documentation

### Add More Platforms
```bash
# Set up Twitter
cat > ~/.distroflow/twitter_auth.json << 'EOF'
{
  "cookies": [
    {"name": "auth_token", "value": "YOUR_TWITTER_TOKEN"}
  ]
}
EOF

# Set up HackerNews
cat > ~/.distroflow/hackernews_auth.json << 'EOF'
{
  "cookies": [
    {"name": "user", "value": "YOUR_USERNAME"}
  ]
}
EOF
```

### Try Advanced Features

**AI-powered Instagram lead generation**:
```bash
./distroflow-cli.sh engage \
  --platform instagram \
  --keywords "your niche keywords" \
  --max-users 50
```

**Schedule daily automation**:
```bash
./distroflow-cli.sh schedule \
  --workflow build-in-public \
  --platforms twitter,reddit \
  --frequency daily
```

---

## Tips for Success

### 1. Start Small
- Begin with ONE platform (Reddit is easiest)
- Test with r/test subreddit
- Verify everything works

### 2. Human-Like Behavior
- Don't spam - DistroFlow has built-in delays
- Respect platform rate limits
- Provide genuine value in your posts

### 3. Monitor Your Posts
- Check that posts appear correctly
- Watch for platform warnings
- Adjust content if needed

### 4. Use Scheduling Wisely
- Post at optimal times for your audience
- Don't post the same content everywhere
- Vary your messaging per platform

---

## Troubleshooting

### Enable Debug Logging

```bash
# See detailed logs
export DEBUG=1
./distroflow-cli.sh launch --platforms reddit ...
```

### Test Individual Components

```python
# Test browser manager
python3 -c "
from distroflow.core.browser_manager import BrowserManager
import asyncio

async def test():
    async with BrowserManager() as browser:
        await browser.page.goto('https://reddit.com')
        print('✅ Browser working')

asyncio.run(test())
"
```

### Verify Authentication

```bash
# Check auth file exists
ls -la ~/.distroflow/
cat ~/.distroflow/reddit_auth.json
```

---

## Getting Help

### Community Support
- **GitHub Discussions**: [Ask questions](https://github.com/yourusername/distroflow/discussions)
- **GitHub Issues**: [Report bugs](https://github.com/yourusername/distroflow/issues)

### Documentation
- **README**: Comprehensive overview
- **ARCHITECTURE**: Technical deep dive
- **PLATFORMS**: Platform-specific guides

### Example Code
- Check `examples/` directory
- Look at `distroflow/platforms/` for reference implementations

---

## Summary

You've learned how to:
- ✅ Install DistroFlow
- ✅ Set up authentication
- ✅ Post to platforms
- ✅ Schedule automation
- ✅ Troubleshoot issues

**Next**: Try posting to multiple platforms and explore advanced features!

---

**Time spent**: ~5 minutes
**Result**: Working cross-platform automation
**ROI**: Infinite (free and open source!)

**Happy automating! 🚀**
