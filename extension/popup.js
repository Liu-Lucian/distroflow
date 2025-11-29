/**
 * DistroFlow Browser Extension - Popup Script
 * Handles UI interactions and API communication
 */

// Configuration
let API_URL = 'http://127.0.0.1:8000';

// DOM Elements
const serverStatus = document.getElementById('serverStatus');
const platformsContainer = document.getElementById('platformsContainer');
const postTitle = document.getElementById('postTitle');
const postContent = document.getElementById('postContent');
const postUrl = document.getElementById('postUrl');
const charCount = document.getElementById('charCount');
const postBtn = document.getElementById('postBtn');
const resultsSection = document.getElementById('resultsSection');
const results = document.getElementById('results');
const viewTasksBtn = document.getElementById('viewTasksBtn');
const settingsBtn = document.getElementById('settingsBtn');
const openDocsBtn = document.getElementById('openDocsBtn');
const settingsPanel = document.getElementById('settingsPanel');
const apiUrl = document.getElementById('apiUrl');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const testConnectionBtn = document.getElementById('testConnectionBtn');

// State
let ws = null;
let platformsStatus = {};

// ============================================================================
// Initialization
// ============================================================================

async function init() {
  // Load settings from storage
  const settings = await chrome.storage.local.get(['apiUrl']);
  if (settings.apiUrl) {
    API_URL = settings.apiUrl;
    apiUrl.value = API_URL;
  }

  // Check server status
  await checkServerStatus();

  // Load platform authentication status
  await loadPlatformStatus();

  // Setup WebSocket connection
  setupWebSocket();

  // Setup event listeners
  setupEventListeners();

  // Update char count
  updateCharCount();
}

// ============================================================================
// Server Communication
// ============================================================================

async function checkServerStatus() {
  try {
    const response = await fetch(`${API_URL}/`);
    const data = await response.json();

    if (data.status === 'ok') {
      updateServerStatus('connected', 'Connected');
      return true;
    }
  } catch (error) {
    updateServerStatus('error', 'Server offline');
    console.error('Server connection failed:', error);
    return false;
  }
}

function updateServerStatus(status, text) {
  serverStatus.className = `server-status ${status}`;
  serverStatus.querySelector('.status-text').textContent = text;
}

async function loadPlatformStatus() {
  try {
    const response = await fetch(`${API_URL}/platforms`);
    const data = await response.json();

    if (data.success) {
      data.platforms.forEach(platform => {
        platformsStatus[platform.name] = platform.authenticated;
        updatePlatformStatus(platform.name, platform.authenticated);
      });
    }
  } catch (error) {
    console.error('Failed to load platform status:', error);
  }
}

function updatePlatformStatus(platformName, authenticated) {
  const statusElement = document.querySelector(`[data-status="${platformName}"]`);
  if (statusElement) {
    if (authenticated) {
      statusElement.classList.add('authenticated');
      statusElement.title = 'Authenticated';
    } else {
      statusElement.classList.remove('authenticated');
      statusElement.title = 'Not authenticated';
    }
  }
}

// ============================================================================
// WebSocket Connection
// ============================================================================

function setupWebSocket() {
  try {
    const wsUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
    ws = new WebSocket(`${wsUrl}/ws`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after 5 seconds
      setTimeout(setupWebSocket, 5000);
    };
  } catch (error) {
    console.error('Failed to setup WebSocket:', error);
  }
}

function handleWebSocketMessage(data) {
  console.log('WebSocket message:', data);

  switch (data.type) {
    case 'post_start':
      showNotification('Posting started', `Posting to ${data.platforms.join(', ')}`);
      break;

    case 'platform_start':
      addPlatformProgress(data.platform, 'in_progress');
      break;

    case 'platform_result':
      updatePlatformProgress(data.platform, data.result);
      break;

    case 'post_complete':
      showNotification(
        data.success ? 'Post complete!' : 'Post failed',
        data.success ? 'Posted successfully' : 'Some posts failed'
      );
      break;
  }
}

// ============================================================================
// Posting Logic
// ============================================================================

