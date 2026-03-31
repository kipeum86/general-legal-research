"""Tests for library-ingest.py kordoc integration helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "library-ingest.py"
SPEC = importlib.util.spec_from_file_location("library_ingest", MODULE_PATH)
library_ingest = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(library_ingest)


def test_hwp_extensions_are_supported():
    """HWP and HWPX should be routed through kordoc, not rejected."""
    assert ".hwp" in library_ingest.SUPPORTED_EXTENSIONS
    assert ".hwpx" in library_ingest.SUPPORTED_EXTENSIONS
    assert ".hwp" in library_ingest.KORDOC_EXTENSIONS
    assert ".hwpx" in library_ingest.KORDOC_EXTENSIONS


def test_build_kordoc_command_uses_json_output():
    """kordoc CLI should be invoked in machine-readable JSON mode."""
    src = Path("/tmp/sample.hwpx")
    command = library_ingest._build_kordoc_command(
        "npx -y -p kordoc -p pdfjs-dist kordoc",
        src,
    )

    assert command[:7] == ["npx", "-y", "-p", "kordoc", "-p", "pdfjs-dist", "kordoc"]
    assert command[7] == str(src)
    assert command[8:] == ["--format", "json", "--silent"]


def test_parse_kordoc_json_success_payload():
    """Successful kordoc output should be returned as a parsed dict."""
    stdout = """
    {
      "success": true,
      "fileType": "hwpx",
      "markdown": "# Title\\n\\nBody text long enough to count as content.",
      "warnings": [{"code": "SKIPPED_IMAGE", "message": "Image skipped"}]
    }
    """

    payload = library_ingest._parse_kordoc_json(stdout, "", 0)

    assert payload["success"] is True
    assert payload["fileType"] == "hwpx"
    assert "Body text" in payload["markdown"]


def test_parse_kordoc_json_failure_surfaces_error_code():
    """Failure payloads should raise a useful RuntimeError."""
    stdout = """
    {
      "success": false,
      "fileType": "hwp",
      "error": "DRM protected file",
      "code": "DRM_PROTECTED"
    }
    """

    with pytest.raises(RuntimeError, match="DRM_PROTECTED"):
        library_ingest._parse_kordoc_json(stdout, "", 1)


def test_build_parser_notes_includes_warning_summary():
    """kordoc parser notes should preserve warning details next to the Markdown."""
    payload = {
        "fileType": "hwpx",
        "metadata": {"creator": "Hancom Office", "pageCount": 12},
        "warnings": [
            {"code": "SKIPPED_IMAGE", "message": "Image skipped", "page": 3},
        ],
    }

    notes = library_ingest._build_parser_notes("kordoc", payload)

    assert "Parser: kordoc" in notes
    assert "Detected file type: hwpx" in notes
    assert "Creator: Hancom Office" in notes
    assert "Page count: 12" in notes
    assert "Warning [SKIPPED_IMAGE]: page 3, Image skipped" in notes
