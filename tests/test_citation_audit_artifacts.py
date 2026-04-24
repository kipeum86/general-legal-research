import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "citation_audit_artifacts.py"
SPEC = importlib.util.spec_from_file_location("citation_audit_artifacts", MODULE_PATH)
citation_audit_artifacts = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = citation_audit_artifacts
SPEC.loader.exec_module(citation_audit_artifacts)
resolve_audit_artifact = citation_audit_artifacts.resolve_audit_artifact


def test_explicit_audit_json_wins_over_session_and_latest(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    explicit = tmp_path / "explicit.json"
    session = output_dir / "citation-audit-session-1.json"
    latest = output_dir / "citation-audit-latest.json"
    explicit.write_text("{}", encoding="utf-8")
    session.write_text("{}", encoding="utf-8")
    latest.write_text("{}", encoding="utf-8")

    resolved = resolve_audit_artifact(output_dir, session_id="session-1", explicit_path=explicit)

    assert resolved.found
    assert resolved.path == explicit
    assert resolved.source == "explicit"


def test_session_audit_json_wins_over_latest(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    session = output_dir / "citation-audit-session-1.json"
    latest = output_dir / "citation-audit-latest.json"
    session.write_text("{}", encoding="utf-8")
    latest.write_text("{}", encoding="utf-8")

    resolved = resolve_audit_artifact(output_dir, session_id="session-1")

    assert resolved.found
    assert resolved.path == session
    assert resolved.source == "session"


def test_latest_is_deprecated_fallback(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    latest = output_dir / "citation-audit-latest.json"
    latest.write_text("{}", encoding="utf-8")

    resolved = resolve_audit_artifact(output_dir, session_id="missing-session")

    assert resolved.found
    assert resolved.path == latest
    assert resolved.source == "latest-fallback"


def test_missing_explicit_path_does_not_fall_back(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    latest = output_dir / "citation-audit-latest.json"
    latest.write_text("{}", encoding="utf-8")
    missing = tmp_path / "missing.json"

    resolved = resolve_audit_artifact(output_dir, session_id="session-1", explicit_path=missing)

    assert not resolved.found
    assert resolved.path is None
    assert resolved.source == "explicit-missing"
    assert resolved.candidates == (missing,)
