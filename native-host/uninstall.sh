#!/bin/bash
#
# IdeaShelf Native Messaging Host Uninstaller (macOS)
#
# Removes the native messaging host manifest from Chrome.
# Does NOT delete the inbox folder or any captured data.
#

set -e

HOST_NAME="com.ideashelf.host"
CHROME_NMH_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
MANIFEST_PATH="$CHROME_NMH_DIR/$HOST_NAME.json"

echo "=== IdeaShelf Native Host Uninstaller ==="
echo ""

if [ -f "$MANIFEST_PATH" ]; then
    rm "$MANIFEST_PATH"
    echo "[OK] Removed native messaging manifest"
else
    echo "[--] No manifest found at $MANIFEST_PATH (already uninstalled?)"
fi

echo ""
echo "Uninstall complete."
echo "Note: Your captured data in ~/IdeaShelf/ has NOT been deleted."
echo "      Remove the extension from chrome://extensions manually."
