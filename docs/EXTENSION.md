# DistroFlow Browser Extension Guide

Complete guide to using the DistroFlow Chrome extension.

---

## Overview

The DistroFlow browser extension provides a convenient way to post content to multiple platforms directly from your browser. It connects to your local DistroFlow API server and provides:

- ✨ Quick posting to multiple platforms
- 🔄 Real-time updates via WebSocket
- 📊 Platform authentication status
- 🔔 Desktop notifications
- ⚙️ Easy configuration

---

## Installation

### Step 1: Install DistroFlow

If you haven't already, install DistroFlow:

```bash
git clone https://github.com/yourusername/distroflow.git
cd distroflow
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
playwright install chromium
```

### Step 2: Start the API Server

The extension requires the DistroFlow API server to be running:

```bash
cd distroflow
source venv/bin/activate
distroflow serve
```

You should see:
```
🚀 Starting DistroFlow API server on 127.0.0.1:8000
📡 API docs available at: http://127.0.0.1:8000/docs
🔌 WebSocket endpoint: ws://127.0.0.1:8000/ws
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open** - the server must be running for the extension to work.

### Step 3: Load Extension in Chrome

1. Open Chrome/Brave/Edge and navigate to:
   - Chrome: `chrome://extensions/`
   - Brave: `brave://extensions/`
   - Edge: `edge://extensions/`

2. Enable **Developer mode** (toggle in top-right corner)

3. Click **Load unpacked**

4. Navigate to and select:
   ```
   /path/to/distroflow/extension
   ```

5. The DistroFlow icon 🚀 should appear in your browser toolbar

**Tip**: Pin the extension for quick access:
- Click the puzzle icon in the toolbar
- Find "DistroFlow"
- Click the pin icon

---

## First Time Setup

### 1. Verify Server Connection

Click the DistroFlow icon. You should see:
- **Green dot**: "Connected" - Server is reachable ✅
- **Yellow dot**: "Connecting..." - Trying to connect ⏳
- **Red dot**: "Server offline" - Can't reach server ❌

If you see "Server offline":
1. Make sure `distroflow serve` is running
2. Click ⚙️ Settings
3. Verify API URL is `http://127.0.0.1:8000`
4. Click "Test Connection"

### 2. Authenticate Platforms

Platform checkboxes show authentication status:
- **Green ●** = Authenticated, ready to use
- **Red ●** = Not authenticated

To authenticate platforms:

```bash
# From command line (terminal where distroflow is installed)
distroflow setup twitter
distroflow setup reddit
distroflow setup hackernews
distroflow setup instagram
```

Then refresh the extension popup to see updated status.

---

## Usage

### Quick Post

1. **Click the DistroFlow icon** in your toolbar

2. **Select platforms** by checking the boxes:
   - Check multiple platforms to cross-post
   - Only platforms with green ● are authenticated

3. **Fill in content**:
   - **Title** (optional): For Reddit, HackerNews
   - **Content**: Your post text (required)
   - **URL** (optional): Link to share

4. **Click "Post Now"**

5. **View results**:
   - Green ✓ = Success
   - Red ✗ = Failed (with error message)
   - Click "View" link to see your post

### Keyboard Shortcuts

- **Ctrl/Cmd + Enter**: Submit post (when in content textarea)
- **Ctrl/Cmd + Shift + D**: Open DistroFlow (on supported sites)

### Context Menu

Right-click selected text on any page → **Post to DistroFlow**

This will:
1. Copy selected text to content field
2. Copy current page URL
3. Open the extension popup

Perfect for sharing quotes, articles, or interesting findings.

---

## Advanced Features

### Platform-Specific Formatting

DistroFlow automatically formats content for each platform:

**Example Post**:
```
Title: Show HN: My New Project
Content: I built a tool to automate cross-platform posting!
URL: https://github.com/user/project
```

