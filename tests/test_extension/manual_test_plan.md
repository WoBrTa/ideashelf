# IdeaShelf Extension - Manual Test Plan

Use this checklist to verify the Chrome extension works correctly after installation.

## Prerequisites

- [ ] Chrome browser installed
- [ ] Extension loaded in developer mode (`chrome://extensions`)
- [ ] Native messaging host installed (`native-host/install.sh YOUR_EXTENSION_ID`)
- [ ] Inbox directory exists at `~/IdeaShelf/inbox/`

## Test Cases

### 1. Extension Loads Successfully
- [ ] Navigate to `chrome://extensions`
- [ ] Enable "Developer mode" (toggle in top-right)
- [ ] Click "Load unpacked" and select the `extension/` folder
- [ ] Extension appears in the list with no errors
- [ ] Extension icon is visible in the Chrome toolbar

### 2. Context Menu Appears on Text Selection
- [ ] Navigate to any web page (e.g., Wikipedia)
- [ ] Select some text on the page
- [ ] Right-click the selected text
- [ ] "Save to IdeaShelf" menu item is visible in the context menu

### 3. Right-Click Capture Writes JSON to Inbox
- [ ] Select text on a web page
- [ ] Right-click and choose "Save to IdeaShelf"
- [ ] Check `~/IdeaShelf/inbox/` for a new `.json` file
- [ ] Open the JSON file and verify it contains:
  - `id` (UUID)
  - `captured_at` (ISO timestamp)
  - `source_url` (the page URL)
  - `source_title` (the page title)
  - `content_type`: "text_selection"
  - `content` (the selected text)
  - `context.preceding_text` and `context.following_text`

### 4. Popup Opens and Accepts Text
- [ ] Click the IdeaShelf icon in the Chrome toolbar
- [ ] Popup opens with a text area and "Save" button
- [ ] Type or paste text into the text area
- [ ] Click "Save"
- [ ] Status shows "Saved to IdeaShelf!"
- [ ] Check `~/IdeaShelf/inbox/` for a new `.json` file
- [ ] Verify `content_type` is "quick_note"

### 5. Popup Pre-fills with Selected Text
- [ ] Select text on a web page
- [ ] Click the IdeaShelf icon
- [ ] The text area should be pre-filled with the selected text
- [ ] Click "Save" to capture it

### 6. Keyboard Shortcut Captures Selected Text
- [ ] Select text on a web page
- [ ] Press `Cmd+Shift+S` (Mac) or `Ctrl+Shift+S` (Windows/Linux)
- [ ] The popup should open (shortcut triggers popup action)
- [ ] The selected text should appear in the text area

### 7. Options Page Loads and Saves Settings
- [ ] Right-click the extension icon > "Options" (or go to extension details > "Extension options")
- [ ] Options page loads with:
  - Inbox path field (default: `~/IdeaShelf/inbox/`)
  - Keyboard shortcut display
  - Notification toggle
  - Auto-note toggle
- [ ] Change the notification toggle
- [ ] Click "Save Settings"
- [ ] Status shows "Settings saved."
- [ ] Reload the options page; setting should persist

### 8. Extension Works on Standard Web Pages
Test capture on each of these sites:
- [ ] Wikipedia article
- [ ] News site (e.g., BBC, NYT)
- [ ] GitHub README
- [ ] Google search results page
- [ ] Blog post

### 9. Extension Handles Unsupported Pages Gracefully
- [ ] Navigate to `chrome://extensions` or `chrome://settings`
- [ ] Try to right-click capture (no context menu should appear on these pages)
- [ ] Try clicking the extension icon and saving a quick note (should still work)

### 10. Rapid Captures All Succeed
- [ ] Select text on a page
- [ ] Perform 5 captures in rapid succession (context menu or popup)
- [ ] Check `~/IdeaShelf/inbox/` — there should be 5 distinct `.json` files
- [ ] Each file should have a unique `id`

## Troubleshooting

If captures fail silently:
1. Check `chrome://extensions` for errors on the IdeaShelf extension
2. Click "Inspect views: service worker" to see background script logs
3. Verify the native host is installed: check for `com.ideashelf.host.json` in
   `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`
4. Test the native host directly:
   ```bash
   echo '{"id":"test","captured_at":"2026-01-01T00:00:00Z","content_type":"test","content":"hello"}' | python3 native-host/ideashelf_host.py
   ```
   (Note: this won't work exactly as-is because native messaging uses a binary length prefix,
   but you can run the Python tests to verify the host logic.)
