import importlib.util
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_legal_opinion.py"
SPEC = importlib.util.spec_from_file_location("validate_legal_opinion", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


VALID_OPINION = """
# Formal Legal Opinion Letter

## Scope and Assumptions

## Executive Summary / Conclusions

## Issue Tree

## Detailed Legal Analysis

## Counter-Analysis / Risk Considerations

## Practical Implications / Recommendations

## Annotated Bibliography

## Verification Guide
"""


def test_valid_legal_opinion_sections_pass() -> None:
    result = validator.validate_legal_opinion_text(VALID_OPINION)

    assert result.valid
    assert result.missing_sections == []


def test_missing_required_sections_fail() -> None:
    result = validator.validate_legal_opinion_text(
        """
        # Formal Legal Opinion Letter

        ## Scope and Assumptions

        ## Detailed Legal Analysis
        """
    )

    assert not result.valid
    assert "issue_tree" in result.missing_sections
    assert "verification_guide" in result.missing_sections


def test_require_audit_fails_when_appendix_missing() -> None:
    result = validator.validate_legal_opinion_text(VALID_OPINION, require_audit=True)

    assert not result.valid
    assert any("Citation Audit Log" in error for error in result.errors)


def test_require_audit_passes_when_appendix_present() -> None:
    result = validator.validate_legal_opinion_text(
        VALID_OPINION + "\n\n## 부록: 검증 로그 (Citation Audit Log)\n",
        require_audit=True,
    )

    assert result.valid


def test_cli_returns_nonzero_for_invalid_opinion(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text("# Formal Legal Opinion Letter\n\n## Scope and Assumptions\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/validate_legal_opinion.py", str(path), "--json"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "missing_sections" in result.stdout
