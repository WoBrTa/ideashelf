# IdeaShelf Re-Review — Post-Fix Verification

**BLUF:** The six fixes listed in Claude’s log are implemented and do address the original problems I flagged. The security issue (path traversal) is resolved, the misleading settings are removed, shortcut behavior is now documented correctly, and a native-host timeout prevents indefinite hangs. One minor note: `capture_method` is now present but does not distinguish “shortcut-opened popup” vs. “icon-opened popup” (both resolve to `popup`), which is acceptable for v0.1 but worth noting if you want that granularity later.

---

## Fix-by-Fix Verification

### 1. Path Traversal Fix — **Resolved**
**Where:** `native-host/ideashelf_host.py`
- `sanitize_id()` now applies `os.path.basename()` and strips non `[A-Za-z0-9_-]` chars.
- `write_capture()` uses `sanitize_id()` before forming the filename.
- Tests added in `tests/test_native_host.py` confirm traversal inputs stay inside inbox.
**Outcome:** This closes the path traversal risk I flagged.

**Minor residual note:** If `id` sanitizes to empty, it becomes `"unknown"`, so repeated invalid IDs could overwrite the same file. In practice, extension-generated UUIDs avoid this, so it’s low risk.

### 2. Fake Inbox Path Setting Removed — **Resolved**
**Where:** `extension/options/options.html`, `extension/options/options.js`
- Editable inbox path field removed.
- Options page now shows a read-only inbox location and tells users to edit `DEFAULT_INBOX` in `ideashelf_host.py`.
- Storage defaults and save logic now only handle `notifications`.
**Outcome:** The UI no longer lies about a setting that doesn’t work.

### 3. Dead `onCommand` Listener Removed — **Resolved**
**Where:** `extension/background.js`
- The `chrome.commands.onCommand` listener is gone.
- Comment explains that `_execute_action` opens the popup when `default_popup` is set.
- `README.md` updated to clarify shortcut opens the popup.
**Outcome:** Dead code removed and documentation matches behavior.

### 4. 5-Second Native Messaging Timeout — **Resolved**
**Where:** `extension/background.js`
- `sendToNativeHost()` now has a 5s timeout with a guarded callback to prevent double-response.
- Both context menu and popup flows run through this path, so both gain timeout protection.
**Outcome:** The “hang forever” failure mode is removed; users now get a failure response if the host stalls.

### 5. `autoNote` Setting Removed — **Resolved**
**Where:** `extension/options/options.html`, `extension/options/options.js`
- Toggle removed from UI and storage.
**Outcome:** Dead setting eliminated; no more user confusion.

### 6. `capture_method` Added — **Resolved (with minor scope note)**
**Where:** `extension/background.js`, `extension/popup/popup.js`
- Payload now includes `capture_method`.
- Values currently used: `"context_menu"` and `"popup"`.
**Outcome:** This fixes the missing metadata. Shortcut-triggered captures still go through popup and are labeled `popup`, which is reasonable for v0.1. If you later want to differentiate “shortcut-opened popup” vs “clicked popup,” you’ll need to add state in the popup trigger flow.

---

## Test Status
Claude reports 31/31 tests passing and added two tests for sanitization. I did **not** re-run tests locally in this pass.

---

## Summary Judgment
All six fixes are present and address the original issues. No new regressions were visible in the changed files. The only remaining gap worth tracking for v0.2 is optional granularity for `capture_method` on shortcut-opened popups; otherwise, the fixes are solid.
