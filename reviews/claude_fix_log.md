# Claude Fix Log — Post-Review Changes

All 6 items from the agreed punch list are implemented. 31/31 tests pass.

## Changes Made

### 1. Path Traversal Fix (native-host/ideashelf_host.py)
- Added `sanitize_id()` function: applies `os.path.basename()` then strips everything except `[a-zA-Z0-9\-_]`
- `write_capture()` now calls `sanitize_id()` before building the filename
- Added 2 new tests: `test_path_traversal_id_is_sanitized` and `test_sanitize_id_strips_dangerous_chars`
- `"../../etc/passwd"` → basename gives `"passwd"` → regex keeps `"passwd"` → file stays in inbox. No traversal possible.

### 2. Removed Fake Inbox Path Setting (extension/options/)
- Removed the editable text input for inbox path from `options.html`
- Replaced with a read-only display showing `~/IdeaShelf/inbox/` and a hint that says to edit `DEFAULT_INBOX` in the host script to change it
- Cleaned out `inboxPath` from `options.js` defaults and save logic

### 3. Removed Dead `onCommand` Listener (extension/background.js)
- Deleted the `chrome.commands.onCommand` listener entirely
- Added a comment explaining that `_execute_action` opens the popup when `default_popup` is set
- Updated README capture methods table: shortcut now says "opens popup with selected text pre-filled"
- Updated options.html shortcut hint to say "Opens the capture popup"

### 4. Added 5-Second Native Messaging Timeout (extension/background.js)
- `sendToNativeHost()` now sets a `setTimeout` that fires after 5 seconds
- On timeout: calls callback with `{ success: false, error: "Native host timed out" }`, disconnects port
- Uses a `responded` flag to prevent double-callback from timeout + normal response racing
- Both context menu and popup flows get timeout protection (they both go through `sendToNativeHost`)

### 5. Removed `autoNote` Setting (extension/options/)
- Removed the toggle from `options.html`
- Removed from `options.js` defaults and save logic
- Will add back in v0.2 when the capture flow actually implements the prompt behavior

### 6. Added `capture_method` to Payload (extension/background.js, popup/popup.js)
- `buildPayload()` now accepts and includes `capture_method` field
- Context menu captures: `"context_menu"`
- Popup captures: `"popup"`
- Field propagates into the JSON written to inbox

## Test Results
```
31 passed in 0.03s
```

New tests added:
- `test_path_traversal_id_is_sanitized` — verifies traversal IDs stay inside inbox
- `test_sanitize_id_strips_dangerous_chars` — unit tests for the sanitize function

## Files Modified
- `native-host/ideashelf_host.py` — added `re` import, `sanitize_id()`, updated `write_capture()`
- `extension/background.js` — removed `onCommand`, added timeout, added `capture_method`
- `extension/popup/popup.js` — added `captureMethod: "popup"` to message
- `extension/options/options.html` — removed inbox path input, removed autoNote toggle, added read-only inbox display
- `extension/options/options.js` — simplified to notifications-only settings
- `tests/test_native_host.py` — added 2 security tests
- `README.md` — corrected shortcut description

---

Codex — if Woody wants you to re-review, the above is the full diff summary. The path traversal fix is the most security-relevant change. Everything else is cleanup.

— Claude
