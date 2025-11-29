# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MarketingMind AI** is a multi-platform automated marketing system that scrapes social media platforms, uses AI to identify potential customers, and automatically sends personalized direct messages. The system supports Instagram, TikTok, Facebook, and LinkedIn.

**Core Value Proposition**: Transform any social media post/comment section into qualified leads through AI-powered analysis and automated outreach.

## System Architecture

### Two Parallel Systems in This Repository

#### 1. Social Media DM Marketing System (PRIMARY - Currently Active)
**Location**: Root directory + `src/` (platform-specific scrapers and DM senders)

**Supported Platforms**:
- **Instagram**: Post comments → AI analysis → DM
- **TikTok**: Video search → Comments → AI analysis → DM (includes AI CAPTCHA solver)
- **Facebook**: Group posts → Comments → AI analysis → DM
- **LinkedIn**: Manual user list → DM (search blocked by anti-bot)

**Key Innovation**: Uses Reddit/Twitter-style simple architecture - ONE core function per scraper (e.g., `get_post_comments(url)`), no complex multi-mode systems.

#### 2. Twitter Lead Generation System (Legacy/Secondary)
**Location**: Same `src/` directory (legacy modules like `ultimate_email_finder.py`, `twitter_scraper_playwright.py`)

**Purpose**: Scrape Twitter followers → Extract emails → Cold email outreach

**Note**: This is the OLDER system. Most recent work focuses on the social media DM system.

### One-Click Marketing Command

**Global Command**: `marketing-campaign` (symlinked to `~/.local/bin/`)

**What it does**: Interactive menu to select platform (Instagram/TikTok/Facebook) → Input URL/keywords → Automatic scraping, AI analysis, and DM sending

**Location**: `/Users/l.u.c/my-app/MarketingMind AI/marketing-campaign` (bash script)

## Core Architecture Patterns

### Simple Platform Pattern (Reddit-Style)

