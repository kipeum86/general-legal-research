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


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def update_index(
    *,
    law_name: str,
    law_dir: str,
    jurisdiction: str,
    articles: list[dict],
    index_dir: Path | None = None,
) -> None:
    """Update article-index.json and source-registry.json."""
    idx_dir = index_dir or INDEX_DIR
    idx_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    # article-index.json
    ai_path = idx_dir / "article-index.json"
    ai = {}
    if ai_path.exists():
        ai = json.loads(ai_path.read_text(encoding="utf-8"))
    ai[law_name] = {
        "law_dir": law_dir,
        "jurisdiction": jurisdiction,
        "articles": articles,
        "last_updated": now,
    }
    _atomic_json_write(ai_path, ai)

    # source-registry.json
    sr_path = idx_dir / "source-registry.json"
    sr = {}
    if sr_path.exists():
        sr = json.loads(sr_path.read_text(encoding="utf-8"))
    sr[law_name] = {
        "law_dir": law_dir,
        "jurisdiction": jurisdiction,
        "article_count": len(articles),
        "last_fetched": now,
    }
    _atomic_json_write(sr_path, sr)


# ---------------------------------------------------------------------------
# Cache lookup
# ---------------------------------------------------------------------------

def lookup(
    law_name: str,
    article: int | None = None,
    *,
    library_dir: Path | None = None,
) -> dict | None:
    """Look up a cached law or article.

    Returns dict with keys: hit, content, path, stale, fetched_at
    Returns None if not found.
    """
    lib = library_dir or LIBRARY_DIR

    # Find matching law directory
    law_dir = None
    if not lib.exists():
        return {"hit": False}
    for d in lib.iterdir():
        if not d.is_dir():
            continue
        meta_path = d / "_meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("law_name") == law_name:
                law_dir = d
                break

    if law_dir is None:
        return {"hit": False}

    if article is not None:
        art_path = law_dir / f"art{article:03d}.md"
        if not art_path.exists():
            return {"hit": False}
        content = art_path.read_text(encoding="utf-8")
        fetched_at = _parse_fetched_at(content)
        stale = _is_stale(fetched_at)
        return {
            "hit": True,
            "content": content,
            "path": str(art_path),
            "fetched_at": fetched_at,
            "stale": stale,
        }
    else:
        # Return law-level info
        meta = json.loads((law_dir / "_meta.json").read_text(encoding="utf-8"))
        return {
            "hit": True,
            "law_dir": str(law_dir),
            "meta": meta,
            "stale": _is_stale(meta.get("last_fetched")),
        }


def _parse_fetched_at(content: str) -> str | None:
    """Extract fetched_at from frontmatter."""
    m = re.search(r"fetched_at:\s*(.+)", content)
    return m.group(1).strip() if m else None


def _is_stale(fetched_at: str | None) -> bool:
    """Check if fetched_at is older than STALENESS_DAYS."""
    if not fetched_at:
        return True
    try:
        dt = datetime.fromisoformat(fetched_at)
        age = (datetime.now(timezone.utc) - dt).days
        return age > STALENESS_DAYS
    except (ValueError, TypeError):
        return True


# ---------------------------------------------------------------------------
# Reverse cross-reference index
# ---------------------------------------------------------------------------

def update_crossref_reverse_index(
    *,
    source_law: str,
    source_article: int,
    cross_refs: list[dict],
    index_dir: Path | None = None,
) -> None:
    """Update the global reverse cross-reference index.

    For each outbound reference from source_law:source_article,
    add an entry so the target can find who references it.
    """
    idx_dir = index_dir or INDEX_DIR
    idx_dir.mkdir(parents=True, exist_ok=True)
    rev_path = idx_dir / "cross-refs-reverse.json"

    rev = {}
    if rev_path.exists():
        rev = json.loads(rev_path.read_text(encoding="utf-8"))

    for ref in cross_refs:
        target_law = ref.get("law", source_law)  # internal refs = same law
        target_article = ref.get("article")
        if target_article is None:
            continue
        key = f"{target_law}:art{target_article}"
        if key not in rev:
            rev[key] = []
        entry = {"source_law": source_law, "source_article": source_article}
        if entry not in rev[key]:
            rev[key].append(entry)

    _atomic_json_write(rev_path, rev)


def query_reverse_crossrefs(
    law_name: str,
    article: int | None = None,
    *,
    index_dir: Path | None = None,
) -> list[dict]:
    """Query who references a given law/article."""
    idx_dir = index_dir or INDEX_DIR
    rev_path = idx_dir / "cross-refs-reverse.json"
    if not rev_path.exists():
        return []
    rev = json.loads(rev_path.read_text(encoding="utf-8"))
    if article is not None:
        key = f"{law_name}:art{article}"
        return rev.get(key, [])
    else:
        results = []
        prefix = f"{law_name}:art"
        for k, v in rev.items():
            if k.startswith(prefix):
                results.extend(v)
        return results
