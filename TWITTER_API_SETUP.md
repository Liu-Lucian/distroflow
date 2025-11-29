# Twitter API Setup Guide

Step-by-step instructions to get your Twitter API credentials.

## Prerequisites

- Twitter account (must be verified)
- Phone number associated with account
- Developer account approval (usually instant for most use cases)

---

## Step 1: Apply for Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click "Sign up for a developer account"
3. Choose **"Hobbyist"** → **"Exploring the API"** (or choose what fits your use case)
4. Fill out the application:
   - **How will you use the Twitter API?**
     ```
     I'm building a marketing automation tool to help businesses find potential
     customers on Twitter. The tool will:
     - Search for relevant users based on keywords
     - Analyze follower relationships
     - Generate personalized outreach messages
     - Export data for CRM integration

     This is for legitimate business development, not spam or data selling.
     ```
   - Answer other questions honestly
   - Accept Terms and Conditions

5. Verify your email
6. Wait for approval (usually instant, sometimes up to 24 hours)

---

## Step 2: Create a New App

1. Once approved, go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click **"Projects & Apps"** in left sidebar
3. Click **"+ Create App"** or **"+ Create Project"**
4. Name your app (e.g., "MarketingMind AI")
5. You'll see three keys:
   - **API Key** (also called Consumer Key)
   - **API Secret Key** (also called Consumer Secret)
   - **Bearer Token**

6. **IMPORTANT:** Copy these keys immediately! You won't see them again.

---

## Step 3: Set App Permissions

1. Go to your app settings
2. Click **"Settings"** tab
3. Scroll to **"App permissions"**
4. Click **"Edit"**
5. Select **"Read and Write"** (needed for following and liking)
6. Enable **"Request email address from users"** (optional)
7. Save changes

---

## Step 4: Generate Access Token and Secret

1. In your app, click **"Keys and tokens"** tab
2. Under **"Authentication Tokens"** section
3. Click **"Generate"** next to "Access Token and Secret"
4. You'll get:
   - **Access Token**
   - **Access Token Secret**

5. **IMPORTANT:** Copy these immediately!

---

## Step 5: Add Keys to .env File

Open your `.env` file and add all the keys:

```env
# These you already have from the user
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_API_KEY_HERE
TWITTER_ACCESS_TOKEN=1711446271398207489-kQSgu6BvxvxnhqMqPKPlbSwcMh0Ynu
TWITTER_ACCESS_TOKEN_SECRET=DT0keTurEezuOXEKQwvcm0r8odzREFdpiHKK4CiudqD0H

# Add these from Twitter Developer Portal
TWITTER_API_KEY=your_api_key_from_step_2
TWITTER_API_SECRET=your_api_secret_from_step_2
TWITTER_BEARER_TOKEN=your_bearer_token_from_step_2
```

---

## Step 6: Verify Setup

Test your configuration:

```bash
# Activate virtual environment
source venv/bin/activate

# Test Twitter connection
python -c "from src.twitter_client import TwitterClient; client = TwitterClient(); print('✓ Twitter API connected!')"
```

If no errors, you're ready to go!

---

## API Tier Comparison

### Free Tier (Essential)
- 500,000 tweets/month read
- 1,667 tweets/month write
- 1 app environment

**Good for:** Testing, small campaigns

### Basic Tier ($100/month)
- 10,000,000 tweets/month read
- 50,000 tweets/month write
- 2 app environments

**Good for:** Regular use, medium campaigns

### Pro Tier ($5,000/month)
- 1,000,000 tweets/month read
- 100,000 tweets/month write
- Full archive search

**Good for:** Large-scale operations

**For MarketingMind AI:** Free tier is enough to get started!

---

## Rate Limits (Free Tier)

### Reading Data
- **Search tweets:** 180 requests per 15 min
- **Get followers:** 15 requests per 15 min (1,000 followers each = 15,000 followers per 15 min)
- **Get user info:** 900 requests per 15 min

### Writing Data
- **Follow users:** 50 per 24 hours (Free tier limit)
- **Like tweets:** 1,000 per 24 hours
- **Send DMs:** 500 per 24 hours

**Important:** The tool automatically handles rate limiting!

---

## Troubleshooting

### Error: "403 Forbidden"
**Cause:** App permissions not set correctly
**Fix:** Set permissions to "Read and Write" (Step 3)

### Error: "401 Unauthorized"
**Cause:** Wrong API keys
**Fix:** Double-check keys in .env file

### Error: "429 Too Many Requests"
**Cause:** Rate limit exceeded
**Fix:** Wait 15 minutes, the tool will auto-retry

### Error: "App not set up correctly"
**Cause:** Missing app setup
**Fix:** Complete all settings in Twitter Developer Portal

---

## Security Best Practices

1. **Never commit .env file to Git** (already in .gitignore)
2. **Don't share API keys** publicly
3. **Rotate keys** if compromised
4. **Use environment variables** (we already do this)
5. **Monitor usage** in Twitter Developer Portal

---

## Alternative: Using Existing Keys

If you already have Twitter API keys from another project:

1. Just add them to `.env`
2. Make sure app has "Read and Write" permissions
3. Verify rate limits aren't exhausted

---

## Next Steps

After setup:

1. ✅ Keys added to `.env`
2. ✅ Run verification test
3. ✅ Try small test campaign
4. ✅ Review results
5. ✅ Scale up

You're ready to start finding leads!
