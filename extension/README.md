# DistroFlow Browser Extension

Chrome extension for cross-platform content distribution.

## Features

✨ **Quick Post** - Post to multiple platforms with one click
🔄 **Real-time Updates** - WebSocket connection for live progress
⚙️ **Easy Setup** - Configure API server URL in settings
📊 **Platform Status** - See which platforms are authenticated
🔔 **Notifications** - Get notified when posts complete

## Installation

### Prerequisites

1. **Start the DistroFlow API server**:
   ```bash
   cd /path/to/distroflow
   source venv/bin/activate
   distroflow serve
   ```

   The server will start on `http://127.0.0.1:8000`

2. **Verify server is running**:
   - Open `http://127.0.0.1:8000/docs` in your browser
   - You should see the API documentation

### Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`

2. Enable **Developer mode** (toggle in top-right corner)

3. Click **Load unpacked**

4. Select the `extension` directory from your DistroFlow installation:
   ```
   /path/to/distroflow/extension
   ```

5. The DistroFlow icon should appear in your extensions toolbar

### First Time Setup

1. Click the DistroFlow extension icon

2. If the server status shows "Server offline":
   - Click ⚙️ Settings
   - Verify API URL is `http://127.0.0.1:8000`
   - Click "Test Connection"

3. Platform Authentication:
   - Green ● = Authenticated
   - Red ● = Not authenticated
   - Run `distroflow setup <platform>` to authenticate

## Usage

### Quick Post

1. Click the DistroFlow extension icon

2. Select platforms to post to (check boxes)

3. Enter your content:
   - **Title** (optional): For platforms that need it (Reddit, HN)
   - **Content**: Your post text
   - **URL** (optional): Link to share

4. Click **Post Now**

5. Results will appear below showing success/failure per platform

### Keyboard Shortcuts

- **Ctrl/Cmd + Enter** in content textarea: Submit post
- **Ctrl/Cmd + Shift + D** on any page: Open DistroFlow (when on supported sites)

### Context Menu

Right-click selected text on any page → **Post to DistroFlow** to quickly share

## Settings

Click ⚙️ Settings to:
- Change API server URL
- Test server connection

## Troubleshooting

### "Server offline" error

**Problem**: Extension can't connect to API server

**Solutions**:
1. Make sure server is running: `distroflow serve`
2. Check server URL in Settings matches where server is running
3. Try `http://localhost:8000` instead of `http://127.0.0.1:8000`

### "Not authenticated" for a platform

**Problem**: Platform shows red ● status

**Solution**:
```bash
# Authenticate platform from command line
distroflow setup twitter
distroflow setup reddit
# etc.
```

Then refresh extension (click icon again)

### Post fails with error

**Check**:
- Platform is authenticated (green ●)
- Server logs for errors: Look at terminal where `distroflow serve` is running
- Platform websites haven't changed (selectors may need updating)

### Extension not appearing

**Solutions**:
1. Refresh `chrome://extensions/` page
2. Make sure "Developer mode" is enabled
3. Try reloading the extension (click refresh icon)

## Development

### File Structure

```
extension/
├── manifest.json       # Extension configuration
├── popup.html          # Main UI
├── popup.css           # Styles
├── popup.js            # UI logic
├── background.js       # Service worker
├── content.js          # Content script
├── icons/              # Extension icons
└── README.md           # This file
```

### Making Changes

1. Edit files in `extension/` directory

2. Reload extension in Chrome:
   - Go to `chrome://extensions/`
   - Click reload icon for DistroFlow

3. Test changes

### Adding Features

**New Platform Support**:
- Add platform to checkbox list in `popup.html`
- Update platform status colors in `popup.js`
- Implement platform in main DistroFlow package

**Custom Notifications**:
- Edit `background.js` → `showNotification()`

**UI Styling**:
- Edit `popup.css`

## API Endpoints Used

The extension communicates with these DistroFlow API endpoints:

- `GET /` - Check server status
- `GET /platforms` - Get platform authentication status
- `POST /post` - Post content to platforms
- `WS /ws` - WebSocket for real-time updates

See API docs at `http://127.0.0.1:8000/docs` when server is running.

## Security

- Extension only communicates with local API server
- No data sent to external servers
- All credentials stored in `~/.distroflow/` directory
- WebSocket connection is local-only

## Future Features

- [ ] Schedule posts from extension
- [ ] View scheduled tasks
- [ ] Platform-specific content previews
- [ ] Batch posting to multiple URLs
- [ ] Template system
- [ ] Analytics dashboard
- [ ] Dark mode

## Support

- **Documentation**: See main README at project root
- **Issues**: https://github.com/yourusername/distroflow/issues
- **Discussions**: https://github.com/yourusername/distroflow/discussions

## License

MIT License - See LICENSE file in project root
