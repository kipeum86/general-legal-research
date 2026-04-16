"""Post-fetch sanitization for sources[] JSON records.

Step 3 (web-researcher / deep-researcher) writes `output/research-result.json`
with fields like `snippet` and `full_text` populated from WebFetch,
`mcp__markitdown__convert_to_markdown`, or MCP search tools. That text is
untrusted (see `CLAUDE.md § 1a) Trust Boundary`), so this CLI walks every
record and:

1. Runs `prompt_injection_filter.sanitize()` on `snippet` and `full_text`.
2. Records `prompt_injection_risk` (`low`/`medium`/`high`) and
   `prompt_injection_findings` on each source.
3. For `high`-risk sources, replaces `snippet`/`full_text` with
   `[EXCLUDED_HIGH_RISK]` so downstream steps cannot quote them.

Usage:
    python3 scripts/sanitize_source.py output/research-result.json
    python3 scripts/sanitize_source.py output/research-result.json --output sanitized.json

Exit codes:
    0 — all sources clean
    2 — at least one medium- or high-risk source was sanitized
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prompt_injection_filter as pif  # noqa: E402


_TEXT_FIELDS = ("snippet", "full_text", "raw_text", "excerpt")


def _worst(a: str, b: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return a if order[a] >= order[b] else b


def _sanitize_source(source: dict) -> tuple[dict, str, list[str]]:
    """Return (updated_source, risk_level, finding_codes)."""
    worst = "low"
    codes: set[str] = set()

    for field in _TEXT_FIELDS:
        value = source.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        cleaned, report = pif.sanitize(value)
        worst = _worst(worst, report.risk_level)
        for f in report.findings:
            codes.add(f.code)
        source[field] = cleaned

    if worst == "high":
        for field in _TEXT_FIELDS:
            if isinstance(source.get(field), str):
                source[field] = "[EXCLUDED_HIGH_RISK]"

    source["prompt_injection_risk"] = worst
    source["prompt_injection_findings"] = sorted(codes)
    return source, worst, sorted(codes)


def sanitize_file(path: Path, output: Path | None = None) -> dict:
    """Sanitize every source in the JSON file in place (or write to `output`)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = data.get("sources")
    if not isinstance(sources, list):
        raise ValueError(
            f"{path}: expected top-level 'sources' array, got {type(sources).__name__}"
        )

    medium_count = 0
    high_count = 0
    for source in sources:
        if not isinstance(source, dict):
            continue
        _, risk, _ = _sanitize_source(source)
        if risk == "medium":
            medium_count += 1
        elif risk == "high":
            high_count += 1

    target = output or path
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "path": str(path),
        "output": str(target),
        "total_sources": len(sources),
        "medium_count": medium_count,
        "high_count": high_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Sanitize prompt-injection patterns in a sources[] JSON file. "
            "Overwrites the file in place unless --output is given."
        ),
    )
    parser.add_argument("path", help="Path to sources JSON (e.g. output/research-result.json)")
    parser.add_argument(
        "--output",
        help="Write sanitized JSON to this path instead of overwriting input",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = sanitize_file(
        Path(args.path),
        Path(args.output) if args.output else None,
    )
    print(
        "Sanitized {total_sources} source(s): "
        "{medium_count} medium, {high_count} high.".format(**summary)
    )
    return 0 if summary["medium_count"] == 0 and summary["high_count"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
