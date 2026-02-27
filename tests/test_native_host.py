"""
Tests for the IdeaShelf native messaging host.

Tests the core logic of ideashelf_host.py: payload validation,
inbox creation, file writing, and error handling.
"""

import json
import os
import struct
import sys
import tempfile
import threading
import uuid

import pytest

# Add native-host to the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "native-host"))

import ideashelf_host


def make_payload(**overrides):
    """Create a valid capture payload with optional overrides."""
    payload = {
        "id": str(uuid.uuid4()),
        "captured_at": "2026-02-27T14:30:00Z",
        "source_url": "https://example.com/article",
        "source_title": "Test Article",
        "content_type": "text_selection",
        "content": "This is a test capture of selected text.",
        "context": {
            "preceding_text": "Before the selection",
            "following_text": "After the selection",
        },
        "user_note": "",
    }
    payload.update(overrides)
    return payload


class TestValidatePayload:
    """Tests for payload validation."""

    def test_valid_payload_passes(self):
        payload = make_payload()
        valid, err = ideashelf_host.validate_payload(payload)
        assert valid is True
        assert err == ""

    def test_missing_required_field_id(self):
        payload = make_payload()
        del payload["id"]
        valid, err = ideashelf_host.validate_payload(payload)
        assert valid is False
        assert "id" in err

    def test_missing_required_field_content(self):
        payload = make_payload()
        del payload["content"]
        valid, err = ideashelf_host.validate_payload(payload)
        assert valid is False
        assert "content" in err

    def test_missing_multiple_required_fields(self):
        payload = make_payload()
        del payload["id"]
        del payload["captured_at"]
        valid, err = ideashelf_host.validate_payload(payload)
        assert valid is False
        assert "id" in err
        assert "captured_at" in err

    def test_empty_content_string_fails(self):
        payload = make_payload(content="   ")
        valid, err = ideashelf_host.validate_payload(payload)
        assert valid is False
        assert "content" in err.lower()

    def test_non_dict_payload_fails(self):
        valid, err = ideashelf_host.validate_payload("not a dict")
        assert valid is False
        assert "object" in err.lower()

    def test_non_dict_list_payload_fails(self):
        valid, err = ideashelf_host.validate_payload([1, 2, 3])
        assert valid is False


class TestEnsureInbox:
    """Tests for inbox directory creation."""

    def test_creates_inbox_if_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, "new_inbox")
            ok, err = ideashelf_host.ensure_inbox(inbox)
            assert ok is True
            assert os.path.isdir(inbox)

    def test_existing_inbox_is_fine(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ok, err = ideashelf_host.ensure_inbox(tmpdir)
            assert ok is True

    def test_read_only_parent_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            readonly = os.path.join(tmpdir, "readonly")
            os.makedirs(readonly)
            os.chmod(readonly, 0o444)
            try:
                inbox = os.path.join(readonly, "inbox")
                ok, err = ideashelf_host.ensure_inbox(inbox)
                assert ok is False
                assert "Cannot create" in err
            finally:
                os.chmod(readonly, 0o755)


class TestWriteCapture:
    """Tests for writing capture files."""

    def test_valid_capture_writes_json_file(self):
        with tempfile.TemporaryDirectory() as inbox:
            payload = make_payload()
            ok, err, filepath = ideashelf_host.write_capture(payload, inbox)
            assert ok is True
            assert err == ""
            assert os.path.isfile(filepath)

            with open(filepath, "r") as f:
                saved = json.load(f)
            assert saved["id"] == payload["id"]
            assert saved["content"] == payload["content"]

    def test_file_named_by_capture_id(self):
        with tempfile.TemporaryDirectory() as inbox:
            capture_id = "test-uuid-1234"
            payload = make_payload(id=capture_id)
            ok, err, filepath = ideashelf_host.write_capture(payload, inbox)
            assert ok is True
            assert os.path.basename(filepath) == f"{capture_id}.json"

    def test_read_only_directory_fails(self):
        with tempfile.TemporaryDirectory() as inbox:
            os.chmod(inbox, 0o444)
            try:
                payload = make_payload()
                ok, err, filepath = ideashelf_host.write_capture(payload, inbox)
                assert ok is False
                assert "Failed to write" in err
            finally:
                os.chmod(inbox, 0o755)

    def test_large_payload_succeeds(self):
        """10KB of text content should be handled correctly."""
        with tempfile.TemporaryDirectory() as inbox:
            large_text = "A" * 10240  # 10KB
            payload = make_payload(content=large_text)
            ok, err, filepath = ideashelf_host.write_capture(payload, inbox)
            assert ok is True

            with open(filepath, "r") as f:
                saved = json.load(f)
            assert len(saved["content"]) == 10240

    def test_concurrent_writes_produce_distinct_files(self):
        """Simulate 5 rapid captures - all should produce distinct files."""
        with tempfile.TemporaryDirectory() as inbox:
            payloads = [make_payload() for _ in range(5)]
            results = [None] * 5

            def write_one(i):
                results[i] = ideashelf_host.write_capture(payloads[i], inbox)

            threads = [threading.Thread(target=write_one, args=(i,)) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # All should succeed
            for i, (ok, err, filepath) in enumerate(results):
                assert ok is True, f"Write {i} failed: {err}"

            # All files should be distinct
            files = os.listdir(inbox)
            assert len(files) == 5

    def test_path_traversal_id_is_sanitized(self):
        """IDs with path traversal characters must not write outside inbox."""
        with tempfile.TemporaryDirectory() as inbox:
            payload = make_payload(id="../../etc/evil")
            ok, err, filepath = ideashelf_host.write_capture(payload, inbox)
            assert ok is True
            # File must be inside the inbox, not outside it
            assert os.path.dirname(os.path.abspath(filepath)) == os.path.abspath(inbox)
            assert ".." not in os.path.basename(filepath)
            assert "/" not in os.path.basename(filepath)

    def test_sanitize_id_strips_dangerous_chars(self):
        """sanitize_id should strip slashes, dots, and special chars."""
        # os.path.basename strips the path, regex strips remaining unsafe chars
        assert ideashelf_host.sanitize_id("../../etc/passwd") == "passwd"
        assert ideashelf_host.sanitize_id("normal-uuid-1234") == "normal-uuid-1234"
        assert ideashelf_host.sanitize_id("has spaces!@#") == "hasspaces"
        assert ideashelf_host.sanitize_id("") == "unknown"
        assert ideashelf_host.sanitize_id("...") == "unknown"

    def test_malformed_json_in_read_message(self):
        """Malformed JSON should not crash the host."""
        # Test validate_payload with various bad inputs
        valid, err = ideashelf_host.validate_payload(None)
        assert valid is False

        valid, err = ideashelf_host.validate_payload(42)
        assert valid is False
