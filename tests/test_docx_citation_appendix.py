import importlib.util
import sys
from pathlib import Path

from docx import Document


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "docx_citation_appendix.py"
SPEC = importlib.util.spec_from_file_location("docx_citation_appendix", MODULE_PATH)
docx_citation_appendix = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = docx_citation_appendix
SPEC.loader.exec_module(docx_citation_appendix)
append_citation_audit_log = docx_citation_appendix.append_citation_audit_log
inject_unverified_tags_with_report = docx_citation_appendix.inject_unverified_tags_with_report


def _aggregate(text: str, start: int, end: int, label: str = "contradicted") -> dict:
    return {
        "aggregated": [
            {
                "claim": {
                    "text": text,
                    "sentence_span": {"start": start, "end": end},
                },
                "verdict": {
                    "label": label,
                    "verifier_name": "test-verifier",
                    "evidence": [{"url": "https://example.test/source"}],
                },
            }
        ]
    }


def test_injects_unverified_tag_when_span_matches_claim_text() -> None:
    body = "Alpha.\n\nBeta citation."
    claim = "Beta citation."
    start = body.index(claim)
    end = start + len(claim)

    annotated, report = inject_unverified_tags_with_report(body, _aggregate(claim, start, end))

    assert annotated == "Alpha.\n\nBeta citation. [Unverified]"
    assert report["inserted"] == 1
    assert report["skipped"] == []


def test_relocates_when_span_mismatch_but_claim_text_is_unique() -> None:
    body = "Alpha.\n\nBeta citation."
    claim = "Beta citation."

    annotated, report = inject_unverified_tags_with_report(body, _aggregate(claim, 0, len("Alpha.")))

    assert annotated == "Alpha.\n\nBeta citation. [Unverified]"
    assert report["inserted"] == 1
    assert report["relocated"] == 1


def test_skips_when_mismatched_claim_text_is_ambiguous() -> None:
    body = "Same claim.\n\nSame claim."
    claim = "Same claim."

    annotated, report = inject_unverified_tags_with_report(body, _aggregate(claim, 0, len("Different")))

    assert annotated == body
    assert report["inserted"] == 0
    assert report["skipped"][0]["reason"] == "ambiguous_claim_text"


def test_skips_claim_inside_code_fence() -> None:
    body = "Intro.\n\n```\nBeta citation.\n```\n"
    claim = "Beta citation."
    start = body.index(claim)
    end = start + len(claim)

    annotated, report = inject_unverified_tags_with_report(body, _aggregate(claim, start, end))

    assert annotated == body
    assert report["inserted"] == 0
    assert report["skipped"][0]["reason"] == "span_inside_code_or_quote"


def test_appendix_includes_audit_status_and_provenance() -> None:
    doc = Document()

    append_citation_audit_log(
        doc,
        {"aggregated": []},
        audit_status="skipped",
        artifact_path="output/citation-audit-session.json",
        resolution_message="No citation-audit JSON artifact found.",
        insertion_report={"inserted": 0, "relocated": 0, "skipped": [{"reason": "claim_text_not_found"}]},
    )

    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    assert "Audit status: skipped" in text
    assert "output/citation-audit-session.json" in text
    assert "inserted=0" in text
