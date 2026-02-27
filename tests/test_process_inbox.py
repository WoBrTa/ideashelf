"""
Tests for the IdeaShelf inbox processor (reference implementation).

Tests the core logic of process_inbox.py: markdown generation,
frontmatter formatting, file movement, and config handling.
"""

import json
import os
import sys
import tempfile
import uuid

import pytest

# Add runtime to the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

import process_inbox


def make_capture(**overrides):
    """Create a valid capture dict with optional overrides."""
    capture = {
        "id": str(uuid.uuid4()),
        "captured_at": "2026-02-27T14:30:00Z",
        "source_url": "https://example.com/article",
        "source_title": "Test Article Title",
        "content_type": "text_selection",
        "content": "This is a test capture for processing.",
        "context": {
            "preceding_text": "Before",
            "following_text": "After",
        },
        "user_note": "",
    }
    capture.update(overrides)
    return capture


def write_capture_to_inbox(capture, inbox_path):
    """Write a capture dict as a JSON file in the inbox."""
    filename = f"{capture['id']}.json"
    filepath = os.path.join(inbox_path, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(capture, f, indent=2)
    return filepath


class TestBuildMarkdown:
    """Tests for markdown generation."""

    def test_valid_capture_produces_markdown_with_frontmatter(self):
        capture = make_capture()
        config = process_inbox.DEFAULT_CONFIG
        md = process_inbox.build_markdown(capture, config)

        assert md.startswith("---\n")
        assert "captured: 2026-02-27" in md
        assert "source: https://example.com/article" in md
        assert "source_title: Test Article Title" in md
        assert "type: text_selection" in md
        assert "status: raw" in md
        assert "This is a test capture for processing." in md

    def test_user_note_included_when_present(self):
        capture = make_capture(user_note="Important insight")
        config = process_inbox.DEFAULT_CONFIG
        md = process_inbox.build_markdown(capture, config)

        assert "Important insight" in md

    def test_source_url_included_at_bottom(self):
        capture = make_capture()
        config = process_inbox.DEFAULT_CONFIG
        md = process_inbox.build_markdown(capture, config)

        assert "*Source: https://example.com/article*" in md

    def test_missing_optional_fields_still_work(self):
        """JSON missing context and user_note should process cleanly."""
        capture = {
            "id": str(uuid.uuid4()),
            "captured_at": "2026-02-27T14:30:00Z",
            "source_url": "",
            "source_title": "",
            "content_type": "quick_note",
            "content": "Just a quick thought.",
        }
        config = process_inbox.DEFAULT_CONFIG
        md = process_inbox.build_markdown(capture, config)

        assert "---\n" in md
        assert "Just a quick thought." in md
        assert "type: quick_note" in md


class TestGenerateFilename:
    """Tests for output filename generation."""

    def test_filename_starts_with_date_prefix(self):
        capture = make_capture(captured_at="2026-02-27T14:30:00Z")
        filename = process_inbox.generate_filename(capture)
        assert filename.startswith("260227_")

    def test_filename_ends_with_md(self):
        capture = make_capture()
        filename = process_inbox.generate_filename(capture)
        assert filename.endswith(".md")

    def test_filename_has_slug_from_content(self):
        capture = make_capture(content="Machine learning fundamentals")
        filename = process_inbox.generate_filename(capture)
        assert "machine_learning" in filename


class TestProcessInbox:
    """Tests for the full inbox processing flow."""

    def test_valid_json_produces_markdown_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "inbox")
            output = os.path.join(tmpdir, "ideas")
            os.makedirs(inbox)

            capture = make_capture()
            write_capture_to_inbox(capture, inbox)

            config = {
                "inbox_folder": inbox,
                "output_folder": output,
                "defaults": {"status": "raw"},
            }
            processed, errors = process_inbox.process_inbox(config)

            assert processed == 1
            assert errors == 0

            # Check output file exists
            output_files = os.listdir(output)
            assert len(output_files) == 1
            assert output_files[0].endswith(".md")

            # Check content
            with open(os.path.join(output, output_files[0]), "r") as f:
                content = f.read()
            assert "This is a test capture" in content

    def test_processed_json_moved_to_processed_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "inbox")
            output = os.path.join(tmpdir, "ideas")
            os.makedirs(inbox)

            capture = make_capture()
            write_capture_to_inbox(capture, inbox)

            config = {
                "inbox_folder": inbox,
                "output_folder": output,
                "defaults": {"status": "raw"},
            }
            process_inbox.process_inbox(config)

            # Original JSON should be gone from inbox
            inbox_jsons = [f for f in os.listdir(inbox) if f.endswith(".json")]
            assert len(inbox_jsons) == 0

            # Should be in processed/
            processed_dir = os.path.join(inbox, "processed")
            assert os.path.isdir(processed_dir)
            processed_files = os.listdir(processed_dir)
            assert len(processed_files) == 1
            assert processed_files[0] == f"{capture['id']}.json"

    def test_empty_inbox_produces_no_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "inbox")
            output = os.path.join(tmpdir, "ideas")
            os.makedirs(inbox)

            config = {
                "inbox_folder": inbox,
                "output_folder": output,
                "defaults": {"status": "raw"},
            }
            processed, errors = process_inbox.process_inbox(config)

            assert processed == 0
            assert errors == 0

    def test_missing_optional_fields_still_process(self):
        """Captures without context or user_note should process cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "inbox")
            output = os.path.join(tmpdir, "ideas")
            os.makedirs(inbox)

            capture = {
                "id": str(uuid.uuid4()),
                "captured_at": "2026-02-27T14:30:00Z",
                "source_url": "",
                "source_title": "",
                "content_type": "quick_note",
                "content": "Minimal capture",
            }
            write_capture_to_inbox(capture, inbox)

            config = {
                "inbox_folder": inbox,
                "output_folder": output,
                "defaults": {"status": "raw"},
            }
            processed, errors = process_inbox.process_inbox(config)

            assert processed == 1
            assert errors == 0

    def test_config_output_folder_is_respected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "inbox")
            custom_output = os.path.join(tmpdir, "custom_output")
            os.makedirs(inbox)

            capture = make_capture()
            write_capture_to_inbox(capture, inbox)

            config = {
                "inbox_folder": inbox,
                "output_folder": custom_output,
                "defaults": {"status": "raw"},
            }
            process_inbox.process_inbox(config)

            assert os.path.isdir(custom_output)
            output_files = os.listdir(custom_output)
            assert len(output_files) == 1

    def test_multiple_json_files_all_processed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "inbox")
            output = os.path.join(tmpdir, "ideas")
            os.makedirs(inbox)

            for i in range(6):
                capture = make_capture(content=f"Capture number {i}")
                write_capture_to_inbox(capture, inbox)

            config = {
                "inbox_folder": inbox,
                "output_folder": output,
                "defaults": {"status": "raw"},
            }
            processed, errors = process_inbox.process_inbox(config)

            assert processed == 6
            assert errors == 0

            output_files = os.listdir(output)
            assert len(output_files) == 6
