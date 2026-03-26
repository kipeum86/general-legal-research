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


# ---------------------------------------------------------------------------
# Article persistence
# ---------------------------------------------------------------------------

def write_article_md(
    *,
    law_name: str,
    law_dir: str,
    article_number: int,
    title: str,
    content: str,
    jurisdiction: str,
    source: str,
    source_id: str,
    cross_refs: list[dict] | None = None,
    library_dir: Path | None = None,
) -> Path:
    """Write a single article as Markdown with YAML frontmatter.

    Returns path to written file.
    """
    lib = library_dir or LIBRARY_DIR
    law_path = lib / law_dir
    law_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    refs = cross_refs or extract_crossrefs(content, jurisdiction)

    frontmatter = {
        "law": law_name,
        "article_number": article_number,
        "title": title,
        "jurisdiction": jurisdiction,
        "source": source,
        "source_id": source_id,
        "fetched_at": now,
        "grade": "A",
        "cross_refs": refs,
    }

    art_filename = f"art{article_number:03d}.md"
    art_path = law_path / art_filename

    lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {json.dumps(item, ensure_ascii=False)}")
        else:
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, bool)) else v}")
    lines.append("---")
    lines.append("")
    lines.append(f"# 제{article_number}조({title})" if jurisdiction == "KR" else f"# Article {article_number} — {title}")
    lines.append("")
    lines.append(content)
    lines.append("")

    art_path.write_text("\n".join(lines), encoding="utf-8")

    # Update or create _meta.json
    meta_path = law_path / "_meta.json"
    meta = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta.update({
        "law_name": law_name,
        "law_dir": law_dir,
        "jurisdiction": jurisdiction,
        "source": source,
        "last_fetched": now,
        "article_count": len(list(law_path.glob("art*.md"))),
    })
    _atomic_json_write(meta_path, meta)

    return art_path


def _atomic_json_write(path: Path, data: dict | list) -> None:
    """Write JSON atomically (write to temp file, then rename)."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(path)
