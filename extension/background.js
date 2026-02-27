// IdeaShelf - Background Service Worker
// Handles context menu, keyboard shortcut, popup messages, and native messaging.

const NATIVE_HOST_NAME = "com.ideashelf.host";

// --- Context Menu ---

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "save-to-ideashelf",
    title: "Save to IdeaShelf",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "save-to-ideashelf" && tab?.id) {
    captureFromTab(tab.id, tab.url, tab.title);
  }
});

// --- Keyboard Shortcut ---
// _execute_action opens the popup by default. If no popup is set, this fires.
// Since we have a popup, the shortcut opens it. To support shortcut-based capture
// without the popup, we listen for a message from the popup or handle it here
// when the popup isn't open.

chrome.commands.onCommand.addListener((command, tab) => {
  if (command === "_execute_action" && tab?.id) {
    captureFromTab(tab.id, tab.url, tab.title);
  }
});

// --- Message Handling from Popup and Content Script ---

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "capture-quick-note") {
    const payload = buildPayload({
      content: message.content,
      contentType: "quick_note",
      sourceUrl: message.sourceUrl || "",
      sourceTitle: message.sourceTitle || "",
      precedingText: "",
      followingText: "",
      userNote: message.userNote || "",
    });
    sendToNativeHost(payload, sendResponse);
    return true; // keep channel open for async response
  }

  if (message.type === "capture-selection") {
    const payload = buildPayload({
      content: message.content,
      contentType: message.contentType || "text_selection",
      sourceUrl: message.sourceUrl || "",
      sourceTitle: message.sourceTitle || "",
      precedingText: message.precedingText || "",
      followingText: message.followingText || "",
      userNote: message.userNote || "",
    });
    sendToNativeHost(payload, sendResponse);
    return true;
  }

  return false;
});

// --- Core Capture Flow ---

function captureFromTab(tabId, url, title) {
  chrome.tabs.sendMessage(tabId, { type: "get-selection" }, (response) => {
    if (chrome.runtime.lastError) {
      // Content script may not be injected (e.g. chrome:// pages)
      showNotification("Capture failed", "Cannot capture from this page.");
      return;
    }

    const content = response?.selectedText || "";
    const contentType = content ? "text_selection" : "bookmark";

    const payload = buildPayload({
      content: content || `Bookmarked: ${title || url}`,
      contentType,
      sourceUrl: url || "",
      sourceTitle: title || "",
      precedingText: response?.precedingText || "",
      followingText: response?.followingText || "",
      userNote: "",
    });

    sendToNativeHost(payload, (result) => {
      if (result?.success) {
        showNotification("Saved", "Idea captured to IdeaShelf.");
      } else {
        showNotification("Error", result?.error || "Failed to save.");
      }
    });
  });
}

// --- Payload Builder ---

function buildPayload({
  content,
  contentType,
  sourceUrl,
  sourceTitle,
  precedingText,
  followingText,
  userNote,
}) {
  return {
    id: crypto.randomUUID(),
    captured_at: new Date().toISOString(),
    source_url: sourceUrl,
    source_title: sourceTitle,
    content_type: contentType,
    content: content,
    context: {
      preceding_text: precedingText,
      following_text: followingText,
    },
    user_note: userNote,
  };
}

// --- Native Messaging ---

function sendToNativeHost(payload, callback) {
  try {
    const port = chrome.runtime.connectNative(NATIVE_HOST_NAME);

    port.onMessage.addListener((response) => {
      if (callback) callback(response);
      port.disconnect();
    });

    port.onDisconnect.addListener(() => {
      if (chrome.runtime.lastError) {
        const errMsg = chrome.runtime.lastError.message || "Disconnected";
        if (callback) callback({ success: false, error: errMsg });
      }
    });

    port.postMessage(payload);
  } catch (err) {
    if (callback) callback({ success: false, error: err.message });
  }
}

// --- Notifications ---

async function showNotification(title, message) {
  const settings = await chrome.storage.sync.get({ notifications: true });
  if (!settings.notifications) return;

  // Service workers can't use the Notifications API directly,
  // so we use chrome.notifications if available, otherwise log.
  if (chrome.notifications) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon-48.png",
      title: title,
      message: message,
    });
  }
}
