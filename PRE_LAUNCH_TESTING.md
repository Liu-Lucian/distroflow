# DistroFlow Pre-Launch Testing Checklist

Complete testing checklist before launch day.

---

## Installation Testing

### Fresh Install Test (Ubuntu/Mac/Windows)

- [ ] **Clone repository**
  ```bash
  git clone https://github.com/yourusername/distroflow.git
  cd distroflow
  ```

- [ ] **Create virtualenv**
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  ```

- [ ] **Install package**
  ```bash
  pip install -e .
  ```
  - [ ] No errors during install
  - [ ] All dependencies installed

- [ ] **Install Playwright**
  ```bash
  playwright install chromium
  ```
  - [ ] Browser downloaded successfully

- [ ] **Verify installation**
  ```bash
  distroflow --version
  ```
  - [ ] Shows version 0.1.0
  - [ ] No import errors

---

## CLI Testing

### Basic Commands

- [ ] **Version command**
  ```bash
  distroflow version
  ```
  - [ ] Shows version info
  - [ ] Shows description

- [ ] **Help command**
  ```bash
  distroflow --help
  ```
  - [ ] Lists all commands
  - [ ] Shows usage examples

### Setup Authentication

- [ ] **Setup Twitter**
  ```bash
  distroflow setup twitter
  ```
  - [ ] Shows instructions
  - [ ] Creates `~/.distroflow/twitter_auth.json`

- [ ] **Setup Reddit**
  ```bash
  distroflow setup reddit
  ```
  - [ ] Shows instructions
  - [ ] Creates `~/.distroflow/reddit_auth.json`

- [ ] **Setup HackerNews**
  ```bash
  distroflow setup hackernews
  ```
  - [ ] Shows instructions
  - [ ] Creates `~/.distroflow/hackernews_auth.json`

### Posting

- [ ] **Single platform post**
  ```bash
  distroflow launch \
    --platforms twitter \
    --content "Test post from DistroFlow CLI"
  ```
  - [ ] Posts successfully
  - [ ] Shows success message
  - [ ] Returns post URL

- [ ] **Multi-platform post**
  ```bash
  distroflow launch \
    --platforms "twitter,reddit" \
    --title "Test Post" \
    --content "Testing DistroFlow"
  ```
  - [ ] Posts to both platforms
  - [ ] Shows results for each
  - [ ] No errors

- [ ] **Post with URL**
  ```bash
  distroflow launch \
    --platforms hackernews \
    --title "Show HN: Test" \
    --url "https://github.com/yourusername/distroflow"
  ```
  - [ ] Posts to HN
  - [ ] URL included
  - [ ] Appears on /newest

### Scheduling

- [ ] **Schedule a post**
  ```bash
  distroflow schedule \
    --workflow test \
    --platforms twitter \
    --frequency once \
    --content "Scheduled test post"
  ```
  - [ ] Task created
  - [ ] Shows task ID

- [ ] **List tasks**
  ```bash
  distroflow list-tasks
  ```
  - [ ] Shows scheduled tasks
  - [ ] Correct status

- [ ] **Cancel task**
  ```bash
  distroflow cancel <task_id>
  ```
  - [ ] Task cancelled
  - [ ] Confirmation message

### Server Mode

- [ ] **Start server**
  ```bash
  distroflow serve
  ```
  - [ ] Server starts on port 8000
  - [ ] No errors
  - [ ] Shows startup message

- [ ] **Access API docs**
  - [ ] Open `http://127.0.0.1:8000/docs`
  - [ ] Swagger UI loads
  - [ ] All endpoints listed

- [ ] **Test API endpoint**
  ```bash
  curl http://127.0.0.1:8000/
  ```
  - [ ] Returns JSON response
  - [ ] Status: "ok"

---

## Browser Extension Testing

### Installation

- [ ] **Load extension in Chrome**
  - [ ] Go to `chrome://extensions/`
  - [ ] Enable Developer mode
  - [ ] Load unpacked → select `extension/` directory
  - [ ] Extension appears in toolbar

- [ ] **Extension icon**
  - [ ] Icon visible (rocket logo)
  - [ ] Clicking opens popup

### Server Connection

- [ ] **Check server status** (with server running)
  - [ ] Green dot: "Connected"
  - [ ] Shows version
  - [ ] Shows authenticated platforms

- [ ] **Check server status** (with server stopped)
  - [ ] Red dot: "Server offline"
  - [ ] Error message clear

- [ ] **Test connection** (in settings)
  - [ ] Click ⚙️ Settings
  - [ ] Click "Test Connection"
  - [ ] Shows connection result

### Platform Status

- [ ] **Authenticated platform**
  - [ ] Green ● next to platform name
  - [ ] Hovering shows "Authenticated"

- [ ] **Unauthenticated platform**
  - [ ] Red ● next to platform name
  - [ ] Hovering shows "Not authenticated"

### Posting