**What Gets Posted**:
- **Twitter**: "I built a tool to automate cross-platform posting! https://github.com/user/project"
- **Reddit**: Title + Content as text post to r/test
- **HackerNews**: "Show HN: My New Project" with URL
- **Instagram**: Content as caption (no clickable URL)

### Real-Time Updates

The extension uses WebSocket for live updates:

When you click "Post Now":
1. Button shows "Posting..." with spinner
2. You get notifications as each platform completes
3. Results appear in real-time

You can:
- Close the popup while posting
- Get desktop notifications for completion
- See final results when you reopen

### Settings

Click ⚙️ Settings to configure:

**API Server URL**:
- Default: `http://127.0.0.1:8000`
- Change if running server on different port/host
- Use `http://localhost:8000` if 127.0.0.1 doesn't work

**Test Connection**:
- Verifies server is reachable
- Shows authenticated platforms
- Useful for debugging

### Quick Actions

**📋 View Tasks**: Opens API docs showing scheduled tasks

**⚙️ Settings**: Toggle settings panel

**📚 Docs**: Opens full API documentation

---

## Platform-Specific Tips

### Twitter
- 280 character limit (extension shows warning)
- Media uploads not yet supported via extension
- Use hashtags in content

### Reddit
- **Title required** for posts
- Default posts to r/test (safe for testing)
- Change subreddit in code: `distroflow/platforms/reddit.py`

### HackerNews
- **URL or title required**
- Prefix title with "Show HN:" or "Ask HN:"
- Text posts go to "newest" page

### Instagram
- Content becomes caption
- URLs not clickable (Instagram limitation)
- Media upload not yet supported

---

## Troubleshooting

### Extension Issues

#### "Server offline" error

**Cause**: Can't reach API server

**Solutions**:
```bash
# 1. Start the server
cd /path/to/distroflow
source venv/bin/activate
distroflow serve

# 2. Verify it's running
curl http://127.0.0.1:8000

# 3. Check extension settings
# Click ⚙️ → Verify URL → Test Connection
```

#### Platform shows red ●

**Cause**: Platform not authenticated

**Solution**:
```bash
# Authenticate from command line
distroflow setup <platform>

# Example:
distroflow setup twitter
```

Then refresh extension.

#### Post fails with "Authentication failed"

**Cause**: Cookies expired or invalid

**Solution**:
1. Delete old auth file:
   ```bash
   rm ~/.distroflow/twitter_auth.json
   ```

2. Re-authenticate:
   ```bash
   distroflow setup twitter
   ```

3. Try posting again

#### Extension not loading

**Solutions**:
1. Go to `chrome://extensions/`
2. Click reload icon for DistroFlow
3. Check for error messages
4. Verify manifest.json is valid

### Server Issues

#### Server won't start

**Check**:
```bash
# 1. Is port 8000 in use?
lsof -i :8000
kill <PID>  # If something else is using it

# 2. Are dependencies installed?
pip install fastapi uvicorn python-dotenv

# 3. Try different port
distroflow serve --port 8080
# Then update extension settings to http://127.0.0.1:8080
```

#### CORS errors in console

**Cause**: Browser security blocking requests

**Solution**: This should work automatically, but if not:
1. Make sure server is running with CORS middleware
2. Check `distroflow/api/server.py` has `CORSMiddleware`
3. Restart server

### Posting Issues

#### All platforms fail

**Check**:
1. Server is running
2. Extension shows "Connected"
3. At least one platform authenticated
4. Content field not empty

#### Some platforms succeed, others fail

**Common causes**:
- **Platform not authenticated**: Red ●
- **Platform UI changed**: Selectors outdated
- **Network issue**: Platform website down

**Debug**:
1. Check server logs in terminal
2. Try posting just to failed platform
3. Check if you can post manually on platform website

---

## Development

### File Structure

```
extension/
├── manifest.json         # Extension metadata
├── popup.html            # Main UI
├── popup.css             # Styles
├── popup.js              # UI logic
├── background.js         # Service worker
├── content.js            # Content script
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

### Making Changes

1. **Edit files** in `extension/` directory

2. **Reload extension**:
   - Go to `chrome://extensions/`
   - Click reload icon for DistroFlow

