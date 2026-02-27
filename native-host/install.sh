#!/bin/bash
#
# IdeaShelf Native Messaging Host Installer (macOS)
#
# Registers the native messaging host with Chrome so the extension
# can communicate with the local Python host script.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOST_NAME="com.ideashelf.host"
HOST_SCRIPT="$SCRIPT_DIR/ideashelf_host.py"
MANIFEST_TEMPLATE="$SCRIPT_DIR/$HOST_NAME.json"

# Chrome native messaging host directory on macOS
CHROME_NMH_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"

echo "=== IdeaShelf Native Host Installer ==="
echo ""

# Check that the host script exists
if [ ! -f "$HOST_SCRIPT" ]; then
    echo "ERROR: Cannot find $HOST_SCRIPT"
    exit 1
fi

# Make the host script executable
chmod +x "$HOST_SCRIPT"
echo "[OK] Made ideashelf_host.py executable"

# Create the Chrome NMH directory if needed
mkdir -p "$CHROME_NMH_DIR"
echo "[OK] Native messaging directory ready"

# Get the extension ID from the user or use placeholder
EXTENSION_ID="${1:-}"
if [ -z "$EXTENSION_ID" ]; then
    echo ""
    echo "NOTE: You need your Chrome extension ID to complete setup."
    echo "  1. Load the extension in chrome://extensions (developer mode)"
    echo "  2. Copy the extension ID shown under the extension name"
    echo "  3. Re-run this script with the ID:"
    echo "     ./install.sh YOUR_EXTENSION_ID"
    echo ""
    echo "For now, installing with a placeholder. You can re-run later."
    EXTENSION_ID="EXTENSION_ID_PLACEHOLDER"
fi

# Write the native messaging manifest with correct paths
cat > "$CHROME_NMH_DIR/$HOST_NAME.json" << EOF
{
  "name": "$HOST_NAME",
  "description": "IdeaShelf native messaging host for local file writes",
  "path": "$HOST_SCRIPT",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://$EXTENSION_ID/"
  ]
}
EOF

echo "[OK] Installed native messaging manifest to:"
echo "     $CHROME_NMH_DIR/$HOST_NAME.json"

# Create default inbox directory
INBOX_DIR="$HOME/IdeaShelf/inbox"
mkdir -p "$INBOX_DIR"
echo "[OK] Created inbox directory: $INBOX_DIR"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "  1. Load the extension in Chrome (chrome://extensions, developer mode)"
echo "  2. If you haven't already, re-run with your extension ID:"
echo "     ./install.sh YOUR_EXTENSION_ID"
echo "  3. Test by right-clicking selected text and choosing 'Save to IdeaShelf'"
echo "  4. Check ~/IdeaShelf/inbox/ for captured JSON files"
