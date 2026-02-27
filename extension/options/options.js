// IdeaShelf - Options Script
// Loads and saves user settings to chrome.storage.sync.

const DEFAULTS = {
  notifications: true,
};

const notificationsToggle = document.getElementById("notifications-toggle");
const saveBtn = document.getElementById("save-btn");
const statusEl = document.getElementById("status");

// Load saved settings on page load
chrome.storage.sync.get(DEFAULTS, (settings) => {
  notificationsToggle.checked = settings.notifications;
});

saveBtn.addEventListener("click", () => {
  const settings = {
    notifications: notificationsToggle.checked,
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
