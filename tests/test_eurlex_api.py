"""Tests for eurlex_api.py CLI flags."""
import subprocess
import sys


def test_get_document_json_flag_exists():
    result = subprocess.run(
        [sys.executable, "scripts/eurlex_api.py", "get-document", "--help"],
        capture_output=True, text=True,
        cwd="/Users/kpsfamily/코딩 프로젝트/general-legal-research",
    )
    assert "--json" in result.stdout


def test_get_document_save_flag_exists():
    result = subprocess.run(
        [sys.executable, "scripts/eurlex_api.py", "get-document", "--help"],
        capture_output=True, text=True,
        cwd="/Users/kpsfamily/코딩 프로젝트/general-legal-research",
    )
    assert "--save" in result.stdout


def test_search_no_save_flag():
    result = subprocess.run(
        [sys.executable, "scripts/eurlex_api.py", "search", "--help"],
        capture_output=True, text=True,
        cwd="/Users/kpsfamily/코딩 프로젝트/general-legal-research",
    )
    assert "--save" not in result.stdout


def test_search_title_no_save_flag():
    result = subprocess.run(
        [sys.executable, "scripts/eurlex_api.py", "search-title", "--help"],
        capture_output=True, text=True,
        cwd="/Users/kpsfamily/코딩 프로젝트/general-legal-research",
    )
    assert "--save" not in result.stdout
