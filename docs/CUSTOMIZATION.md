# IdeaShelf Customization Guide

## Changing the Output Folder

By default, processed ideas are written to `~/IdeaShelf/ideas/`. To change this:

1. Copy the example config to the IdeaShelf root:
   ```bash
   cp runtime/config.example.yaml ~/IdeaShelf/config.yaml
   ```

2. Edit `~/IdeaShelf/config.yaml`:
   ```yaml
   output_folder: ~/Documents/MyIdeas/
   ```

3. The inbox processor will use this path on its next run.

## Configuring Taxonomy

The taxonomy defines the categories the AI runtime uses when tagging your captures. Edit `~/IdeaShelf/config.yaml`:

```yaml
taxonomy:
  types:
    - metaphor
    - exercise
    - correction
    - concept
    - reference
    - positioning
    - example
    - insight
  categories:
    - ai-development
    - training
    - research
    - strategy
  themes:
    - scaffolding
    - architecture
    - leadership
```

The reference processor (`process_inbox.py`) doesn't perform AI-based tagging — it just demonstrates the file flow. When connected to Claude Code or another AI runtime, these taxonomy values guide the classification.

## Extension Settings

Open the extension options page:
- Right-click the IdeaShelf icon in Chrome > **Options**
- Or go to `chrome://extensions`, find IdeaShelf, click **Details** > **Extension options**

Available settings:

| Setting | Default | Description |
|---------|---------|-------------|
| Inbox folder path | `~/IdeaShelf/inbox/` | Where captures are saved (display only; the native host uses its own default) |
| Notifications | On | Show a toast when a capture succeeds |
| Auto-note prompt | Off | Prompt for a user note on each capture |

## Changing the Inbox Location

The inbox path is set in the native messaging host (`ideashelf_host.py`). To change it:

1. Edit `native-host/ideashelf_host.py`
2. Change the `DEFAULT_INBOX` variable:
   ```python
   DEFAULT_INBOX = os.path.expanduser("~/Documents/IdeaShelf/inbox/")
   ```
3. Re-run `install.sh` to update the native host registration

## Output File Format

Processed files use this structure:

```markdown
---
captured: 2026-02-27
source: https://example.com/article
source_title: Page Title
type: text_selection
themes: []
categories: []
status: raw
summary: First 100 characters of content...
---

# Title Inferred from Content

The captured text content here.

---
*User note: Any note you added during capture*
*Source: https://example.com/article*
```

## Connecting to Claude Code

To have Claude Code process your inbox automatically:

1. Set up a scheduled task or file watcher that triggers when new files appear in `~/IdeaShelf/inbox/`
2. The task should read the raw JSON, apply AI-based tagging using your taxonomy config, and write structured markdown to the output folder
3. The reference `process_inbox.py` shows the expected file flow — your Claude Code integration replaces it with intelligent processing

## Adding Custom Capture Types

The `content_type` field in captures currently supports:
- `text_selection` — text selected on a web page
- `quick_note` — text typed in the popup
- `bookmark` — page URL saved when no text is selected

To add custom types, modify the extension's `background.js` to detect and label new content patterns.
