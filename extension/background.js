// IdeaShelf - Background Service Worker
// Handles context menu, popup messages, and native messaging.

const NATIVE_HOST_NAME = "com.ideashelf.host";
const NATIVE_HOST_TIMEOUT_MS = 5000;

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
    captureFromTab(tab.id, tab.url, tab.title, "context_menu");
  }
});

// Note: The keyboard shortcut (_execute_action) opens the popup when a
// default_popup is set in manifest.json. The popup pre-fills with
// selected text, so the shortcut is still useful — it just goes through
// the popup flow, not directly through this service worker.

// --- Message Handling from Popup ---

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "capture-quick-note") {
    const payload = buildPayload({
      content: message.content,
      contentType: "quick_note",
      captureMethod: message.captureMethod || "popup",
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
      captureMethod: message.captureMethod || "popup",
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

function captureFromTab(tabId, url, title, captureMethod) {
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
      captureMethod,
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
  captureMethod,
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
    capture_method: captureMethod,
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
  let responded = false;

  function respond(result) {
    if (responded) return;
    responded = true;
    if (callback) callback(result);
  }

  try {
    const port = chrome.runtime.connectNative(NATIVE_HOST_NAME);

    // Timeout: if the host doesn't respond within 5 seconds, error out
    const timeoutId = setTimeout(() => {
      respond({ success: false, error: "Native host timed out" });
      try { port.disconnect(); } catch (_) {}
    }, NATIVE_HOST_TIMEOUT_MS);

    port.onMessage.addListener((response) => {
      clearTimeout(timeoutId);
      respond(response);
      port.disconnect();
    });

    port.onDisconnect.addListener(() => {
      clearTimeout(timeoutId);
      if (chrome.runtime.lastError) {
        const errMsg = chrome.runtime.lastError.message || "Disconnected";
        respond({ success: false, error: errMsg });
      }
    });

    port.postMessage(payload);
  } catch (err) {
    respond({ success: false, error: err.message });
  }
}

// --- Notifications ---

async function showNotification(title, message) {
  const settings = await chrome.storage.sync.get({ notifications: true });
  if (!settings.notifications) return;

  if (chrome.notifications) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon-48.png",
      title: title,
      message: message,
    });
  }
}
