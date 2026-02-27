#!/usr/bin/env python3
"""
IdeaShelf Inbox Processor (Reference Implementation)

Reads raw JSON captures from the inbox folder, generates structured
markdown files with YAML frontmatter, and moves processed files to
inbox/processed/.

This is a reference implementation to demonstrate the file flow.
The real intelligence comes from Claude Code or a compatible AI runtime
processing the inbox with proper inference for tagging and categorization.

No external dependencies. Python 3 stdlib only.
"""

import json
import os
import shutil
import sys
from datetime import datetime

# Try to load PyYAML if available, otherwise use a simple fallback
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

DEFAULT_CONFIG = {
    "output_folder": os.path.expanduser("~/IdeaShelf/ideas/"),
    "inbox_folder": os.path.expanduser("~/IdeaShelf/inbox/"),
    "taxonomy": {
        "types": [
            "metaphor", "exercise", "correction", "concept",
            "reference", "positioning", "example", "insight",
        ],
        "categories": [],
        "themes": [],
    },
    "defaults": {
        "status": "raw",
    },
}


def load_config(config_path=None):
    """Load config from YAML file, falling back to defaults."""
    config = dict(DEFAULT_CONFIG)

    if config_path is None:
        config_path = os.path.expanduser("~/IdeaShelf/config.yaml")

    if os.path.isfile(config_path):
        try:
            if HAS_YAML:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
            else:
                # Simple key: value parsing for the most common settings
                user_config = _parse_simple_yaml(config_path)

            if "output_folder" in user_config:
                config["output_folder"] = os.path.expanduser(user_config["output_folder"])
            if "inbox_folder" in user_config:
                config["inbox_folder"] = os.path.expanduser(user_config["inbox_folder"])
        except Exception:
            pass  # Use defaults on config parse failure

    return config


def _parse_simple_yaml(path):
    """Minimal YAML parser for top-level key: value pairs."""
    result = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                if value:
                    result[key] = value
    return result


def generate_summary(content):
    """Generate a simple summary: first 100 chars of content."""
    cleaned = content.strip().replace("\n", " ")
    if len(cleaned) > 100:
        return cleaned[:97] + "..."
    return cleaned


def generate_title(capture):
    """Generate a title from the capture content."""
    content = capture.get("content", "")
    content_type = capture.get("content_type", "")

    if content_type == "bookmark":
        return capture.get("source_title", "Bookmark")

    # Use first line or first ~60 chars as title
    first_line = content.strip().split("\n")[0]
    if len(first_line) > 60:
        return first_line[:57] + "..."
    return first_line or "Untitled Capture"


def generate_filename(capture):
    """Generate output filename: YYMMDD_description.md"""
    captured_at = capture.get("captured_at", "")
    try:
        dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
        date_prefix = dt.strftime("%y%m%d")
    except (ValueError, AttributeError):
        date_prefix = datetime.now().strftime("%y%m%d")

    # Create a slug from content
    content = capture.get("content", "untitled")
    slug = content.strip().split("\n")[0][:40]
    slug = "".join(c if c.isalnum() or c == " " else "" for c in slug)
    slug = slug.strip().replace(" ", "_").lower()
    if not slug:
        slug = "capture"

    return f"{date_prefix}_{slug}.md"


def build_markdown(capture, config):
    """Build a markdown file with YAML frontmatter from a capture."""
    content_type = capture.get("content_type", "unknown")
    source_url = capture.get("source_url", "")
    source_title = capture.get("source_title", "")
    content = capture.get("content", "")
    user_note = capture.get("user_note", "")
    captured_at = capture.get("captured_at", "")
    status = config.get("defaults", {}).get("status", "raw")

    title = generate_title(capture)
    summary = generate_summary(content)

    # Parse date for frontmatter
    try:
        dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
        captured_date = dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        captured_date = datetime.now().strftime("%Y-%m-%d")

    # Build YAML frontmatter
    lines = [
        "---",
        f"captured: {captured_date}",
        f"source: {source_url}",
        f"source_title: {source_title}",
        f"type: {content_type}",
        "themes: []",
        "categories: []",
        f"status: {status}",
        f"summary: {summary}",
        "---",
        "",
        f"# {title}",
        "",
        content,
    ]

    if user_note:
        lines.extend(["", f"---", f"*User note: {user_note}*"])

    if source_url:
        lines.extend(["", f"*Source: {source_url}*"])

    return "\n".join(lines) + "\n"


def process_inbox(config=None):
    """Process all JSON files in the inbox folder.

    Returns (processed_count, error_count).
    """
    if config is None:
        config = load_config()

    inbox_path = config.get("inbox_folder", DEFAULT_CONFIG["inbox_folder"])
    output_path = config.get("output_folder", DEFAULT_CONFIG["output_folder"])
    processed_path = os.path.join(inbox_path, "processed")

    # Ensure directories exist
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(processed_path, exist_ok=True)

    processed_count = 0
    error_count = 0

    if not os.path.isdir(inbox_path):
        return 0, 0

    for filename in sorted(os.listdir(inbox_path)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(inbox_path, filename)
        if not os.path.isfile(filepath):
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                capture = json.load(f)

            markdown = build_markdown(capture, config)
            out_filename = generate_filename(capture)

            # Avoid overwriting: append capture ID if file exists
            out_filepath = os.path.join(output_path, out_filename)
            if os.path.exists(out_filepath):
                base, ext = os.path.splitext(out_filename)
                capture_id = capture.get("id", "dup")[:8]
                out_filepath = os.path.join(output_path, f"{base}_{capture_id}{ext}")

            with open(out_filepath, "w", encoding="utf-8") as f:
                f.write(markdown)

            # Move processed JSON to processed/ subfolder
            shutil.move(filepath, os.path.join(processed_path, filename))
            processed_count += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}", file=sys.stderr)
            error_count += 1

    return processed_count, error_count


def main():
    config = load_config()
    processed, errors = process_inbox(config)

    print(f"IdeaShelf Inbox Processor")
    print(f"  Processed: {processed} items")
    if errors:
        print(f"  Errors:    {errors} items")
    if processed == 0 and errors == 0:
        print(f"  Inbox is empty. Nothing to process.")


if __name__ == "__main__":
    main()
