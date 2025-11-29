/**
 * DistroFlow Browser Extension - Content Script
 * Runs on web pages to provide quick posting functionality
 */

// Only inject on specific domains if needed
const ALLOWED_DOMAINS = [
  'twitter.com',
  'reddit.com',
  'news.ycombinator.com',
  'instagram.com',
  'linkedin.com',
  'facebook.com'
];

const currentDomain = window.location.hostname;
const isAllowedDomain = ALLOWED_DOMAINS.some(domain => currentDomain.includes(domain));

if (isAllowedDomain) {
  console.log('DistroFlow content script loaded on', currentDomain);

  // Add quick post button to page (optional feature)
  // Can be expanded later for platform-specific integrations
}

// Listen for messages from popup/background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_PAGE_CONTENT') {
    // Extract content from page for quick posting
    const content = extractPageContent();
    sendResponse({ content });
  }
});

function extractPageContent() {
  // Extract useful content from the current page
  const title = document.title;
  const url = window.location.href;

  // Try to get meta description
  const metaDescription = document.querySelector('meta[name="description"]');
  const description = metaDescription ? metaDescription.content : '';

  // Try to get selected text
  const selection = window.getSelection().toString();

  return {
    title,
    url,
    description,
    selection,
  };
}

// Keyboard shortcut to open extension (optional)
document.addEventListener('keydown', (e) => {
  // Cmd/Ctrl + Shift + D to open DistroFlow
  if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'D') {
    e.preventDefault();
    chrome.runtime.sendMessage({ type: 'OPEN_POPUP' });
  }
});
