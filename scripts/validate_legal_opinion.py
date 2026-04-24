"""Validate structural requirements for legal opinion Markdown drafts."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SECTION_RULES: dict[str, tuple[str, ...]] = {
    "scope": ("scope", "assumption", "as-of", "범위", "전제", "기준일"),
    "conclusion_summary": ("conclusion", "executive summary", "key conclusion", "결론", "요약"),
    "issue_tree": ("issue tree", "issues presented", "issue", "쟁점"),
    "detailed_analysis": ("detailed analysis", "legal analysis", "analysis", "분석", "검토의견"),
    "counter_analysis": ("counter", "risk consideration", "risk", "반대", "반론", "리스크", "위험"),
    "practical_implications": ("practical", "implication", "recommendation", "실무", "권고", "시사점"),
    "annotated_bibliography": ("bibliography", "annotated", "sources", "참고문헌", "출처", "자료"),
    "verification_guide": ("verification", "verify", "검증", "확인"),
}


@dataclass
class OpinionValidationResult:
    valid: bool = True
    missing_sections: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "missing_sections": self.missing_sections,
            "errors": self.errors,
            "warnings": self.warnings,
            "headings": self.headings,
        }


def validate_legal_opinion_text(text: str, *, require_audit: bool = False) -> OpinionValidationResult:
    result = OpinionValidationResult()
    headings = extract_headings(text)
    result.headings = headings

    if not headings:
        result.valid = False
        result.errors.append("No Markdown headings found.")
        return result

    normalized_headings = [_normalize(heading) for heading in headings]
    for section, tokens in SECTION_RULES.items():
        if not any(any(token in heading for token in tokens) for heading in normalized_headings):
            result.missing_sections.append(section)

    if result.missing_sections:
        result.valid = False
        result.errors.append("Missing required legal opinion sections.")

    if require_audit and not _has_citation_audit_log(text):
        result.valid = False
        result.errors.append("Citation Audit Log appendix is required but missing.")

    if "[Unverified]" in text and not _has_citation_audit_log(text):
        result.warnings.append("[Unverified] tags are present without a Citation Audit Log appendix.")

    return result


def validate_legal_opinion_file(path: str | Path, *, require_audit: bool = False) -> OpinionValidationResult:
    return validate_legal_opinion_text(Path(path).read_text(encoding="utf-8"), require_audit=require_audit)


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^#{1,6}\s+(.+)$", stripped)
        if match:
            headings.append(_strip_markup(match.group(1)))
            continue
        if re.fullmatch(r"\*\*[^*]+\*\*", stripped):
            headings.append(_strip_markup(stripped))
    return headings


def _strip_markup(value: str) -> str:
    return value.strip().strip("#").replace("**", "").strip()


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower())


def _has_citation_audit_log(text: str) -> bool:
    lowered = text.lower()
    return "citation audit log" in lowered or "검증 로그" in lowered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a legal opinion Markdown draft.")
    parser.add_argument("file", type=Path, help="Markdown file to validate.")
    parser.add_argument("--require-audit", action="store_true", help="Require a Citation Audit Log appendix.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = validate_legal_opinion_file(args.file, require_audit=args.require_audit)
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    elif result.valid:
        print("Legal opinion validation passed.")
    else:
        print("Legal opinion validation failed.")
        for error in result.errors:
            print(f"- {error}")
        if result.missing_sections:
            print(f"- Missing sections: {', '.join(result.missing_sections)}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
