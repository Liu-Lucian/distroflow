# MarketingMind AI - Usage Guide

Complete guide for using MarketingMind AI to automate your lead generation and social media growth.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Use Cases](#use-cases)
4. [Commands](#commands)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### 1. Set up Python environment

```bash
# Navigate to project directory
cd "/Users/l.u.c/my-app/MarketingMind AI"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

The `.env` file has been created with your keys. You still need to add:

- **Twitter API Key** (API Key and API Secret)
- **Twitter Bearer Token**

To get these:
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use existing one
3. Get your API Key, API Secret, and Bearer Token
4. Add them to `.env`

---

## Configuration

Your `.env` file should look like this:

```env
# Already configured
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_API_KEY_HERE
TWITTER_ACCESS_TOKEN=1711446271398207489-kQSgu6BvxvxnhqMqPKPlbSwcMh0Ynu
TWITTER_ACCESS_TOKEN_SECRET=DT0keTurEezuOXEKQwvcm0r8odzREFdpiHKK4CiudqD0H

# Need to add these
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

---

## Use Cases

### Use Case 1: Sales Lead Generation

**Goal:** Find 500 potential customers for your product

```bash
# Create a product description file
cat > product.txt << EOF
We provide AI-powered customer service automation for e-commerce businesses.
Our platform helps online stores reduce support costs by 60% while improving
customer satisfaction through intelligent chatbots and automated workflows.
Perfect for mid-sized e-commerce stores with 50-500 support tickets per day.
EOF

# Run lead generation
python main.py find-leads \
  --product product.txt \
  --count 500 \
  --find-emails \
  --format excel
```

**What happens:**
1. AI extracts relevant keywords from your product description
2. Searches Twitter for influencers in your niche
3. Scrapes 500 followers from these influencers
4. Finds email addresses where possible
5. Exports everything to Excel with multiple sheets

**Time:** ~30-60 minutes (vs 2 weeks manually)

**Output:** Excel file in `exports/` with:
- Lead data (name, username, bio, followers)
- Email addresses
- Source influencers
- Campaign summary

---

### Use Case 2: Market Research

**Goal:** Analyze competitor's audience

```bash
# Scrape and analyze competitor's followers
python main.py analyze-competitor \
  --username competitor_handle \
  --count 1000 \
  --format excel
```

**What happens:**
1. Fetches competitor's profile
2. Scrapes their followers
3. Extracts professional information
4. Exports to Excel for analysis

**Use this data to:**
- Understand competitor's customer base
- Identify market segments
- Find partnership opportunities
- Plan marketing campaigns

---

### Use Case 3: Social Media Growth

**Goal:** Grow your Twitter following

```bash
# Target competitor's followers
python main.py grow \
  --target competitor_handle \
  --follow \
  --engage \
  --count 100
```

**What happens:**
1. Finds followers of target account
2. Automatically follows them
3. Likes their recent tweets
4. Builds engagement

**Warning:** Respect Twitter's rate limits and Terms of Service!

---

### Use Case 4: Generate Personalized Messages

**Goal:** Create custom outreach messages

```bash
# Generate a DM
python main.py generate-message \
  --name "Sarah Johnson" \
  --username "sarahj_tech" \
  --bio "Product Manager at SaaS startup. AI enthusiast." \
  --product "AI-powered customer service automation" \
  --type dm \
  --tone professional

# Generate an email
python main.py generate-message \
  --name "John Smith" \
  --username "johnsmith" \
  --bio "E-commerce founder. Scaling to $10M." \
  --product product.txt \
  --type email \
  --tone friendly
```

---

## Commands

### 1. find-leads

Find leads based on product description

```bash
python main.py find-leads \
  --product "your product description or path/to/file.txt" \
  --count 500 \
  [--find-emails] \
  [--generate-messages] \
  [--format excel|csv|json]
```

**Options:**
- `--product`: Product description (text or file path)
- `--count`: Number of leads (default: 500)
- `--find-emails`: Find email addresses
- `--generate-messages`: Generate outreach messages
- `--format`: Export format (excel, csv, json)

---

### 2. analyze-competitor

Analyze competitor's followers

```bash
python main.py analyze-competitor \
  --username competitor_handle \
  --count 500 \
  [--format excel|csv|json]
```

**Options:**
- `--username`: Competitor's Twitter handle
- `--count`: Number of followers to scrape
- `--format`: Export format

---

### 3. grow

Social media growth automation

```bash
python main.py grow \
  --target competitor_handle \
  [--follow] \
  [--engage] \
  --count 100
```

**Options:**
- `--target`: Target account to get followers from
- `--follow`: Auto-follow users
- `--engage`: Auto-like tweets
- `--count`: Number of users to process

---

### 4. generate-message

Generate personalized messages

```bash
python main.py generate-message \
  --name "Lead Name" \
  --username "twitter_handle" \
  --bio "Their bio" \
  --product "Your product or path/to/file.txt" \
  --type connection|dm|email \
  [--tone professional|casual|friendly]
```

**Options:**
- `--name`: Lead's name
- `--username`: Lead's Twitter username
- `--bio`: Lead's bio/description
- `--product`: Product description or file
- `--type`: Message type (connection, dm, email)
- `--tone`: Message tone

---

## Best Practices

### 1. Rate Limiting

Twitter has strict rate limits:
- Max 15 requests per 15 minutes for most endpoints
- Max 50 followers per minute for scraping

**Recommendation:**
- Start with small numbers (100-200 leads)
- Let the script run slowly to avoid limits
- Use the built-in rate limiting (automatic)

### 2. Compliance

**Legal Requirements:**
- Follow GDPR and privacy regulations
- Get consent before sending marketing emails
- Comply with Twitter's Terms of Service
- Respect CAN-SPAM Act for emails

**Best Practices:**
- Don't be spammy
- Personalize your messages
- Provide value in your outreach
- Allow opt-outs

### 3. Email Finding

Email finding works best when:
- Users have their website in bio
- Company domain is clear
- Bio contains email

**Tips:**
- Check LinkedIn profiles manually for high-value leads
- Use Hunter.io API for better results (add key to .env)
- Verify emails before sending (use Clearbit)

### 4. Message Personalization

AI-generated messages are good but:
- Always review before sending
- Add personal touches manually
- Reference specific details
- A/B test different approaches

### 5. Optimize Your Product Description

Good product descriptions lead to better targeting:
- Be specific about your target audience
- Include industry keywords
- Mention specific use cases
- Highlight unique value proposition

**Example:**
```
Bad: "We make software for businesses"

Good: "AI-powered inventory management for e-commerce stores
with 100-1000 SKUs. Reduce stockouts by 40% and optimize
cash flow through predictive analytics."
```

---

## Troubleshooting

### Issue: "Missing required API keys"

**Solution:**
1. Check `.env` file exists
2. Verify all required keys are present
3. Make sure no extra spaces in key values

### Issue: Twitter API errors

**Solutions:**
- Check API keys are correct
- Verify app has proper permissions
- Check rate limits haven't been exceeded
- Wait 15 minutes and try again

### Issue: No influencers found

**Solutions:**
- Broaden your product description
- Include more keywords
- Try different search terms
- Lower minimum follower count

### Issue: Few emails found

**Solutions:**
- Add Hunter.io API key
- Add Clearbit API key
- Focus on leads with websites in bio
- Manually check LinkedIn profiles

### Issue: Slow performance

**This is normal!**
- Twitter rate limits slow things down
- Finding 500 leads takes 30-60 minutes
- Don't interrupt the process
- Let it run in background

---

## Output Files

All exports go to `exports/` directory:

### Excel Format (Recommended)
- **Summary Sheet**: Campaign overview and statistics
- **Leads Sheet**: All lead data
- **Influencers Sheet**: Source influencers

### CSV Format
- Single file with all lead data
- Easy to import into CRM

### JSON Format
- Structured data for developers
- Can be imported into custom tools

---

## Next Steps

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Add Twitter API keys** to `.env`
3. **Test with small campaign:** 50-100 leads first
4. **Review results** and adjust strategy
5. **Scale up** to full campaigns

## Support

For issues or questions:
1. Check this guide first
2. Review error messages
3. Check Twitter API status
4. Verify rate limits

---

## License & Disclaimer

This tool is for legitimate marketing purposes only.

**You are responsible for:**
- Complying with all laws and regulations
- Following platform Terms of Service
- Respecting user privacy
- Not sending spam

Use responsibly and ethically.
