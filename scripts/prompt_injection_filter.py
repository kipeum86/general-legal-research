"""Prompt-injection detection and redaction for ingested/fetched text.

Trust model
-----------
Every string fed into this module is treated as hostile data:
- Text converted from library/inbox/ documents
- Snippets and full_text from web fetches (WebFetch, MarkItDown, MCP search)
- Anything parsed out of user-supplied files

Purpose
-------
1. `scan(text)` returns a structured `Report` listing injection patterns
   with code, severity, offset, and matched span.
2. `sanitize(text)` replaces each high/medium-risk span with a neutralized
   marker (e.g. `[REDACTED:OVERRIDE_INSTRUCTIONS]`) and returns the report.
3. `wrap_as_data(text, source_label)` fences the payload in an
   `<<<UNTRUSTED_DATA>>>` block so downstream agents treat it as data,
   not instruction.

CLI
---
    python3 scripts/prompt_injection_filter.py scan --path FILE [--json]
    python3 scripts/prompt_injection_filter.py sanitize --path FILE --output OUT

Exit codes
----------
- 0: clean
- 2: medium/high-risk findings present (CI-friendly gating signal)
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Iterable


# ---------- patterns ----------


@dataclasses.dataclass(frozen=True)
class _Pattern:
    code: str
    severity: str  # "low" | "medium" | "high"
    regex: re.Pattern[str]
    description: str


def _compile(pattern: str, flags: int = re.IGNORECASE) -> re.Pattern[str]:
    return re.compile(pattern, flags)


# Order matters: more-specific markers first so the chat-marker matcher wins
# over the generic "system:" substring.
_PATTERNS: tuple[_Pattern, ...] = (
    # Chat-template / tool-call markers (LLM meta-syntax embedded in data)
    _Pattern(
        code="CHAT_MARKER",
        severity="high",
        regex=_compile(
            r"<\|(?:im_start|im_end|system|user|assistant)\|>"
            r"|<\|endoftext\|>"
            r"|\[INST\]|\[/INST\]"
            r"|^\s*(?:System|Assistant|Human|User)\s*:\s",
            flags=re.IGNORECASE | re.MULTILINE,
        ),
        description="Chat template or role marker embedded in untrusted text",
    ),
    _Pattern(
        code="TOOL_CALL_INJECTION",
        severity="high",
        regex=_compile(
            r"```(?:tool_call|function_call|tool_use|shell|bash)\b.*?```",
            flags=re.IGNORECASE | re.DOTALL,
        ),
        description="Fenced block attempting to invoke tools/shell commands",
    ),
    # Direct instruction overrides
    _Pattern(
        code="OVERRIDE_INSTRUCTIONS",
        severity="high",
        regex=_compile(
            r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+"
            r"(?:instructions?|prompts?|rules?|directives?|context)"
            r"|disregard\s+(?:the\s+)?(?:system|previous|prior|above)\s+"
            r"(?:prompt|instructions?|rules?)"
            r"|forget\s+(?:everything|all)\s+(?:you\s+)?(?:were\s+told|know)"
            r"|override\s+(?:the\s+)?(?:system\s+)?(?:prompt|instructions?)"
            r"|\[\[\s*system\s+override\s*\]\]"
            r"|이전\s*지시(?:사항|은|는)?\s*(?:모두\s*)?무시"
            r"|앞선?\s*지시(?:사항|은|는)?\s*(?:모두\s*)?무시"
            r"|시스템\s*프롬프트\s*(?:를|을)?\s*무시",
        ),
        description="Direct instruction to override system/prior prompts",
    ),
    _Pattern(
        code="REVEAL_SYSTEM",
        severity="high",
        regex=_compile(
            r"(?:reveal|show|print|dump|leak|expose)\s+(?:your\s+)?"
            r"(?:system\s+prompt|initial\s+instructions?|hidden\s+prompt|developer\s+message)"
            r"|what\s+(?:are\s+)?your\s+(?:system\s+)?instructions?"
            r"|시스템\s*프롬프트\s*(?:를|을)?\s*(?:공개|출력|노출|알려)"
            r"|초기\s*지시(?:사항)?\s*(?:을|를)?\s*(?:공개|알려)",
        ),
        description="Request to disclose the system/developer prompt",
    ),
    _Pattern(
        code="ROLE_REASSIGN",
        severity="high",
        regex=_compile(
            r"you\s+are\s+(?:now\s+)?(?:DAN|STAN|an?\s+unrestricted|an?\s+uncensored|"
            r"in\s+developer\s+mode|jailbroken|an?\s+evil)"
            r"|act\s+as\s+(?:if\s+you\s+were\s+)?(?:an?\s+unrestricted|DAN|"
            r"a\s+different\s+assistant|the\s+opposite)"
            r"|pretend\s+(?:to\s+be|you\s+are)\s+(?:an?\s+unrestricted|DAN|jailbroken)"
            r"|당신은\s*이제\s*(?:제한\s*없는|무제한|검열되지\s*않은|DAN)"
            r"|너는\s*이제\s*(?:제한\s*없는|무제한)",
        ),
        description="Attempt to reassign the model's role or persona",
    ),
    # Lower-confidence heuristics (not enough alone to trigger high risk)
    _Pattern(
        code="AI_SELF_REFERENCE",
        severity="low",
        regex=_compile(
            r"as\s+an?\s+(?:ai|language)\s+model"
            r"|i\s+am\s+an?\s+ai\s+(?:language\s+)?model",
        ),
        description="Text that speaks in the voice of an AI assistant",
    ),
)


# ---------- data classes ----------


@dataclasses.dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    start: int
    end: int
    snippet: str
    description: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class Report:
    findings: tuple[Finding, ...]
    risk_level: str  # "low" | "medium" | "high"

    def to_dict(self, *, path: str | None = None) -> dict:
        payload = {
            "risk_level": self.risk_level,
            "findings": [f.to_dict() for f in self.findings],
        }
        if path is not None:
            payload["path"] = path
        return payload


# ---------- detection ----------


def _iter_findings(text: str) -> Iterable[Finding]:
    seen_spans: set[tuple[int, int, str]] = set()
    for pattern in _PATTERNS:
        for match in pattern.regex.finditer(text):
            span = (match.start(), match.end(), pattern.code)
            if span in seen_spans:
                continue
            seen_spans.add(span)
            snippet = text[match.start() : match.end()].strip()
            if len(snippet) > 200:
                snippet = snippet[:200] + "…"
            yield Finding(
                code=pattern.code,
                severity=pattern.severity,
                start=match.start(),
                end=match.end(),
                snippet=snippet,
                description=pattern.description,
            )


def _risk_level(findings: tuple[Finding, ...]) -> str:
    high = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")
    low = sum(1 for f in findings if f.severity == "low")

    if high >= 2:
        return "high"
    if high == 1:
        return "medium" if medium + low == 0 else "high"
    if medium >= 1:
        return "medium"
    if low >= 1:
        return "medium" if low >= 2 else "low"
    return "low"


def scan(text: str) -> Report:
    """Return a structured report of injection patterns found in `text`."""
    if not text:
        return Report(findings=tuple(), risk_level="low")
    findings = tuple(sorted(_iter_findings(text), key=lambda f: f.start))
    return Report(findings=findings, risk_level=_risk_level(findings))


# ---------- redaction ----------


def sanitize(text: str) -> tuple[str, Report]:
    """Replace medium/high-severity matches with neutralized markers.

    Low-severity findings are reported but not redacted — they're often
    legitimate commentary (e.g. a law-firm memo discussing AI models).
    """
    report = scan(text)
    if not report.findings:
        return text, report

    # Walk in reverse so slice offsets remain valid.
    pieces = list(text)
    redactable = [f for f in report.findings if f.severity in {"medium", "high"}]
    for finding in sorted(redactable, key=lambda f: f.start, reverse=True):
        marker = f"[REDACTED:{finding.code}]"
        pieces[finding.start : finding.end] = list(marker)
    return "".join(pieces), report


def wrap_as_data(text: str, *, source_label: str) -> str:
    """Fence `text` in an untrusted-data block with a source label.

    Downstream agents must treat the contents as data, never instructions.
    """
    label = source_label.replace('"', "'")
    return (
        f'<<<UNTRUSTED_DATA source="{label}">>>\n'
        f"{text}\n"
        "<<<END_UNTRUSTED_DATA>>>"
    )


# ---------- CLI ----------


def _cmd_scan(args: argparse.Namespace) -> int:
    path = Path(args.path)
    text = path.read_text(encoding="utf-8", errors="replace")
    report = scan(text)
    if args.json:
        print(json.dumps(report.to_dict(path=str(path)), ensure_ascii=False, indent=2))
    else:
        print(f"Risk: {report.risk_level}")
        for f in report.findings:
            print(f"  [{f.severity:>6}] {f.code}: {f.snippet}")
    return 0 if report.risk_level == "low" else 2


def _cmd_sanitize(args: argparse.Namespace) -> int:
    src = Path(args.path)
    text = src.read_text(encoding="utf-8", errors="replace")
    cleaned, report = sanitize(text)
    out_path = Path(args.output) if args.output else src
    out_path.write_text(cleaned, encoding="utf-8")
    if args.json:
        print(json.dumps(report.to_dict(path=str(src)), ensure_ascii=False, indent=2))
    else:
        print(f"Sanitized {src} → {out_path} (risk: {report.risk_level})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan or sanitize untrusted text for prompt-injection patterns."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan_p = sub.add_parser("scan", help="Scan a file and print a risk report")
    scan_p.add_argument("--path", required=True, help="File to scan")
    scan_p.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    scan_p.set_defaults(func=_cmd_scan)

    san_p = sub.add_parser("sanitize", help="Write a redacted copy of the file")
    san_p.add_argument("--path", required=True, help="Input file")
    san_p.add_argument(
        "--output",
        help="Output file (defaults to overwriting input)",
    )
    san_p.add_argument("--json", action="store_true", help="Emit JSON report to stdout")
    san_p.set_defaults(func=_cmd_sanitize)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