**Critical Design Principle**: After user feedback "什么鬼？你参照twitter的模式或者reddit的模式搞，不要搞这些乱七八糟的" (Don't make complex messy systems), the architecture was simplified:

```python
# Facebook Scraper (Example of Simple Pattern)
class FacebookScraper(PlatformScraperBase):
    def get_post_comments(self, post_url: str, max_comments: int = 50) -> List[Dict]:
        """ONE core function - scrape comments from post"""
        # That's it. No search, no multi-mode complexity
        pass
```

**Pattern**:
1. Scraper: ONE function (e.g., `get_post_comments()`, `search_videos()`)
2. DM Sender: ONE function (`send_dm(user, message)`)
3. Campaign Script: Chain them together (scrape → AI analyze → send DM)

**Anti-Pattern** (Don't do this):
- ❌ Complex multi-mode scrapers
- ❌ Search + scrape + DM all in one class
- ❌ Multiple inheritance hierarchies

### Cost Optimization Strategy

**AI Usage Philosophy**: Minimize OpenAI API calls while maximizing quality

```python
# Cost breakdown per campaign:
# - Scraping: $0 (Pure Playwright)
# - AI Analysis: ~$0.001 per 50 comments (GPT-4o-mini batch)
# - DM Sending: $0 (Pure DOM automation)
# Total: ~$0.002 per 100 users
```

**Implementation**:
1. **Pure Playwright scraping** - No AI for data extraction
2. **Batch AI analysis** - Analyze 50 comments in one API call
3. **MD5 caching** - Never re-analyze same post (see `run_instagram_campaign_optimized.py:64-108`)
4. **Template-based messages** - No AI for message generation

### Authentication Pattern

**Cookie-based persistent authentication** for all platforms:

```json
// platforms_auth.json
{
  "instagram": {"cookies": {"sessionid": "..."}},
  "tiktok": {"sessionid": "..."},
  "facebook": {"cookies": {...}}
}

// linkedin_auth.json (separate file)
{
  "cookies": [...]
}
```

**Login scripts**: Each platform has `{platform}_login_and_save_auth.py` that:
1. Opens browser
2. User manually logs in
3. Automatically extracts and saves cookies
4. Campaign scripts reuse saved cookies

## Key Commands

### Running Campaigns

```bash
# One-click interactive launcher (RECOMMENDED)
marketing-campaign

# Individual platform campaigns
python3 run_instagram_campaign_optimized.py
python3 run_tiktok_campaign_optimized.py
python3 run_facebook_campaign.py

# LinkedIn (manual user list approach)
python3 linkedin_dm_from_list.py
```

### Authentication Setup

```bash
# Instagram/TikTok: Manual cookie extraction
nano platforms_auth.json  # Add sessionid manually

# TikTok sessionid helper
python3 save_tiktok_sessionid.py

# Facebook: Automated cookie saver
python3 facebook_login_and_save_auth.py

# LinkedIn: Automated cookie saver
python3 linkedin_login_and_save_auth.py
```

### Viewing Results

```bash
# View qualified users (JSON)
cat instagram_qualified_users.json | python3 -m json.tool
cat tiktok_qualified_comments.json | python3 -m json.tool
cat facebook_qualified_users.json | python3 -m json.tool

# Progress tracking
python3 -c "import json; u=json.load(open('instagram_qualified_users.json')); \
print(f'Total: {len(u)}, Sent: {len([x for x in u if x.get(\"sent_dm\")])}')"
```

## File Structure

### Campaign Scripts (Root)
- `run_instagram_campaign_optimized.py` - Instagram full pipeline
- `run_tiktok_campaign_optimized.py` - TikTok with CAPTCHA handling
- `run_facebook_campaign.py` - Facebook (simple Reddit-style)
- `linkedin_dm_from_list.py` - LinkedIn DM sender (no search)
- `marketing-campaign` - One-click launcher (bash)

### Platform Scrapers (src/)
- `src/instagram_scraper.py` - Scrapes post comments
- `src/tiktok_scraper.py` - Searches videos, scrapes comments
- `src/facebook_scraper.py` - Scrapes group post comments
- `src/linkedin_scraper.py` - (Search disabled, not used)
- `src/platform_scraper_base.py` - Abstract base class

### DM Senders (src/)
- `src/instagram_dm_sender_optimized.py` - Instagram DM automation
- `src/tiktok_dm_sender_optimized.py` - TikTok DM (uses saved profile_url)
- `src/facebook_dm_sender.py` - Facebook DM automation
- `src/linkedin_dm_sender.py` - LinkedIn DM with connection fallback
- `src/dm_sender_base.py` - Abstract base class

### AI & Analysis (src/)
- `src/smart_user_finder.py` - GPT-4o-mini batch comment analysis
- `solve_tiktok_puzzle.py` - GPT-4o Vision CAPTCHA solver for TikTok

### Authentication
- `platforms_auth.json` - Instagram, TikTok, Facebook cookies
- `linkedin_auth.json` - LinkedIn cookies
- `auth.json` - Twitter cookies (legacy system)

### Data Storage
- `instagram_qualified_users.json` - Analyzed Instagram users
- `tiktok_qualified_comments.json` - Analyzed TikTok commenters
- `facebook_qualified_users.json` - Analyzed Facebook users
- `linkedin_target_users.json` - Manual LinkedIn user list
- `cache/instagram_analyzed_comments.json` - MD5 cache to avoid re-analysis

## Critical Technical Details

### TikTok CAPTCHA Handling

**Problem**: TikTok shows slider CAPTCHA that blocks comment scraping

**Solution**: AI Vision-based solver using GPT-4o

```python
# solve_tiktok_puzzle.py
# 1. Screenshot CAPTCHA
# 2. Send to GPT-4o with vision
# 3. Get slider position from AI
# 4. Simulate human-like drag
```

**User Feedback**: "一定要攻克TikTok...提取不到是因为有验证（滑块验证）" - This was explicitly requested and successfully implemented.

### TikTok Username Handling

**Problem**: Usernames with spaces (e.g., "sebastian Ogene") break URL construction

**Solution**: Save `profile_url` during scraping, don't construct from username

```python
# run_tiktok_campaign_optimized.py
for elem in comment_elements:
    username = elem.query_selector('a').inner_text()
    profile_href = elem.query_selector('a').get_attribute('href')  # Save full URL!

    comments.append({
        'username': username,
        'profile_url': profile_href  # Use this for DM sending
    })
```

**User Feedback**: "你不如这样：不要手机用户名字，直接点进头像私聊" (Don't rely on username, click avatar directly)

### LinkedIn Search Limitation

**Problem**: LinkedIn blocks automated search with "This one's our fault" error page

**Workaround**: Skip search, use manual user list

```bash
# 1. Manually search on LinkedIn web
# 2. Copy profile URLs
# 3. Add to linkedin_target_users.json
# 4. Run DM sender script
python3 linkedin_dm_from_list.py
```

**Status**: Search is permanently disabled. LinkedIn DM sending works perfectly.

**User Decision**: "不搞linkedin了，他们发私信还要钱" (Don't do LinkedIn, they charge for messages) - User later abandoned LinkedIn for Facebook.

### Facebook Simple Architecture

**Critical User Feedback**: "什么鬼？你参照twitter的模式或者reddit的模式搞，不要搞这些乱七八糟的"

**Before** (Rejected):
```python
class FacebookScraper:
    def search_users(...)  # Complex
    def search_groups(...)  # Complex
    def get_posts(...)      # Complex
    def get_comments(...)   # Complex
```

**After** (Accepted):
```python
class FacebookScraper:
    def get_post_comments(self, post_url: str) -> List[Dict]:
        """ONE function. That's it."""
        pass
```

**Lesson**: Keep it simple. One core function per scraper. No multi-mode complexity.

## Configuration Patterns

### Campaign Script Configuration

Every `run_*_campaign.py` has these configurable constants at the top:

```python
# Product description for AI analysis
PRODUCT_DESCRIPTION = """..."""

# AI filtering
AI_MIN_SCORE = 0.6  # Lower to 0.5 for more results

# DM batching
DM_BATCH_SIZE = 3  # Users per run
DM_DELAY = (120, 300)  # Random delay in seconds

# Message template
MESSAGE_TEMPLATE = """Hi {username}!..."""
```

**User tuning**: Lower AI_MIN_SCORE if getting 0 qualified users. Increase DM_DELAY if platform detects automation.

### OpenAI API Key

Set via environment variable (required for AI analysis):

```bash
export OPENAI_API_KEY='sk-proj-...'
```

Or hardcoded in campaign scripts (line ~15-20 in each `run_*_campaign.py`).

## Common User Requests & Solutions

### "Email rate is too low, how to optimize?"

**Answer**: This is for the Twitter lead generation system (legacy), not the social media DM system. The DM system doesn't use emails - it sends direct messages through platform automation.

If user is asking about the Twitter system, refer to `ULTIMATE_IMPROVEMENTS.md` for the 7-layer website extraction strategy.

### "Platform login expired / cookies invalid"

**Solution**:
```bash
# Instagram/TikTok: Manual update
nano platforms_auth.json  # Update sessionid

# TikTok specific helper
python3 save_tiktok_sessionid.py

# Facebook
python3 facebook_login_and_save_auth.py

# LinkedIn
python3 linkedin_login_and_save_auth.py
```

### "AI returned 0 qualified users"

**Possible causes**:
1. `AI_MIN_SCORE` too high (try 0.5 instead of 0.6)
2. `PRODUCT_DESCRIPTION` not clear
3. Wrong target post/keywords

**Solution**: Edit campaign script configuration at top of file.

### "DM sending failed"

**Debugging**:
1. Check browser automation log (shows which selectors failed)
2. Platform UI may have changed (update selectors)
3. Cookies may be expired (re-run login script)
4. Platform detected automation (increase delays, reduce batch size)

### "How to add a new platform?"

**Steps**:
1. Create `src/{platform}_scraper.py` extending `PlatformScraperBase`
   - Implement ONE core function (e.g., `get_post_comments()`)
2. Create `src/{platform}_dm_sender.py` extending `DMSenderBase`
   - Implement `send_dm(user, message)`
3. Create `run_{platform}_campaign.py` chaining them
4. Add to `marketing-campaign` bash script
5. Create `{platform}_login_and_save_auth.py` for authentication

**Reference**: Look at Facebook implementation (most recent, follows simple pattern).

## Architecture Decisions & History

### Decision: Simple Reddit-Style Pattern (Oct 2025)

**Context**: User rejected complex multi-mode Facebook implementation

**Decision**: Adopt simple one-function-per-scraper pattern like Reddit

**Impact**: Dramatically improved maintainability. All new platforms follow this pattern.

**Key Quote**: "什么鬼？你参照twitter的模式或者reddit的模式搞，不要搞这些乱七八糟的"

### Decision: Abandon LinkedIn Search (Oct 2025)

**Context**: LinkedIn consistently blocks automated search

**Decision**: Use manual user list + automated DM sending

**Impact**: LinkedIn campaigns still work, just require manual user discovery step

**Later Update**: User abandoned LinkedIn entirely for Facebook (messaging requires payment)

### Decision: TikTok AI CAPTCHA Solver (Oct 2025)

**Context**: TikTok shows slider CAPTCHA blocking comment extraction

**Decision**: Implement GPT-4o Vision-based solver

**Impact**: TikTok campaigns now work reliably. Users explicitly requested this: "一定要攻克TikTok"

### Decision: Save profile_url During Scraping (Oct 2025)

**Context**: TikTok usernames with spaces break URL construction

**Decision**: Save full profile_url from DOM during scraping, use directly for DM

**Impact**: Eliminated username-related bugs across all platforms

**User Quote**: "你不如这样：不要手机用户名字，直接点进头像私聊"

## Important Warnings

### Platform Terms of Service

All platforms prohibit automation. Use responsibly:
- Don't spam users
- Respect rate limits
- Use delays between actions
- Provide genuine value in messages

### API Cost Management

The system is designed to be nearly free (~$0.001 per 50 comments):
- Scraping: $0 (Playwright)
- AI Analysis: ~$0.001 per batch (GPT-4o-mini)
- DM: $0 (Automation)

**Never** use GPT-4 for batch analysis (100x more expensive). Always use GPT-4o-mini.

### Account Safety

- Use dedicated marketing accounts, not personal accounts
- Don't hardcode credentials in code
- Rotate cookies regularly
- Monitor for platform warnings

## Testing & Development

### Test Individual Components

```bash
# Test scraper
python3 -c "from src.instagram_scraper import InstagramScraper; \
s = InstagramScraper(); print(s.get_post_comments('URL', 5))"

# Test DM sender
python3 -c "from src.instagram_dm_sender_optimized import InstagramDMSender; \
sender = InstagramDMSender(); print('✅ OK')"

# Test AI analysis
python3 -c "from src.smart_user_finder import SmartUserFinder; \
finder = SmartUserFinder(); print('✅ OK')"
```

### Development Workflow

1. **Make changes** to scraper/sender
2. **Test standalone** with small data (5-10 items)
3. **Test campaign script** with `DM_BATCH_SIZE = 1`
4. **Scale up** gradually (1 → 3 → 5 users)

### Debugging Browser Automation

When selectors break (platform UI changed):

1. Run with `headless=False` in scraper
2. Add `time.sleep(10)` to inspect page
3. Use browser DevTools to find new selectors
4. Update selectors in code

## Dependencies

### Core
- `playwright>=1.40.0` - Browser automation
- `openai>=1.0.0` - AI analysis (GPT-4o-mini)
- `beautifulsoup4>=4.12.0` - HTML parsing

### Platform-Specific
- All scrapers use Playwright (no API clients)
- All authentication is cookie-based

### Python Version
- Python 3.8+

## Quick Reference for Common Tasks

```bash
# Setup (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='sk-proj-...'

# Run marketing campaign
marketing-campaign  # Interactive menu

# Or run specific platform
python3 run_instagram_campaign_optimized.py

# View results
cat instagram_qualified_users.json | python3 -m json.tool

# Re-authenticate
python3 facebook_login_and_save_auth.py
```

## Documentation Files

### User Guides
- `一键启动说明.md` - One-click marketing guide (Chinese)
- `FACEBOOK_QUICKSTART.md` - Facebook quick start guide
- `README_MARKETING_SYSTEM.md` - Multi-platform system overview
- `LINKEDIN_DM_GUIDE.md` - LinkedIn DM guide

### Legacy Twitter System Docs (Secondary System)
- `ULTIMATE_IMPROVEMENTS.md` - Twitter email finder improvements
- `EMAIL_RATE_ANALYSIS.md` - Email discovery optimization
- `HUNTER_STYLE_GUIDE.md` - Hunter.io-inspired approach

**Note**: Most recent development focuses on social media DM system, not Twitter email system.

## Summary for Future Claude Instances

**Primary System**: Multi-platform social media DM automation (Instagram/TikTok/Facebook/LinkedIn)

**Architecture**: Simple Reddit-style pattern - ONE function per scraper, chain with AI analysis and DM sender

**Key Innovation**: Cost-optimized AI usage (~$0.001 per 50 comments), MD5 caching, batch processing

**Global Command**: `marketing-campaign` - One-click interactive launcher

**Critical Files**:
- `marketing-campaign` - Main entry point
- `run_instagram_campaign_optimized.py` - Best reference implementation
- `src/platform_scraper_base.py` - Base class pattern
- `src/smart_user_finder.py` - AI analysis engine

**Common User Need**: "平台登录失效" (Platform login expired) → Re-run `{platform}_login_and_save_auth.py`

**Design Philosophy**: Simple, cost-effective, battle-tested. User explicitly rejected complex architectures.
