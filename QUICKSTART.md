# MarketingMind AI - Quick Start

Get started in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"

# Run the setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Configure Twitter API (3 minutes)

You need to add these to your `.env` file:

```env
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_BEARER_TOKEN=your_token_here
```

**Don't have these yet?** Follow [TWITTER_API_SETUP.md](TWITTER_API_SETUP.md)

Your Access Token is already configured:
```
TWITTER_ACCESS_TOKEN=1711446271398207489-kQSgu6BvxvxnhqMqPKPlbSwcMh0Ynu
TWITTER_ACCESS_TOKEN_SECRET=DT0keTurEezuOXEKQwvcm0r8odzREFdpiHKK4CiudqD0H
```

## Step 3: Test Everything

```bash
# Activate virtual environment
source venv/bin/activate

# Run component tests
python examples/test_components.py
```

If all tests pass, you're ready!

## Step 4: Run Your First Campaign

### Example 1: Find 50 leads for your product

```bash
python main.py find-leads \
  --product "AI-powered CRM for real estate agents" \
  --count 50 \
  --format excel
```

### Example 2: Analyze competitor's followers

```bash
python main.py analyze-competitor \
  --username competitor_handle \
  --count 100 \
  --format excel
```

### Example 3: Generate a personalized message

```bash
python main.py generate-message \
  --name "Sarah Johnson" \
  --username "sarahj" \
  --bio "Marketing Director at SaaS company" \
  --product "AI marketing automation" \
  --type dm
```

## What Happens Next?

1. The tool will analyze your product description
2. Extract relevant keywords using AI
3. Search Twitter for influencers in your niche
4. Scrape their followers (your potential customers)
5. Find email addresses where possible
6. Export everything to Excel

**Output location:** `exports/` directory

## Project Structure

```
MarketingMind AI/
├── main.py              # Main CLI interface
├── setup.sh             # Setup script
├── requirements.txt     # Python dependencies
├── .env                 # Your API keys (already created)
├── src/
│   ├── keyword_extractor.py    # AI keyword extraction
│   ├── twitter_client.py       # Twitter API integration
│   ├── email_finder.py         # Email discovery
│   ├── outreach_engine.py      # Message generation
│   ├── lead_scraper.py         # Main orchestration
│   ├── data_manager.py         # Export functionality
│   └── config.py               # Configuration
├── examples/
│   ├── test_components.py      # Test script
│   └── example_campaign.sh     # Example campaign
├── exports/             # Output files go here
└── logs/                # Log files

```

## Commands Cheat Sheet

```bash
# Find leads
python main.py find-leads --product "description" --count 500 --find-emails

# Analyze competitor
python main.py analyze-competitor --username handle --count 500

# Grow social media
python main.py grow --target handle --follow --engage --count 100

# Generate message
python main.py generate-message --name "Name" --username "handle" \
  --product "description" --type dm

# Get help
python main.py --help
python main.py find-leads --help
```

## Common Issues

### "Missing required API keys"
→ Add Twitter keys to `.env` file

### "403 Forbidden" from Twitter
→ Set app permissions to "Read and Write" in Twitter Developer Portal

### "No influencers found"
→ Try broader keywords in your product description

### Script is slow
→ This is normal! Twitter rate limits require waiting. Finding 500 leads takes 30-60 minutes.

## Next Steps

1. Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed instructions
2. Read [TWITTER_API_SETUP.md](TWITTER_API_SETUP.md) for API setup
3. Check the `examples/` directory for more examples

## Use Cases

**Scenario 1: Sales Team** - Find 500 potential customers
- Time: ~1 hour (vs 2 weeks manually)
- Cost: Free (with Free Twitter API tier)

**Scenario 2: Market Research** - Analyze competitor's 1000 followers
- Time: ~30 minutes
- Output: Detailed Excel with all follower data

**Scenario 3: Social Growth** - Auto-engage with 100 users
- Time: ~10 minutes
- Result: 100 follows + engagements

## Support

Need help?
1. Check error messages carefully
2. Read the documentation
3. Test with small numbers first (10-50 leads)
4. Verify API keys are correct

## Legal & Ethical Use

This tool is for legitimate business purposes only:
- ✓ Finding potential customers
- ✓ Market research
- ✓ Competitive analysis
- ✗ Spamming
- ✗ Harassment
- ✗ Data selling

Always comply with:
- Twitter Terms of Service
- GDPR and privacy laws
- CAN-SPAM Act
- Local regulations

---

Ready to start? Run:

```bash
./setup.sh
python examples/test_components.py
python main.py find-leads --product "Your product" --count 50
```

Good luck! 🚀
