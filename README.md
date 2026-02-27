# IdeaShelf

Frictionless idea capture from anywhere in the browser to a structured local knowledge system.

IdeaShelf is a Chrome extension that catches text, links, and quick notes from your browser and writes them as structured JSON files to a local inbox folder. A separate local AI runtime (like Claude Code) processes the inbox and files tagged ideas — keeping capture fast and intelligence local.

## Architecture

```
[Chrome Extension]            [Local AI Runtime]
      |                              |
      |  captures content            |  watches inbox folder
      |  writes to inbox/            |  reads raw captures
      |                              |  runs inference for tagging
      |                              |  writes structured .md files
      |                              |  to output folder
      v                              v
  ~/IdeaShelf/inbox/          ~/IdeaShelf/ideas/
  (raw JSON captures)         (tagged markdown files)
```

The extension handles capture only — no API calls, no authentication, no network requests. The intelligence layer runs locally and is pluggable.

## Quick Start

### 1. Load the Extension

```bash
git clone https://github.com/WoBrTa/ideashelf.git
cd ideashelf
```

1. Open `chrome://extensions` in Chrome
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` folder
4. Copy the **Extension ID** shown under the extension name

### 2. Install the Native Messaging Host

```bash
cd native-host
./install.sh YOUR_EXTENSION_ID
```

### 3. Capture Something

- Select text on any web page
- Right-click > **Save to IdeaShelf**
- Check `~/IdeaShelf/inbox/` for the captured JSON

## Capture Methods

| Method | How | Content Type |
|--------|-----|-------------|
| Context menu | Select text, right-click > "Save to IdeaShelf" | `text_selection` |
| Popup | Click extension icon, type/paste, click Save | `quick_note` |
| Keyboard shortcut | `Cmd+Shift+S` (Mac) / `Ctrl+Shift+S` — opens popup with selected text pre-filled | `quick_note` |

## Project Structure

```
ideashelf/
├── extension/           # Chrome extension (Manifest V3)
│   ├── manifest.json
│   ├── background.js    # Service worker
│   ├── content.js       # Content script
│   ├── popup/           # Capture UI
│   ├── options/         # Settings page
│   └── icons/
├── native-host/         # Native messaging host (Python)
│   ├── ideashelf_host.py
│   ├── install.sh       # macOS installer
│   └── uninstall.sh
├── runtime/             # Reference inbox processor
│   ├── process_inbox.py
│   └── config.example.yaml
├── tests/               # Unit tests + manual test plan
└── docs/                # Setup and customization guides
```

## Configuration

Copy the example config and customize:

```bash
cp runtime/config.example.yaml ~/IdeaShelf/config.yaml
```

Edit `~/IdeaShelf/config.yaml` to set your output folder and taxonomy. See [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md) for details.

## Running the Reference Processor

```bash
python3 runtime/process_inbox.py
```

This converts raw JSON captures into markdown files with YAML frontmatter. It's a reference implementation — connect Claude Code or your preferred AI runtime for intelligent tagging.

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

For manual extension testing, see [tests/test_extension/manual_test_plan.md](tests/test_extension/manual_test_plan.md).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes and add tests
4. Run the test suite (`python -m pytest tests/ -v`)
5. Commit and push
6. Open a pull request

## Known Limitations (v0.1)

- macOS only for the native messaging host
- No drag-and-drop capture (planned for v0.2)
- No image capture (planned for v0.3)
- Runtime processor is a reference implementation only

## License

MIT License. See [LICENSE](LICENSE).
