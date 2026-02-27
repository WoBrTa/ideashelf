#!/usr/bin/env python3
"""
IdeaShelf Native Messaging Host

Receives JSON capture payloads from the Chrome extension via the native
messaging protocol (4-byte length prefix + JSON) and writes them as
individual .json files to the inbox folder.

No external dependencies. Python 3 stdlib only.
"""

import json
import os
import re
import struct
import sys

DEFAULT_INBOX = os.path.expanduser("~/IdeaShelf/inbox/")

REQUIRED_FIELDS = ["id", "captured_at", "content_type", "content"]


def read_message():
    """Read a native messaging message from stdin.

    Chrome native messaging protocol: 4-byte unsigned int (little-endian)
    indicating message length, followed by the JSON-encoded message.
    """
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length or len(raw_length) < 4:
        return None

    message_length = struct.unpack("<I", raw_length)[0]
    if message_length == 0:
        return None

    # Safety limit: reject messages over 1 MB
    if message_length > 1_048_576:
        return None

    raw_message = sys.stdin.buffer.read(message_length)
    if len(raw_message) < message_length:
        return None

    return json.loads(raw_message.decode("utf-8"))


def send_message(msg):
    """Send a native messaging response back to Chrome."""
    encoded = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def validate_payload(payload):
    """Validate that the capture payload contains required fields.

    Returns (is_valid, error_message).
    """
    if not isinstance(payload, dict):
        return False, "Payload must be a JSON object"

    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    if not isinstance(payload["content"], str) or not payload["content"].strip():
        return False, "Field 'content' must be a non-empty string"

    return True, ""


def ensure_inbox(inbox_path):
    """Create the inbox directory if it does not exist.

    Returns (success, error_message).
    """
    try:
        os.makedirs(inbox_path, exist_ok=True)
        return True, ""
    except OSError as e:
        return False, f"Cannot create inbox directory: {e}"


def sanitize_id(raw_id):
    """Sanitize a capture ID for safe use as a filename.

    Strips path separators and any characters that aren't alphanumeric,
    hyphens, or underscores. Prevents path traversal attacks.
    """
    safe = os.path.basename(str(raw_id))
    safe = re.sub(r"[^a-zA-Z0-9\-_]", "", safe)
    return safe or "unknown"


def write_capture(payload, inbox_path):
    """Write the capture payload as a JSON file in the inbox.

    Returns (success, error_message, filepath).
    """
    capture_id = sanitize_id(payload.get("id", "unknown"))
    filename = f"{capture_id}.json"
    filepath = os.path.join(inbox_path, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return True, "", filepath
    except OSError as e:
        return False, f"Failed to write file: {e}", ""


def get_inbox_path():
    """Determine the inbox path. Could be extended to read from config."""
    return DEFAULT_INBOX


def main():
    """Main loop: read one message, process it, respond, and exit.

    Native messaging hosts are launched per-connection by Chrome.
    """
    try:
        payload = read_message()
    except json.JSONDecodeError:
        send_message({"success": False, "error": "Invalid JSON in message"})
        return
    except Exception as e:
        send_message({"success": False, "error": f"Read error: {e}"})
        return

    if payload is None:
        send_message({"success": False, "error": "No message received"})
        return

    # Validate
    valid, err = validate_payload(payload)
    if not valid:
        send_message({"success": False, "error": err})
        return

    # Ensure inbox exists
    inbox_path = get_inbox_path()
    ok, err = ensure_inbox(inbox_path)
    if not ok:
        send_message({"success": False, "error": err})
        return

    # Write capture
    ok, err, filepath = write_capture(payload, inbox_path)
    if not ok:
        send_message({"success": False, "error": err})
        return

    send_message({
        "success": True,
        "id": payload.get("id"),
        "path": filepath,
    })


if __name__ == "__main__":
    main()