async function handlePost() {
  // Get selected platforms
  const selectedPlatforms = Array.from(
    document.querySelectorAll('input[data-platform]:checked')
  ).map(input => input.value);

  if (selectedPlatforms.length === 0) {
    showError('Please select at least one platform');
    return;
  }

  const content = postContent.value.trim();
  if (!content) {
    showError('Please enter content to post');
    return;
  }

  // Disable button and show loading
  setPostButtonLoading(true);

  // Clear previous results
  results.innerHTML = '';
  resultsSection.style.display = 'none';

  try {
    const response = await fetch(`${API_URL}/post`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        platforms: selectedPlatforms,
        content: content,
        title: postTitle.value.trim() || null,
        url: postUrl.value.trim() || null,
      }),
    });

    const data = await response.json();

    // Show results
    displayResults(data.results);

    // Clear form if all succeeded
    if (data.success) {
      postContent.value = '';
      postTitle.value = '';
      postUrl.value = '';
      updateCharCount();
      showNotification('Success!', 'Posted to all platforms');
    }

  } catch (error) {
    console.error('Post failed:', error);
    showError('Failed to post. Is the server running?');
  } finally {
    setPostButtonLoading(false);
  }
}

function setPostButtonLoading(loading) {
  postBtn.disabled = loading;
  postBtn.querySelector('.btn-text').style.display = loading ? 'none' : 'inline';
  postBtn.querySelector('.btn-loading').style.display = loading ? 'inline' : 'none';
}

function displayResults(resultsList) {
  resultsSection.style.display = 'block';

  resultsList.forEach(result => {
    const item = document.createElement('div');
    item.className = `result-item ${result.success ? 'success' : 'error'}`;

    const icon = document.createElement('span');
    icon.className = 'result-icon';
    icon.textContent = result.success ? '✓' : '✗';

    const text = document.createElement('span');
    text.className = 'result-text';
    text.textContent = result.success
      ? `${result.platform}: Posted successfully`
      : `${result.platform}: ${result.error}`;

    item.appendChild(icon);
    item.appendChild(text);

    if (result.url) {
      const link = document.createElement('a');
      link.className = 'result-link';
      link.href = result.url;
      link.target = '_blank';
      link.textContent = 'View';
      item.appendChild(link);
    }

    results.appendChild(item);
  });
}

// ============================================================================
// UI Helpers
// ============================================================================

function updateCharCount() {
  const count = postContent.value.length;
  charCount.textContent = count;

  // Warn if over Twitter limit
  if (count > 280) {
    charCount.style.color = '#ef4444';
  } else {
    charCount.style.color = '#6b7280';
  }
}

function showError(message) {
  // Simple alert for now, can be improved with custom toast
  alert(message);
}

function showNotification(title, message) {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {
      body: message,
      icon: 'icons/icon48.png'
    });
  }
}

function addPlatformProgress(platform, status) {
  // Could add real-time progress indicators
  console.log(`${platform}: ${status}`);
}

function updatePlatformProgress(platform, result) {
  // Could update real-time progress indicators
  console.log(`${platform} result:`, result);
}

// ============================================================================
// Settings
// ============================================================================

async function saveSettings() {
  const newApiUrl = apiUrl.value.trim();

  await chrome.storage.local.set({ apiUrl: newApiUrl });
  API_URL = newApiUrl;

  showNotification('Settings saved', 'API URL updated');

  // Recheck connection
  await checkServerStatus();
  await loadPlatformStatus();
  setupWebSocket();
}

async function testConnection() {
  testConnectionBtn.textContent = 'Testing...';
  testConnectionBtn.disabled = true;

  const success = await checkServerStatus();

  testConnectionBtn.textContent = 'Test Connection';
  testConnectionBtn.disabled = false;

  if (success) {
    showNotification('Connection OK', 'Server is reachable');
  } else {
    showError('Connection failed. Check if server is running.');
  }
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
  // Post button
  postBtn.addEventListener('click', handlePost);

  // Char count
  postContent.addEventListener('input', updateCharCount);

  // Enter to post (Ctrl/Cmd + Enter in textarea)
  postContent.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handlePost();
    }
  });

  // Quick actions
  viewTasksBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: `${API_URL}/docs#/default/list_tasks_tasks_get` });
  });

  settingsBtn.addEventListener('click', () => {
    settingsPanel.style.display = settingsPanel.style.display === 'none' ? 'block' : 'none';
  });

  openDocsBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: `${API_URL}/docs` });
  });

  // Settings
  saveSettingsBtn.addEventListener('click', saveSettings);
  testConnectionBtn.addEventListener('click', testConnection);

  // Request notification permission
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}

// ============================================================================
// Start
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
