"""Tests for open_law_api.py CLI flags (--json, --save)."""
import subprocess
import sys


CWD = "/Users/kpsfamily/코딩 프로젝트/general-legal-research"


def _run_help(subcommand: str) -> str:
    """Run a subcommand with --help and return stdout."""
    result = subprocess.run(
        [sys.executable, "scripts/open_law_api.py", subcommand, "--help"],
        capture_output=True, text=True,
        cwd=CWD,
    )
    return result.stdout


def test_get_law_json_flag_exists():
    """Verify --json flag is accepted by get-law parser."""
    assert "--json" in _run_help("get-law")


def test_get_law_save_flag_exists():
    """Verify --save flag is accepted by get-law parser."""
    assert "--save" in _run_help("get-law")


def test_get_article_json_flag_exists():
    """Verify --json flag is accepted by get-article parser."""
    assert "--json" in _run_help("get-article")


def test_get_article_save_flag_exists():
    """Verify --save flag is accepted by get-article parser."""
    assert "--save" in _run_help("get-article")


def test_get_case_json_flag_exists():
    """Verify --json flag is accepted by get-case parser."""
    assert "--json" in _run_help("get-case")


def test_get_case_save_flag_exists():
    """Verify --save flag is accepted by get-case parser."""
    assert "--save" in _run_help("get-case")


def test_search_law_no_save_flag():
    """Verify --save is NOT on search-law command."""
    assert "--save" not in _run_help("search-law")


def test_search_law_no_json_flag():
    """Verify --json is NOT on search-law command."""
    assert "--json" not in _run_help("search-law")


def test_search_cases_no_save_flag():
    """Verify --save is NOT on search-cases command."""
    assert "--save" not in _run_help("search-cases")


def test_search_interpretations_no_save_flag():
    """Verify --save is NOT on search-interpretations command."""
    assert "--save" not in _run_help("search-interpretations")
