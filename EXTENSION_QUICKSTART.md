# DistroFlow Extension - Quick Start Guide

Get the browser extension running in 5 minutes!

---

## Step 1: Start the Server (1 minute)

```bash
cd /path/to/distroflow
source venv/bin/activate
distroflow serve
```

You should see:
```
🚀 Starting DistroFlow API server on 127.0.0.1:8000
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open!**

---

## Step 2: Test the Server (30 seconds)

Open a new terminal:

```bash
cd /path/to/distroflow
python3 test_api_server.py
```

You should see:
```
🧪 Testing server status...
   ✅ Server status: ok
   ✅ Version: 0.1.0
🎉 All tests passed! Server is working correctly.
```

Or visit http://127.0.0.1:8000/docs in your browser to see the API docs.

---

## Step 3: Load Extension in Chrome (2 minutes)

1. Open Chrome and navigate to: `chrome://extensions/`

2. Enable **Developer mode** (toggle in top-right)

3. Click **Load unpacked**

4. Navigate to and select:
   ```
   /path/to/distroflow/extension
   ```

5. The DistroFlow icon 🚀 should appear in your toolbar

**Tip**: Click the puzzle icon → Find DistroFlow → Click pin to keep it visible

---

## Step 4: Test the Extension (2 minutes)

1. **Click the DistroFlow icon** 🚀

2. **Check server status**:
   - Top-right should show green dot: "Connected" ✅
   - If red, click ⚙️ Settings and verify URL is `http://127.0.0.1:8000`

3. **Check platform status**:
   - Each platform has a colored dot
   - Green ● = Authenticated
   - Red ● = Not authenticated

4. **Try a test post** (if you have platforms authenticated):
   - Check a platform (e.g., Twitter if authenticated)
   - Enter content: "Testing DistroFlow extension!"
   - Click "Post Now"
   - Check results below

---

## Authenticate Platforms (Optional)

If all platforms show red ●, authenticate at least one:

```bash
# In the terminal where distroflow is installed
distroflow setup twitter  # Or reddit, hackernews, instagram
```

Follow the prompts to save authentication cookies.

Then refresh the extension (click icon again) to see green ●.

---

## Troubleshooting

### "Server offline" error

**Fix**:
```bash
# Make sure server is running
distroflow serve

# Check it's accessible
curl http://127.0.0.1:8000
```

### Extension not loading

**Fix**:
1. Go to `chrome://extensions/`
2. Check for error messages
3. Click reload icon for DistroFlow
4. Verify Developer mode is enabled

### No platforms authenticated

**Fix**:
```bash
# Run setup for at least one platform
distroflow setup twitter
```

---

## Next Steps

- **Full Extension Guide**: See [docs/EXTENSION.md](docs/EXTENSION.md)
- **API Documentation**: Visit http://127.0.0.1:8000/docs (while server running)
- **Main README**: See [README.md](README.md)

---

## Architecture at a Glance

```
Browser Extension → Local API Server → Platform Websites
     ↓                    ↓
Chrome Storage    ~/.distroflow/auth
```

Everything runs locally. No external servers.

---

**Enjoy one-click cross-platform posting! 🚀**
