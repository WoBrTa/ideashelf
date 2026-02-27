# IdeaShelf Code Review Assignment

You are reviewing a Chrome extension project called IdeaShelf, built by Claude (Opus 4.6) in a single session from a PRD. The project lives at `~/dev/ideashelf/`. Read every file before you start writing.

**When you're done, write your full report to:**
```
~/dev/ideashelf/reviews/codex_report.md
```

Woody will hand that file to Claude so they can read your feedback. Make it count.

---

## What the Project Is

A Chrome extension (Manifest V3) that captures selected text, quick notes, and bookmarks from the browser. It sends captures to a Python native messaging host that writes structured JSON files to `~/IdeaShelf/inbox/`. A reference runtime (`runtime/process_inbox.py`) converts those JSON files into tagged markdown. The extension does zero AI work — that's left to a local runtime (Claude Code) to handle later.

## Your Job

### Part 1: Read and Grade Every File

Go through the project file by file. For each one, give a letter grade (A-F) and a short explanation. Here's the file list:

**Extension:**
- `extension/manifest.json`
- `extension/background.js`
- `extension/content.js`
- `extension/popup/popup.html`, `popup.js`, `popup.css`
- `extension/options/options.html`, `options.js`, `options.css`

**Native Host:**
- `native-host/ideashelf_host.py`
- `native-host/install.sh`
- `native-host/uninstall.sh`
- `native-host/com.ideashelf.host.json`

**Runtime:**
- `runtime/process_inbox.py`
- `runtime/config.example.yaml`

**Tests:**
- `tests/test_native_host.py`
- `tests/test_process_inbox.py`
- `tests/test_extension/manual_test_plan.md`

**Docs/Config:**
- `README.md`
- `docs/SETUP.md`
- `docs/CUSTOMIZATION.md`
- `.github/workflows/test.yml`
- `.gitignore`
- `LICENSE`

### Part 2: Run the Tests

```bash
cd ~/dev/ideashelf
python3 -m pytest tests/ -v
```

Report results. If anything fails, explain why.

### Part 3: Trace the Context Menu Capture Flow

Walk through this end-to-end by reading the actual code:

1. User selects text on a webpage, right-clicks, picks "Save to IdeaShelf"
2. `background.js` handles the context menu click
3. `background.js` messages `content.js` to get selection + context
4. `content.js` extracts selected text, preceding 50 chars, following 50 chars, URL, title
5. `background.js` builds the capture payload (UUID, timestamp, content, metadata)
6. `background.js` sends payload via `chrome.runtime.connectNative`
7. `ideashelf_host.py` reads the native messaging protocol (4-byte length prefix + JSON)
8. Host validates, writes `{id}.json` to `~/IdeaShelf/inbox/`
9. Host responds with success
10. `background.js` shows a Chrome notification

At each step: Does the code actually do this correctly? Where could it fail?

### Part 4: Trace the Popup Capture Flow

1. User clicks extension icon, popup opens
2. `popup.js` queries active tab, asks `content.js` for selected text to pre-fill
3. User types/edits text, clicks Save (or Cmd+Enter)
4. `popup.js` sends message to `background.js`
5. `background.js` forwards to native host
6. Host writes file, responds
7. Popup shows "Saved!" then auto-closes after 1.2 seconds

Same question: Does the code do this? Where could it break?

### Part 5: Bug Hunt

Look specifically for these:

- **Security:** Can a malicious page inject into captures? Path traversal in the host? XSS in popup?
- **The keyboard shortcut problem:** `_execute_action` with a `default_popup` set — in Manifest V3, does `chrome.commands.onCommand` fire, or does it just open the popup? Is the `onCommand` listener in `background.js` dead code?
- **Race conditions:** Chrome spawns a new native host process per `connectNative()` call. What happens with 10 rapid captures?
- **Silent failures:** Places where errors are caught/ignored and the user gets zero feedback
- **Service worker lifecycle:** Will the context menu registration survive the service worker going idle and restarting?
- **The inbox path disconnect:** The options page shows an inbox path setting, but `ideashelf_host.py` uses a hardcoded `DEFAULT_INBOX`. The setting is cosmetic. Is that documented?

### Part 6: Architecture Opinion

- Is file-based IPC (extension → native host → JSON files → runtime) the right call?
- Is the capture payload missing anything useful?
- Would you structure the project differently?
- What's the biggest design risk for v0.2+?

### Part 7: Final Verdict

Format this section like:

```
OVERALL GRADE: [letter]

TOP 3 ISSUES:
1. ...
2. ...
3. ...

TOP 3 THINGS DONE WELL:
1. ...
2. ...
3. ...

WILL IT WORK OUT OF THE BOX: [Yes/No/Mostly] — [explanation]
```

---

## Ground Rules

- **Read the actual code.** Don't infer from filenames.
- Be direct. Don't pad with filler praise.
- If Claude did something well, say so specifically. If something is bad, say why and what the fix is.
- Write the report to `~/dev/ideashelf/reviews/codex_report.md` when done.
- Claude will read your report and probably have opinions. That's the point.

Go.
