/**
 * DistroFlow Browser Extension - Background Service Worker
 * Handles extension lifecycle, notifications, and background tasks
 */

// Configuration
const DEFAULT_API_URL = 'http://127.0.0.1:8000';

// State
let apiUrl = DEFAULT_API_URL;

// ============================================================================
// Extension Lifecycle
// ============================================================================

chrome.runtime.onInstalled.addListener((details) => {
  console.log('DistroFlow extension installed', details);

  // Set default settings
  chrome.storage.local.get(['apiUrl'], (result) => {
    if (!result.apiUrl) {
      chrome.storage.local.set({ apiUrl: DEFAULT_API_URL });
    }
  });

  // Show welcome notification
  if (details.reason === 'install') {
    showNotification(
      'Welcome to DistroFlow!',
      'Click the extension icon to start posting to multiple platforms.'
    );

    // Open setup page
    chrome.tabs.create({
      url: 'https://github.com/yourusername/distroflow#quick-start'
    });
  }
});

chrome.runtime.onStartup.addListener(() => {
  console.log('DistroFlow extension started');

  // Load API URL from storage
  chrome.storage.local.get(['apiUrl'], (result) => {
    if (result.apiUrl) {
      apiUrl = result.apiUrl;
    }
  });
});

// ============================================================================
// Message Handling
// ============================================================================

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);

  switch (message.type) {
    case 'POST_CONTENT':
      handlePostContent(message.data)
        .then(result => sendResponse({ success: true, result }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true; // Will respond asynchronously

    case 'CHECK_SERVER':
      checkServerStatus()
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ connected: false, error: error.message }));
      return true;

    case 'GET_PLATFORM_STATUS':
      getPlatformStatus()
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;

    default:
      console.warn('Unknown message type:', message.type);
      sendResponse({ success: false, error: 'Unknown message type' });
  }
});

// ============================================================================
// API Communication
// ============================================================================

async function handlePostContent(data) {
  try {
    const response = await fetch(`${apiUrl}/post`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    // Show notification
    if (result.success) {
      showNotification(
        'Posted successfully!',
        `Posted to ${data.platforms.join(', ')}`
      );
    } else {
      showNotification(
        'Post failed',
        'Some platforms failed. Check results.'
      );
    }

    return result;
  } catch (error) {
    console.error('Post failed:', error);
    showNotification('Error', 'Failed to post. Is the server running?');
    throw error;
  }
}

async function checkServerStatus() {
  try {
    const response = await fetch(`${apiUrl}/`);
    const data = await response.json();

    return {
      connected: data.status === 'ok',
      version: data.version,
      platforms: data.authenticated_platforms
    };
  } catch (error) {
    console.error('Server check failed:', error);
    return { connected: false, error: error.message };
  }
}

async function getPlatformStatus() {
  try {
    const response = await fetch(`${apiUrl}/platforms`);
    const data = await response.json();

    return data;
  } catch (error) {
    console.error('Platform status check failed:', error);
    return { success: false, error: error.message };
  }
}

// ============================================================================
// Notifications
// ============================================================================

function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon128.png',
    title: title,
    message: message,
    priority: 2
  });
}

// ============================================================================
// Context Menu (Optional)
// ============================================================================

chrome.runtime.onInstalled.addListener(() => {
  // Create context menu for selected text
  chrome.contextMenus.create({
    id: 'postToDistroflow',
    title: 'Post to DistroFlow',
    contexts: ['selection']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'postToDistroflow') {
    // Store selected text and open popup
    chrome.storage.local.set({
      quickPostContent: info.selectionText,
      quickPostUrl: tab.url
    });

    // Open extension popup
    chrome.action.openPopup();
  }
});

// ============================================================================
// Alarms (for scheduled checks)
// ============================================================================

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'serverCheck') {
    checkServerStatus().then(result => {
      if (!result.connected) {
        console.warn('Server is offline');
      }
    });
  }
});

// Check server status every 5 minutes
chrome.alarms.create('serverCheck', { periodInMinutes: 5 });

// ============================================================================
// Badge Updates
// ============================================================================

function updateBadge(text, color) {
  chrome.action.setBadgeText({ text });
  chrome.action.setBadgeBackgroundColor({ color });
}

// Update badge on server status change
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.serverConnected) {
    const connected = changes.serverConnected.newValue;
    updateBadge(connected ? '' : '!', connected ? '#10b981' : '#ef4444');
  }
});

console.log('DistroFlow background service worker loaded');
