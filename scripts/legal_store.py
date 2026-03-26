"""
Shared legal document storage, indexing, and cross-reference module.

Used by open_law_api.py and eurlex_api.py (--save flag) to persist
fetched law articles to library/grade-a/ with structured metadata.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_DIR = PROJECT_ROOT / "library" / "grade-a"
INDEX_DIR = PROJECT_ROOT / "index"
STALENESS_DAYS = 90

# ---------------------------------------------------------------------------
# Cross-reference extraction
# ---------------------------------------------------------------------------

# Korean patterns
_KR_INTERNAL_RE = re.compile(r"제(\d+)조(?:의(\d+))?")  # 제17조, 제39조의3
_KR_EXTERNAL_RE = re.compile(r"「([^」]+)」\s*제(\d+)조")  # 「법률명」 제X조

# EU patterns
_EU_ARTICLE_RE = re.compile(r"Article\s+(\d+)(?:\((\d+)\))?", re.IGNORECASE)
_EU_REGULATION_RE = re.compile(
    r"(?:Regulation|Directive)\s+\((?:EU|EC)\)\s+(\d{4}/\d+|\d+/\d+)",
    re.IGNORECASE,
)


def extract_crossrefs(text: str, jurisdiction: str) -> list[dict]:
    """Extract cross-references from statute text.

    Returns list of dicts:
      - type: "internal" (same law) or "external" (different law)
      - article: int (article number)
      - law: str (law name, for external only)
      - raw: str (matched text)
    """
    refs = []
    if jurisdiction == "KR":
        # External refs first (「법률명」 제X조) — must come before internal
        for m in _KR_EXTERNAL_RE.finditer(text):
            refs.append({
                "type": "external",
                "law": m.group(1),
                "article": int(m.group(2)),
                "raw": m.group(0),
            })
        # Internal refs (제X조) — exclude those already matched as external
        external_spans = {m.span() for m in _KR_EXTERNAL_RE.finditer(text)}
        for m in _KR_INTERNAL_RE.finditer(text):
            # Skip if this 제X조 is part of an external 「법률명」 제X조
            if any(es[0] <= m.start() <= es[1] for es in external_spans):
                continue
            art_num = int(m.group(1))
            refs.append({
                "type": "internal",
                "article": art_num,
                "raw": m.group(0),
            })
    elif jurisdiction == "EU":
        for m in _EU_ARTICLE_RE.finditer(text):
            refs.append({
                "type": "internal",
                "article": int(m.group(1)),
                "raw": m.group(0),
            })
        for m in _EU_REGULATION_RE.finditer(text):
            refs.append({
                "type": "external_regulation",
                "regulation": m.group(1),
                "raw": m.group(0),
            })
    # Deduplicate by (type, article)
    seen = set()
    unique = []
    for r in refs:
        key = (r["type"], r.get("law", ""), r.get("article", 0))
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique
