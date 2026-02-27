// IdeaShelf - Options Script
// Loads and saves user settings to chrome.storage.sync.

const DEFAULTS = {
  inboxPath: "~/IdeaShelf/inbox/",
  notifications: true,
  autoNote: false,
};

const inboxPathInput = document.getElementById("inbox-path");
const notificationsToggle = document.getElementById("notifications-toggle");
const autoNoteToggle = document.getElementById("auto-note-toggle");
const saveBtn = document.getElementById("save-btn");
const statusEl = document.getElementById("status");

// Load saved settings on page load
chrome.storage.sync.get(DEFAULTS, (settings) => {
  inboxPathInput.value = settings.inboxPath;
  notificationsToggle.checked = settings.notifications;
  autoNoteToggle.checked = settings.autoNote;
});

saveBtn.addEventListener("click", () => {
  const settings = {
    inboxPath: inboxPathInput.value.trim() || DEFAULTS.inboxPath,
    notifications: notificationsToggle.checked,
    autoNote: autoNoteToggle.checked,
  };

  chrome.storage.sync.set(settings, () => {
    if (chrome.runtime.lastError) {
      showStatus("Failed to save settings.", "error");
    } else {
      showStatus("Settings saved.", "success");
    }
  });
});

function showStatus(message, type) {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  statusEl.classList.remove("hidden");

  setTimeout(() => statusEl.classList.add("hidden"), 2500);
}