- [ ] **Single platform post**
  - [ ] Check Twitter (if authenticated)
  - [ ] Enter content
  - [ ] Click "Post Now"
  - [ ] Shows "Posting..." spinner
  - [ ] Shows success result
  - [ ] Verify post on Twitter

- [ ] **Multi-platform post**
  - [ ] Check Twitter and Reddit
  - [ ] Enter title and content
  - [ ] Click "Post Now"
  - [ ] Shows results for both
  - [ ] Verify posts on both platforms

- [ ] **Post with URL**
  - [ ] Enter content and URL
  - [ ] Post successfully
  - [ ] URL included in post

- [ ] **Character counter**
  - [ ] Type in content field
  - [ ] Counter updates
  - [ ] Shows warning over 280 chars

- [ ] **Keyboard shortcut**
  - [ ] Type content
  - [ ] Press Ctrl/Cmd+Enter
  - [ ] Post submits

### WebSocket Updates

- [ ] **Real-time progress**
  - [ ] Start a post
  - [ ] See "Posting..." status
  - [ ] See platform-by-platform updates
  - [ ] See final results

- [ ] **Desktop notifications** (if enabled)
  - [ ] Post starts → notification
  - [ ] Post completes → notification

### Context Menu

- [ ] **Right-click to post**
  - [ ] Select text on any page
  - [ ] Right-click
  - [ ] See "Post to DistroFlow" option
  - [ ] Click it
  - [ ] Extension opens with text pre-filled

### Settings

- [ ] **Change API URL**
  - [ ] Click ⚙️ Settings
  - [ ] Change URL to `http://localhost:8000`
  - [ ] Click "Save Settings"
  - [ ] Extension reconnects to new URL

- [ ] **Settings persistence**
  - [ ] Close popup
  - [ ] Reopen popup
  - [ ] Settings still saved

### Quick Actions

- [ ] **View Tasks button**
  - [ ] Click "📋 View Tasks"
  - [ ] Opens API docs in new tab

- [ ] **Docs button**
  - [ ] Click "📚 Docs"
  - [ ] Opens API docs in new tab

---

## Platform-Specific Testing

### Twitter

- [ ] **Basic post**
  - [ ] Text under 280 chars
  - [ ] Posts successfully
  - [ ] Appears in timeline

- [ ] **Post with hashtag**
  - [ ] Include #hashtag in content
  - [ ] Hashtag clickable

- [ ] **Post with mention**
  - [ ] Include @username
  - [ ] Mention clickable

### Reddit

- [ ] **Text post**
  - [ ] Title and content
  - [ ] Posts to r/test
  - [ ] Appears in subreddit

- [ ] **Post with URL**
  - [ ] Title and URL
  - [ ] URL post created

### HackerNews

- [ ] **Show HN post**
  - [ ] Title starts with "Show HN:"
  - [ ] URL included
  - [ ] Appears on /newest

- [ ] **Ask HN post**
  - [ ] Title starts with "Ask HN:"
  - [ ] Text content
  - [ ] Appears on /newest

### Instagram (if implemented)

- [ ] **Text post**
  - [ ] Content as caption
  - [ ] Posts successfully

---

## Error Handling Testing

### Invalid Input

- [ ] **No platforms selected**
  - [ ] Try to post without selecting platform
  - [ ] Shows error: "Please select at least one platform"

- [ ] **Empty content**
  - [ ] Try to post with empty content
  - [ ] Shows error: "Please enter content"

- [ ] **Invalid URL**
  - [ ] Enter malformed URL
  - [ ] Handles gracefully

### Authentication Errors

- [ ] **Expired cookies**
  - [ ] Use old/invalid auth file
  - [ ] Shows authentication error
  - [ ] Suggests re-authenticating

- [ ] **Missing auth file**
  - [ ] Try to post to unauthenticated platform
  - [ ] Shows error
  - [ ] Suggests running setup

### Network Errors

- [ ] **Server offline**
  - [ ] Stop server
  - [ ] Try to post
  - [ ] Shows clear error
  - [ ] Suggests checking server

- [ ] **Network timeout**
  - [ ] Simulate slow connection
  - [ ] Handles timeout gracefully

### Platform Errors

- [ ] **Rate limited**
  - [ ] Post many times quickly
  - [ ] Handles rate limit error
  - [ ] Shows retry suggestion

- [ ] **Platform down**
  - [ ] If platform is down
  - [ ] Shows platform-specific error

---

## Performance Testing

### Speed

- [ ] **CLI startup time**
  - [ ] `time distroflow --version`
  - [ ] < 2 seconds

- [ ] **Extension load time**
  - [ ] Click extension icon
  - [ ] Popup opens in < 500ms

- [ ] **Single platform post**
  - [ ] Time from click to success
  - [ ] < 10 seconds (including delays)

- [ ] **Multi-platform post (3 platforms)**
  - [ ] Concurrent posting
  - [ ] < 30 seconds total

### Resource Usage

- [ ] **Memory usage**
  - [ ] Server running idle
  - [ ] < 100 MB RAM

