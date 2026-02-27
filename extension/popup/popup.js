// IdeaShelf - Popup Script
// Handles quick note capture and communicates with the background service worker.

const noteInput = document.getElementById("note-input");
const saveBtn = document.getElementById("save-btn");
const statusEl = document.getElementById("status");

// Focus the text area on open
noteInput.focus();

// Try to pre-fill with any selected text from the active tab
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (!tabs[0]?.id) return;

  chrome.tabs.sendMessage(tabs[0].id, { type: "get-selection" }, (response) => {
    if (chrome.runtime.lastError) return;
    if (response?.selectedText) {
      noteInput.value = response.selectedText;
    }
  });
});

saveBtn.addEventListener("click", () => {
  const content = noteInput.value.trim();
  if (!content) {
    showStatus("Nothing to save.", "error");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.textContent = "Saving...";

  // Get the active tab info for source metadata
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0] || {};

    chrome.runtime.sendMessage(
      {
        type: "capture-quick-note",
        content: content,
        captureMethod: "popup",
        sourceUrl: tab.url || "",
        sourceTitle: tab.title || "",
        userNote: "",
      },
      (response) => {
        saveBtn.disabled = false;
        saveBtn.textContent = "Save";

        if (response?.success) {
          showStatus("Saved to IdeaShelf!", "success");
          noteInput.value = "";
          // Auto-close popup after a brief delay
          setTimeout(() => window.close(), 1200);
        } else {
          const errMsg = response?.error || "Failed to save. Is the native host installed?";
          showStatus(errMsg, "error");
        }
      }
    );
  });
});

// Allow Ctrl/Cmd+Enter to save
noteInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    saveBtn.click();
  }
});

function showStatus(message, type) {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  statusEl.classList.remove("hidden");

  if (type === "success") {
    setTimeout(() => statusEl.classList.add("hidden"), 3000);
  }
}