3. **Test changes**

4. **View console**:
   - Right-click extension icon → Inspect popup
   - Check for errors in console

### Adding Features

**Add a new platform**:

1. Implement in main package: `distroflow/platforms/newplatform.py`

2. Add to extension UI: `popup.html`
   ```html
   <label class="platform-checkbox">
     <input type="checkbox" value="newplatform" data-platform="newplatform">
     <span class="platform-name">New Platform</span>
     <span class="platform-status" data-status="newplatform">●</span>
   </label>
   ```

3. Update status loading in `popup.js`

**Customize styling**:
- Edit `popup.css`
- Use CSS variables for easy theming

**Add notifications**:
- Edit `background.js` → `showNotification()`

---

## Security & Privacy

### Data Flow

```
Browser Extension → Local API Server → Platform Websites
      ↓                    ↓
 Chrome Storage    ~/.distroflow/auth
```

**Nothing goes to external servers** except the platforms you post to.

### What's Stored

**Chrome Storage** (chrome.storage.local):
- API server URL
- Last used settings

**No passwords or credentials** are stored in the extension.

**Authentication** is handled by:
- DistroFlow CLI (`distroflow setup`)
- Stored in `~/.distroflow/` directory
- Read by API server only

### Permissions Explained

The extension requests these permissions:

- **storage**: Save settings (API URL, etc.)
- **activeTab**: Access current tab URL for sharing
- **notifications**: Show desktop notifications
- **host_permissions**: Connect to local API server

**No broad permissions** like "access all websites" or "read browsing history".

---

## Tips & Best Practices

### Efficient Workflow

1. **Keep server running**: Start server once, keep terminal open
2. **Pin extension**: Quick access from toolbar
3. **Use keyboard shortcut**: Ctrl/Cmd+Enter to post
4. **Check status first**: Green ● before posting

### Testing Posts

**Use safe subreddits**:
- r/test (default in Reddit platform)
- r/your_private_subreddit

**HackerNews**:
- Posts go to "newest" page
- Won't hit front page unless popular

**Twitter**:
- Consider using test account first
- No "draft" mode yet

### Platform Limits

Be aware of rate limits:
- **Twitter**: ~300 tweets per 3 hours
- **Reddit**: ~10 posts per hour
- **HackerNews**: ~5 submissions per day
- **Instagram**: ~100 posts per day

DistroFlow adds human-like delays, but don't spam.

---

## Roadmap

Planned features:

- [ ] Schedule posts from extension
- [ ] View scheduled tasks
- [ ] Media upload support
- [ ] Content templates
- [ ] Platform-specific previews
- [ ] Draft saving
- [ ] Post history
- [ ] Analytics dashboard
- [ ] Dark mode

Vote on features: [GitHub Discussions](https://github.com/yourusername/distroflow/discussions)

---

## FAQ

**Q: Can I use this on Firefox?**
A: Not yet. Firefox support requires Manifest v2. Planned for future release.

**Q: Does the server need to run all the time?**
A: Only when using the extension. Start with `distroflow serve`, stop with Ctrl+C.

**Q: Can I run the server remotely?**
A: Yes, but not recommended for security. Would need to:
- Run server on remote machine
- Change extension API URL to remote address
- Ensure server is secure (HTTPS, auth)

**Q: How do I uninstall?**
A: Remove extension from `chrome://extensions/`. Server and auth files stay in `~/.distroflow/`.

**Q: Can multiple people use the same server?**
A: Yes, but they'll share authentication. Better to run separate instances.

---

## Support

- **Bug reports**: [GitHub Issues](https://github.com/yourusername/distroflow/issues)
- **Questions**: [GitHub Discussions](https://github.com/yourusername/distroflow/discussions)
- **Documentation**: [Main README](../README.md)

---

**Enjoy cross-platform posting! 🚀**