- [ ] **CPU usage**
  - [ ] Server running idle
  - [ ] < 5% CPU

- [ ] **Browser memory**
  - [ ] Extension loaded
  - [ ] < 50 MB

---

## Security Testing

### Credentials

- [ ] **Auth files permissions**
  - [ ] Check `~/.distroflow/` permissions
  - [ ] Files not world-readable

- [ ] **No credentials in logs**
  - [ ] Check server logs
  - [ ] No passwords/cookies logged

- [ ] **No credentials in code**
  - [ ] Grep for passwords
  - [ ] All use env vars or config files

### Extension Permissions

- [ ] **Minimal permissions**
  - [ ] Check manifest.json
  - [ ] Only required permissions

- [ ] **CORS headers**
  - [ ] Server sends correct CORS headers
  - [ ] Extension can connect

---

## Documentation Testing

### README

- [ ] **Quick start works**
  - [ ] Follow README steps
  - [ ] No missing steps
  - [ ] All commands work

- [ ] **Examples work**
  - [ ] Copy-paste examples
  - [ ] All execute correctly

- [ ] **Links work**
  - [ ] Click all links in README
  - [ ] No 404s

### Guides

- [ ] **QUICKSTART.md**
  - [ ] Follow 5-minute guide
  - [ ] Complete setup
  - [ ] Make first post

- [ ] **ARCHITECTURE.md**
  - [ ] Code examples work
  - [ ] Diagrams load

- [ ] **EXTENSION.md**
  - [ ] Installation steps work
  - [ ] Troubleshooting tips accurate

### API Docs

- [ ] **Swagger UI**
  - [ ] Open `/docs`
  - [ ] All endpoints documented
  - [ ] Try out feature works

- [ ] **Code examples**
  - [ ] Copy Python examples
  - [ ] Execute successfully

---

## Cross-Platform Testing

### Operating Systems

- [ ] **macOS**
  - [ ] Install works
  - [ ] CLI works
  - [ ] Extension works

- [ ] **Linux (Ubuntu)**
  - [ ] Install works
  - [ ] CLI works
  - [ ] Extension works

- [ ] **Windows**
  - [ ] Install works
  - [ ] CLI works
  - [ ] Extension works

### Browsers

- [ ] **Chrome**
  - [ ] Extension installs
  - [ ] All features work

- [ ] **Brave**
  - [ ] Extension installs
  - [ ] All features work

- [ ] **Edge**
  - [ ] Extension installs
  - [ ] All features work

### Python Versions

- [ ] **Python 3.8**
  - [ ] Install works
  - [ ] No deprecation warnings

- [ ] **Python 3.9**
  - [ ] Install works

- [ ] **Python 3.10**
  - [ ] Install works

- [ ] **Python 3.11**
  - [ ] Install works

---

## Automated Test Script

Run this before launch:

```bash
#!/bin/bash
# Pre-launch automated tests

echo "🧪 DistroFlow Pre-Launch Tests"
echo "=============================="

# 1. Test API server
echo ""
echo "1. Testing API server..."
python3 test_api_server.py || exit 1

# 2. Test CLI version
echo ""
echo "2. Testing CLI..."
distroflow --version || exit 1

# 3. Test linting
echo ""
echo "3. Testing code quality..."
./venv/bin/black --check distroflow/ || exit 1
./venv/bin/flake8 distroflow/ --max-line-length=100 --extend-ignore=E203,W503 || exit 1

# 4. Test import
echo ""
echo "4. Testing imports..."
python3 -c "from distroflow import __version__; print(f'Version: {__version__}')" || exit 1

# 5. Test extension files exist
echo ""
echo "5. Testing extension files..."
[ -f "extension/manifest.json" ] || exit 1
[ -f "extension/popup.html" ] || exit 1
[ -f "extension/popup.js" ] || exit 1
[ -f "extension/background.js" ] || exit 1
[ -f "extension/icons/icon16.png" ] || exit 1
echo "✅ All extension files present"

# 6. Test documentation exists
echo ""
echo "6. Testing documentation..."
[ -f "README.md" ] || exit 1
[ -f "docs/QUICKSTART.md" ] || exit 1
[ -f "docs/ARCHITECTURE.md" ] || exit 1
[ -f "docs/EXTENSION.md" ] || exit 1
echo "✅ All documentation present"

echo ""
echo "=============================="
echo "✅ All automated tests passed!"
echo "=============================="
```

Save as `pre_launch_test.sh` and run: `bash pre_launch_test.sh`

---

## Final Checklist

Before clicking "Launch":

- [ ] All automated tests pass
- [ ] Manual testing complete
- [ ] Documentation reviewed
- [ ] Demo video recorded
- [ ] Screenshots captured
- [ ] GitHub repo polished
- [ ] Launch posts written
- [ ] Response templates ready
- [ ] Team notified (if any)
- [ ] Coffee ready ☕

---

**When all boxes are checked, you're ready to launch! 🚀**
