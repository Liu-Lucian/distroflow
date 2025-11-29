# Testing Human-Like Behavior

Quick test to see the human-like delays in action:

## Quick Test

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate

# Test the rate limiter directly
python src/rate_limiter.py
```

This will simulate 20 API calls with human-like timing. You'll see:
- Variable delays (different each time)
- Occasional longer pauses
- Break messages
- Natural timing patterns

## What You'll See

```
Testing human-like rate limiting...

Request 1/20
✓ Request 1 sent at 14:23:05

Request 2/20
Human-like delay: 5.2s
✓ Request 2 sent at 14:23:11

Request 3/20
Human-like delay: 12.3s
✓ Request 3 sent at 14:23:23

Request 4/20
☕ Taking a short break (3 min)
⏳ Waiting 2.8 more minutes...
⏳ Waiting 2.3 more minutes...
⏳ Waiting 1.8 more minutes...
✓ Request 4 sent at 14:26:45
...
```

## In Real Campaigns

When you run a campaign, you'll see messages like:

```bash
python main.py find-leads --product "Your product" --count 50
```

Output:
```
INFO: Step 2: Finding influencers on Twitter...
INFO: Human-like delay: 4.7s
INFO: Found 3 influencers for query: AI automation
INFO: Simulating reading behavior...
INFO: Human-like delay: 8.2s
INFO: Found 2 influencers for query: SaaS marketing
☕ Taking a short break (2-5 min) to appear more human...
⏳ Waiting 3.2 more minutes to avoid rate limits...
INFO: Step 3: Scraping followers from influencers...
INFO: Human-like delay: 6.1s
...
```

This is **completely normal and expected!**

## Benefits

- ✅ No rate limit blocks
- ✅ Looks like real human activity
- ✅ Account stays safe
- ✅ Sustainable long-term use

## Customization

If you want to adjust the delays (not recommended), edit these values in your command:

**Faster (riskier):**
- min_delay: 2.0
- max_delay: 5.0

**Normal (recommended - default):**
- min_delay: 3.0
- max_delay: 8.0

**Stealth (safest):**
- min_delay: 5.0
- max_delay: 15.0

See `HUMAN_BEHAVIOR.md` for full documentation!
