# IdeaShelf Setup Guide

Step-by-step instructions to install and configure IdeaShelf on macOS.

## Prerequisites

- Google Chrome browser
- Python 3.6+ (pre-installed on macOS or via Homebrew)
- A terminal app (Terminal.app or iTerm2)

## Step 1: Clone the Repository

```bash
git clone https://github.com/WoBrTa/ideashelf.git
cd ideashelf
```

## Step 2: Load the Chrome Extension

1. Open Chrome and navigate to `chrome://extensions`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder inside the cloned repository
5. The IdeaShelf icon (blue lightbulb) should appear in your Chrome toolbar
6. **Copy the Extension ID** shown under the extension name — you'll need this next

## Step 3: Install the Native Messaging Host

The native messaging host is a small Python script that allows the Chrome extension to write files to your local filesystem.

```bash
cd native-host
chmod +x install.sh
./install.sh YOUR_EXTENSION_ID
```

Replace `YOUR_EXTENSION_ID` with the ID you copied from Step 2.

This script will:
- Register the native messaging host with Chrome
- Make the host script executable
- Create the default inbox directory at `~/IdeaShelf/inbox/`

## Step 4: Test the Installation

1. Navigate to any web page in Chrome
2. Select some text
3. Right-click and choose **"Save to IdeaShelf"**
4. Check `~/IdeaShelf/inbox/` — you should see a new `.json` file

```bash
ls ~/IdeaShelf/inbox/
```

## Step 5: Process the Inbox (Optional)

The reference inbox processor converts raw JSON captures into markdown files:

```bash
python3 runtime/process_inbox.py
```

This will:
- Read all `.json` files from `~/IdeaShelf/inbox/`
- Generate markdown files with YAML frontmatter in `~/IdeaShelf/ideas/`
- Move processed JSON to `~/IdeaShelf/inbox/processed/`

## Configuring the Keyboard Shortcut

The default shortcut is `Cmd+Shift+S` (Mac) / `Ctrl+Shift+S` (others).

To change it:
1. Go to `chrome://extensions/shortcuts`
2. Find IdeaShelf
3. Click the pencil icon next to the shortcut
4. Press your preferred key combination

## Uninstalling

To remove the native messaging host:

```bash
cd native-host
./uninstall.sh
```

To remove the extension:
1. Go to `chrome://extensions`
2. Find IdeaShelf and click **Remove**

Your captured data in `~/IdeaShelf/` is preserved — delete it manually if you want a clean removal.

## Troubleshooting

### Captures fail silently
1. Check `chrome://extensions` for errors on IdeaShelf
2. Click "Inspect views: service worker" to see console logs
3. Verify the native host manifest exists:
   ```bash
   cat ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.ideashelf.host.json
   ```
4. Ensure the path in the manifest points to your `ideashelf_host.py`

### "Native host has exited" error
- Make sure `ideashelf_host.py` is executable: `chmod +x native-host/ideashelf_host.py`
- Verify Python 3 is available: `python3 --version`
- Check the shebang line matches your Python path

### Context menu doesn't appear
- The context menu only appears when text is selected
- It won't appear on `chrome://` pages (browser internal pages)
- Try reloading the extension from `chrome://extensions`
