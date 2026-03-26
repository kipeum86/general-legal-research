"""
Shared legal document storage, indexing, and cross-reference module.

Used by open_law_api.py and eurlex_api.py (--save flag) to persist
fetched law articles to library/grade-a/ with structured metadata.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_DIR = PROJECT_ROOT / "library" / "grade-a"
INDEX_DIR = PROJECT_ROOT / "index"
STALENESS_DAYS = 90


class StoreError(RuntimeError):
    """Raised when cached legal data cannot be safely read or written."""


# ---------------------------------------------------------------------------
# Cross-reference extraction
# ---------------------------------------------------------------------------

_KR_ARTICLE_ID_RE = re.compile(r"^\s*(?:제\s*)?(\d+)(?:조)?(?:의\s*(\d+))?\s*$")
_EU_ARTICLE_ID_RE = re.compile(r"^\s*(?:Article|Articles|Art\.?)?\s*(\d+)(?:\((\d+)\))?\s*$", re.IGNORECASE)

# Korean patterns
_KR_INTERNAL_RE = re.compile(r"제\s*(\d+)조(?:의\s*(\d+))?")
_KR_EXTERNAL_RE = re.compile(r"「([^」]+)」\s*제\s*(\d+)조(?:의\s*(\d+))?")

# EU patterns
_EU_ARTICLE_BLOCK_RE = re.compile(
    r"\bArt(?:icle)?s?\.?\s+((?:\d+(?:\(\d+\))?)(?:\s*(?:,|;|and|or|to|-)\s*\d+(?:\(\d+\))?)*)",
    re.IGNORECASE,
)
_EU_ARTICLE_TOKEN_RE = re.compile(r"\d+(?:\(\d+\))?|,|;|-|\b(?:and|or|to)\b", re.IGNORECASE)
_EU_INSTRUMENT_RE = re.compile(
    r"\b(?:(?:Commission|Council|Implementing|Delegated)\s+)?"
    r"(Regulation|Directive|Decision)\s+"
    r"(?:\((EU|EC|EEC)\)\s*)?"
    r"(?:No\s+)?"
    r"(\d{2,4}/\d+(?:/[A-Z]{2,3})?)",
    re.IGNORECASE,
)


def extract_crossrefs(text: str, jurisdiction: str) -> list[dict]:
    """Extract cross-references from statute text."""
    refs: list[dict] = []

    if jurisdiction == "KR":
        external_matches = list(_KR_EXTERNAL_RE.finditer(text))
        external_spans = [m.span() for m in external_matches]

        for m in external_matches:
            article = _make_kr_article_ref(m.group(2), m.group(3))
            refs.append({
                "type": "external",
                "law": m.group(1),
                "article": article["article"],
                "article_id": article["article_id"],
                "raw": m.group(0),
                **({"article_suffix": article["article_suffix"]} if article["article_suffix"] is not None else {}),
            })

        for m in _KR_INTERNAL_RE.finditer(text):
            if any(start <= m.start() < end for start, end in external_spans):
                continue
            article = _make_kr_article_ref(m.group(1), m.group(2))
            refs.append({
                "type": "internal",
                "article": article["article"],
                "article_id": article["article_id"],
                "raw": m.group(0),
                **({"article_suffix": article["article_suffix"]} if article["article_suffix"] is not None else {}),
            })

    elif jurisdiction == "EU":
        for m in _EU_ARTICLE_BLOCK_RE.finditer(text):
            for token in _expand_eu_article_tokens(m.group(1)):
                article = _normalize_article_identifier(token, "EU")
                refs.append({
                    "type": "internal",
                    "article": article["number"],
                    "article_id": article["id"],
                    "raw": f"Article {token}",
                    **({"article_paragraph": article["paragraph"]} if article["paragraph"] is not None else {}),
                })

        for m in _EU_INSTRUMENT_RE.finditer(text):
            instrument_type = m.group(1).lower()
            instrument_id = m.group(3)
            refs.append({
                "type": "external_instrument",
                "instrument_type": instrument_type,
                "regulation": instrument_id,
                "raw": m.group(0),
            })

    seen = set()
    unique = []
    for ref in refs:
        key = (
            ref.get("type"),
            ref.get("law", ""),
            ref.get("article_id", ""),
            ref.get("instrument_type", ""),
            ref.get("regulation", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(ref)
    return unique


def _make_kr_article_ref(article: str | int, suffix: str | int | None = None) -> dict:
    canonical = str(article)
    if suffix not in (None, ""):
        canonical = f"{canonical}의{suffix}"
    normalized = _normalize_article_identifier(canonical, "KR")
    return {
        "article": normalized["number"],
        "article_id": normalized["id"],
        "article_suffix": normalized["suffix"],
    }


def _expand_eu_article_tokens(sequence: str) -> list[str]:
    tokens = _EU_ARTICLE_TOKEN_RE.findall(sequence)
    expanded: list[str] = []
    previous_number: int | None = None
    range_pending = False

    for token in tokens:
        lowered = token.lower()
        if lowered in {",", ";", "and", "or"}:
            range_pending = False
            continue
        if lowered in {"to", "-"}:
            range_pending = previous_number is not None
            continue

        match = re.fullmatch(r"(\d+)(?:\((\d+)\))?", token)
        if not match:
            range_pending = False
            previous_number = None
            continue

        current_number = int(match.group(1))
        current_paragraph = match.group(2)

        if range_pending and previous_number is not None and current_paragraph is None:
            for number in range(previous_number + 1, current_number + 1):
                expanded.append(str(number))
        else:
            expanded.append(token)

        previous_number = current_number if current_paragraph is None else None
        range_pending = False

    return expanded


# ---------------------------------------------------------------------------
# Article persistence
# ---------------------------------------------------------------------------

def write_article_md(
    *,
    law_name: str,
    law_dir: str,
    article_number: int | str,
    title: str,
    content: str,
    jurisdiction: str,
    source: str,
    source_id: str,
    cross_refs: list[dict] | None = None,
    library_dir: Path | None = None,
    article_id: str | None = None,
) -> Path:
    """Write a single article as Markdown with YAML frontmatter."""
    lib = library_dir or LIBRARY_DIR
    law_path = lib / law_dir
    now = datetime.now(timezone.utc).isoformat()
    article_ref = _normalize_article_identifier(article_id or article_number, jurisdiction)
    refs = cross_refs if cross_refs is not None else extract_crossrefs(content, jurisdiction)
    markdown = _render_article_markdown(
        law_name=law_name,
        article_ref=article_ref,
        title=title,
        content=content,
        jurisdiction=jurisdiction,
        source=source,
        source_id=source_id,
        fetched_at=now,
        cross_refs=refs,
    )
    art_path = law_path / article_ref["filename"]

    with _exclusive_lock(_lock_root_for_library(lib)):
        law_path.mkdir(parents=True, exist_ok=True)
        _atomic_text_write(art_path, markdown)
        _atomic_json_write(
            law_path / "_meta.json",
            _build_meta(
                law_name=law_name,
                law_dir=law_dir,
                jurisdiction=jurisdiction,
                source=source,
                source_id=source_id,
                fetched_at=now,
                article_count=len(list(law_path.glob("art*.md"))),
            ),
        )

    return art_path


def save_law_articles(
    *,
    law_name: str,
    law_dir: str,
    jurisdiction: str,
    source: str,
    source_id: str,
    articles: list[dict],
    library_dir: Path | None = None,
    index_dir: Path | None = None,
    replace_existing: bool = False,
) -> Path:
    """Persist a law bundle and keep all indices in sync."""
    if not articles:
        raise StoreError(f"No articles to save for {law_name}")

    lib = library_dir or LIBRARY_DIR
    idx_dir = index_dir or INDEX_DIR
    law_path = lib / law_dir
    lock_root = _lock_root_for_library_and_index(lib, idx_dir)

    normalized_articles = [_normalize_article_payload(article, jurisdiction) for article in articles]
    fetched_at = datetime.now(timezone.utc).isoformat()

    with _exclusive_lock(lock_root):
        lib.mkdir(parents=True, exist_ok=True)
        idx_dir.mkdir(parents=True, exist_ok=True)

        live_dir = law_path
        stage_dir = lib / f".{law_dir}.stage-{uuid.uuid4().hex}"
        backup_dir = lib / f".{law_dir}.backup-{uuid.uuid4().hex}"

        ai_path = idx_dir / "article-index.json"
        sr_path = idx_dir / "source-registry.json"
        rev_path = idx_dir / "cross-refs-reverse.json"

        previous_json = {
            ai_path: ai_path.read_bytes() if ai_path.exists() else None,
            sr_path: sr_path.read_bytes() if sr_path.exists() else None,
            rev_path: rev_path.read_bytes() if rev_path.exists() else None,
        }

        live_meta = _safe_read_json(live_dir / "_meta.json", default={}, allow_missing=True) if live_dir.exists() else {}
        previous_law_names = {
            law_name,
            str(live_meta.get("law_name", "")).strip(),
        }

        ai = _safe_read_json(ai_path, default={}, allow_missing=True)
        sr = _safe_read_json(sr_path, default={}, allow_missing=True)
        rev = _safe_read_json(rev_path, default={}, allow_missing=True)

        previous_law_names.update(_law_names_for_law_dir(ai, law_dir))
        previous_law_names.update(_law_names_for_law_dir(sr, law_dir))
        previous_law_names.discard("")

        try:
            if replace_existing or not live_dir.exists():
                stage_dir.mkdir(parents=True, exist_ok=False)
            else:
                shutil.copytree(live_dir, stage_dir)

            for article in normalized_articles:
                article_ref = {
                    "number": article["article_number"],
                    "suffix": article["article_suffix"],
                    "paragraph": article["paragraph"],
                    "id": article["article_id"],
                    "filename": article["filename"],
                }
                (stage_dir / article["filename"]).write_text(
                    _render_article_markdown(
                        law_name=law_name,
                        article_ref=article_ref,
                        title=article["title"],
                        content=article["content"],
                        jurisdiction=jurisdiction,
                        source=source,
                        source_id=source_id,
                        fetched_at=fetched_at,
                        cross_refs=article["cross_refs"],
                    ),
                    encoding="utf-8",
                )

            _atomic_json_write(
                stage_dir / "_meta.json",
                _build_meta(
                    law_name=law_name,
                    law_dir=law_dir,
                    jurisdiction=jurisdiction,
                    source=source,
                    source_id=source_id,
                    fetched_at=fetched_at,
                    article_count=len(list(stage_dir.glob("art*.md"))),
                ),
            )

            final_article_inventory = _collect_article_inventory(stage_dir, jurisdiction)
            final_index_articles = [
                {
                    "article_number": article["article_number"],
                    "article_id": article["article_id"],
                    **({"article_suffix": article["article_suffix"]} if article["article_suffix"] is not None else {}),
                    "title": article["title"],
                    "file": article["file"],
                }
                for article in final_article_inventory
            ]

            new_ai = _upsert_index_entries(
                current=ai,
                law_name=law_name,
                law_dir=law_dir,
                jurisdiction=jurisdiction,
                articles=final_index_articles,
                fetched_at=fetched_at,
                source=source,
                source_id=source_id,
            )
            new_sr = _upsert_source_registry(
                current=sr,
                law_name=law_name,
                law_dir=law_dir,
                jurisdiction=jurisdiction,
                article_count=len(final_article_inventory),
                fetched_at=fetched_at,
                source=source,
                source_id=source_id,
            )
            new_rev = _rebuild_reverse_index_for_law(
                current=rev,
                law_name=law_name,
                law_dir=law_dir,
                previous_law_names=previous_law_names,
                articles=final_article_inventory,
            )

            restore_needed = False
            if live_dir.exists():
                live_dir.rename(backup_dir)
                restore_needed = True
            stage_dir.rename(live_dir)

            try:
                _atomic_json_write(ai_path, new_ai)
                _atomic_json_write(sr_path, new_sr)
                _atomic_json_write(rev_path, new_rev)
            except Exception:
                if live_dir.exists():
                    shutil.rmtree(live_dir)
                if restore_needed and backup_dir.exists():
                    backup_dir.rename(live_dir)
                for path, original in previous_json.items():
                    _restore_bytes(path, original)
                raise

            if backup_dir.exists():
                try:
                    shutil.rmtree(backup_dir)
                except OSError:
                    pass

        except Exception as exc:
            if stage_dir.exists():
                shutil.rmtree(stage_dir)
            if isinstance(exc, StoreError):
                raise
            raise StoreError(f"Failed to save {law_name}: {exc}") from exc

    return law_path


def save_case_json(
    *,
    case_id: str,
    payload: dict,
    library_dir: Path | None = None,
) -> Path:
    """Persist a case payload atomically."""
    lib = library_dir or LIBRARY_DIR
    case_dir = lib / "_cases"
    case_path = case_dir / f"case_{case_id}.json"

    with _exclusive_lock(_lock_root_for_library(lib)):
        case_dir.mkdir(parents=True, exist_ok=True)
        _atomic_json_write(case_path, payload)

    return case_path


def _render_article_markdown(
    *,
    law_name: str,
    article_ref: dict,
    title: str,
    content: str,
    jurisdiction: str,
    source: str,
    source_id: str,
    fetched_at: str,
    cross_refs: list[dict],
) -> str:
    frontmatter = {
        "law": law_name,
        "article_number": article_ref["number"],
        "article_id": article_ref["id"],
        "title": title,
        "jurisdiction": jurisdiction,
        "source": source,
        "source_id": source_id,
        "fetched_at": fetched_at,
        "grade": "A",
        "cross_refs": cross_refs,
    }
    if article_ref["suffix"] is not None:
        frontmatter["article_suffix"] = article_ref["suffix"]

    heading = _format_article_heading(article_ref, jurisdiction, title)

    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {json.dumps(item, ensure_ascii=False)}")
        else:
            lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.extend(["---", "", heading, "", content.rstrip(), ""])
    return "\n".join(lines)


def _normalize_article_payload(article: dict, jurisdiction: str) -> dict:
    article_value = article.get("article_id", article.get("article_number"))
    if article_value in (None, ""):
        raise StoreError(f"Article payload is missing article_number/article_id: {article!r}")

    article_ref = _normalize_article_identifier(article_value, jurisdiction)
    title = str(article.get("title", "") or "")
    content = str(article.get("content", "") or "")
    cross_refs = article.get("cross_refs")
    if cross_refs is None:
        cross_refs = extract_crossrefs(content, jurisdiction)
    if not isinstance(cross_refs, list):
        raise StoreError(f"cross_refs must be a list for article {article_ref['id']}")

    return {
        "article_number": article_ref["number"],
        "article_id": article_ref["id"],
        "article_suffix": article_ref["suffix"],
        "paragraph": article_ref["paragraph"],
        "title": title,
        "content": content,
        "cross_refs": cross_refs,
        "filename": article_ref["filename"],
    }


def _build_meta(
    *,
    law_name: str,
    law_dir: str,
    jurisdiction: str,
    source: str,
    source_id: str,
    fetched_at: str,
    article_count: int,
) -> dict:
    return {
        "law_name": law_name,
        "law_dir": law_dir,
        "jurisdiction": jurisdiction,
        "source": source,
        "source_id": source_id,
        "last_fetched": fetched_at,
        "article_count": article_count,
    }


def _format_article_heading(article_ref: dict, jurisdiction: str, title: str) -> str:
    if jurisdiction == "KR":
        heading = f"# 제{article_ref['id']}조"
        if title:
            heading += f"({title})"
        return heading

    heading = f"# Article {article_ref['id']}"
    if title:
        heading += f" — {title}"
    return heading


def _normalize_article_identifier(article: int | str, jurisdiction: str) -> dict:
    raw = str(article).strip()

    if jurisdiction == "KR":
        match = _KR_ARTICLE_ID_RE.fullmatch(raw)
        if not match:
            raise StoreError(f"Unsupported Korean article identifier: {article!r}")
        number = int(match.group(1))
        suffix = int(match.group(2)) if match.group(2) else None
        article_id = str(number) if suffix is None else f"{number}의{suffix}"
        filename = f"art{number:03d}.md" if suffix is None else f"art{number:03d}-{suffix:03d}.md"
        return {
            "number": number,
            "suffix": suffix,
            "paragraph": None,
            "id": article_id,
            "filename": filename,
        }

    if jurisdiction == "EU":
        match = _EU_ARTICLE_ID_RE.fullmatch(raw)
        if not match:
            raise StoreError(f"Unsupported EU article identifier: {article!r}")
        number = int(match.group(1))
        paragraph = int(match.group(2)) if match.group(2) else None
        article_id = str(number)
        return {
            "number": number,
            "suffix": None,
            "paragraph": paragraph,
            "id": article_id,
            "filename": f"art{number:03d}.md",
        }

    raise StoreError(f"Unsupported jurisdiction for article identifier: {jurisdiction}")


def _collect_article_inventory(law_path: Path, jurisdiction: str) -> list[dict]:
    articles = []
    for art_path in sorted(law_path.glob("art*.md")):
        raw_text = art_path.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter(raw_text)
        article_id = frontmatter.get("article_id")
        if article_id in (None, ""):
            article_id = _article_id_from_filename(art_path.name)
        article_ref = _normalize_article_identifier(article_id, jurisdiction)

        cross_refs = frontmatter.get("cross_refs", [])
        if not isinstance(cross_refs, list):
            raise StoreError(f"cross_refs in {art_path} must be a list")

        articles.append({
            "article_number": article_ref["number"],
            "article_id": article_ref["id"],
            "article_suffix": article_ref["suffix"],
            "title": str(frontmatter.get("title", "") or ""),
            "cross_refs": cross_refs,
            "file": art_path.name,
        })

    articles.sort(key=lambda item: (item["article_number"], item["article_suffix"] or 0))
    return articles


def _article_id_from_filename(name: str) -> str:
    match = re.fullmatch(r"art(\d{3})(?:-(\d{3}))?\.md", name)
    if not match:
        raise StoreError(f"Unsupported cached article filename: {name}")
    number = int(match.group(1))
    suffix = int(match.group(2)) if match.group(2) else None
    return str(number) if suffix is None else f"{number}의{suffix}"


# ---------------------------------------------------------------------------
# Atomic filesystem helpers
# ---------------------------------------------------------------------------

def _atomic_json_write(path: Path, data: dict | list) -> None:
    _atomic_text_write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
        _fsync_directory(path.parent)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def _restore_bytes(path: Path, data: bytes | None) -> None:
    if data is None:
        if path.exists():
            path.unlink()
        return

    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.restore.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
        _fsync_directory(path.parent)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def _fsync_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return

    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


@contextmanager
def _exclusive_lock(lock_root: Path):
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / ".legal_store.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _lock_root_for_library(lib: Path) -> Path:
    return lib.parent if lib.parent != lib else lib


def _lock_root_for_library_and_index(lib: Path, idx: Path) -> Path:
    common = Path(os.path.commonpath([str(lib.resolve()), str(idx.resolve())]))
    return common


def _safe_read_json(path: Path, *, default, allow_missing: bool) -> dict | list:
    if not path.exists():
        if allow_missing:
            return default.copy() if isinstance(default, dict) else list(default)
        raise StoreError(f"Missing required JSON file: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StoreError(f"Corrupted JSON in {path}: {exc}") from exc

    if isinstance(default, dict) and not isinstance(data, dict):
        raise StoreError(f"Expected JSON object in {path}")
    if isinstance(default, list) and not isinstance(data, list):
        raise StoreError(f"Expected JSON array in {path}")
    return data


def _parse_frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    data = {}
    index = 1
    while index < len(lines):
        line = lines[index]
        if line.strip() == "---":
            break
        if not line.strip():
            index += 1
            continue

        if line.endswith(":") and ": " not in line:
            key = line[:-1].strip()
            items = []
            index += 1
            while index < len(lines):
                item_line = lines[index]
                if item_line.strip() == "---":
                    break
                if not item_line.startswith("  - "):
                    break
                items.append(_parse_frontmatter_value(item_line[4:].strip()))
                index += 1
            data[key] = items
            continue

        if ":" in line:
            key, raw_value = line.split(":", 1)
            data[key.strip()] = _parse_frontmatter_value(raw_value.strip())
        index += 1

    return data


def _parse_frontmatter_value(raw: str):
    if raw == "":
        return ""
    if raw in {"true", "false", "null"}:
        return json.loads(raw)
    if raw.startswith(("{", "[", '"')):
        return json.loads(raw)
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def _yaml_scalar(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if value == "":
            return '""'
        if (
            "\n" in value
            or ":" in value
            or value.startswith((" ", "-", "?", "@", "!", "&", "*", "{", "[", "#"))
            or value.endswith(" ")
            or value in {"true", "false", "null"}
            or re.fullmatch(r"-?\d+(?:\.\d+)?", value)
        ):
            return json.dumps(value, ensure_ascii=False)
        return value
    return json.dumps(value, ensure_ascii=False)


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
    source: str | None = None,
    source_id: str | None = None,
) -> None:
    """Update article-index.json and source-registry.json."""
    idx_dir = index_dir or INDEX_DIR
    now = datetime.now(timezone.utc).isoformat()

    with _exclusive_lock(idx_dir.parent if idx_dir.parent != idx_dir else idx_dir):
        idx_dir.mkdir(parents=True, exist_ok=True)
        ai_path = idx_dir / "article-index.json"
        sr_path = idx_dir / "source-registry.json"

        ai = _safe_read_json(ai_path, default={}, allow_missing=True)
        sr = _safe_read_json(sr_path, default={}, allow_missing=True)

        new_ai = _upsert_index_entries(
            current=ai,
            law_name=law_name,
            law_dir=law_dir,
            jurisdiction=jurisdiction,
            articles=articles,
            fetched_at=now,
            source=source or "",
            source_id=source_id or "",
        )
        new_sr = _upsert_source_registry(
            current=sr,
            law_name=law_name,
            law_dir=law_dir,
            jurisdiction=jurisdiction,
            article_count=len(articles),
            fetched_at=now,
            source=source or "",
            source_id=source_id or "",
        )

        _atomic_json_write(ai_path, new_ai)
        _atomic_json_write(sr_path, new_sr)


def _upsert_index_entries(
    *,
    current: dict,
    law_name: str,
    law_dir: str,
    jurisdiction: str,
    articles: list[dict],
    fetched_at: str,
    source: str,
    source_id: str,
) -> dict:
    updated = {key: value for key, value in current.items() if _entry_law_dir(value) != law_dir and key != law_name}
    sorted_articles = sorted(
        articles,
        key=lambda item: _article_sort_key(item.get("article_id", item.get("article_number"))),
    )
    updated[law_name] = {
        "law_dir": law_dir,
        "jurisdiction": jurisdiction,
        "source": source,
        "source_id": source_id,
        "articles": sorted_articles,
        "last_updated": fetched_at,
    }
    return updated


def _upsert_source_registry(
    *,
    current: dict,
    law_name: str,
    law_dir: str,
    jurisdiction: str,
    article_count: int,
    fetched_at: str,
    source: str,
    source_id: str,
) -> dict:
    updated = {key: value for key, value in current.items() if _entry_law_dir(value) != law_dir and key != law_name}
    updated[law_name] = {
        "law_dir": law_dir,
        "jurisdiction": jurisdiction,
        "source": source,
        "source_id": source_id,
        "article_count": article_count,
        "last_fetched": fetched_at,
    }
    return updated


def _entry_law_dir(value) -> str | None:
    if isinstance(value, dict):
        return value.get("law_dir")
    return None


def _law_names_for_law_dir(registry: dict, law_dir: str) -> set[str]:
    return {key for key, value in registry.items() if _entry_law_dir(value) == law_dir}


def _article_sort_key(article_value: int | str | None) -> tuple[int, int]:
    if article_value is None:
        return (0, 0)
    raw = str(article_value)
    match = _KR_ARTICLE_ID_RE.fullmatch(raw)
    if match:
        return (int(match.group(1)), int(match.group(2) or 0))
    match = _EU_ARTICLE_ID_RE.fullmatch(raw)
    if match:
        return (int(match.group(1)), int(match.group(2) or 0))
    if re.fullmatch(r"\d+", raw):
        return (int(raw), 0)
    return (0, 0)


# ---------------------------------------------------------------------------
# Cache lookup
# ---------------------------------------------------------------------------

def lookup(
    law_name: str,
    article: int | str | None = None,
    *,
    library_dir: Path | None = None,
) -> dict | None:
    """Look up a cached law or article."""
    lib = library_dir or LIBRARY_DIR
    if not lib.exists():
        return {"hit": False}

    law_dir = None
    meta = None
    for candidate in lib.iterdir():
        if not candidate.is_dir():
            continue
        meta_path = candidate / "_meta.json"
        if not meta_path.exists():
            continue
        try:
            candidate_meta = _safe_read_json(meta_path, default={}, allow_missing=False)
        except StoreError:
            continue
        if candidate_meta.get("law_name") == law_name:
            law_dir = candidate
            meta = candidate_meta
            break

    if law_dir is None or meta is None:
        return {"hit": False}

    if article is not None:
        article_ref = _normalize_article_identifier(article, str(meta.get("jurisdiction", "KR") or "KR"))
        art_path = law_dir / article_ref["filename"]
        if not art_path.exists():
            return {"hit": False}
        content = art_path.read_text(encoding="utf-8")
        fetched_at = _parse_fetched_at(content)
        return {
            "hit": True,
            "content": content,
            "path": str(art_path),
            "fetched_at": fetched_at,
            "stale": _is_stale(fetched_at),
        }

    return {
        "hit": True,
        "law_dir": str(law_dir),
        "meta": meta,
        "stale": _is_stale(meta.get("last_fetched")),
    }


def _parse_fetched_at(content: str) -> str | None:
    return _parse_frontmatter(content).get("fetched_at")


def _is_stale(fetched_at: str | None) -> bool:
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
    source_article: int | str,
    cross_refs: list[dict],
    index_dir: Path | None = None,
    source_law_dir: str | None = None,
    source_article_id: str | None = None,
) -> None:
    """Update the global reverse cross-reference index for one article."""
    idx_dir = index_dir or INDEX_DIR
    source_article_key = _canonical_article_key(source_article_id or source_article)
    source_article_number = _article_sort_key(source_article_key)[0]

    with _exclusive_lock(idx_dir.parent if idx_dir.parent != idx_dir else idx_dir):
        idx_dir.mkdir(parents=True, exist_ok=True)
        rev_path = idx_dir / "cross-refs-reverse.json"
        rev = _safe_read_json(rev_path, default={}, allow_missing=True)
        rev = _remove_reverse_entries_for_article(
            rev,
            source_law=source_law,
            source_law_dir=source_law_dir,
            source_article=source_article_number,
            source_article_id=source_article_key,
        )
        rev = _add_reverse_entries(
            rev,
            source_law=source_law,
            source_law_dir=source_law_dir,
            source_article=source_article_number,
            source_article_id=source_article_key,
            cross_refs=cross_refs,
        )
        _atomic_json_write(rev_path, rev)


def _rebuild_reverse_index_for_law(
    *,
    current: dict,
    law_name: str,
    law_dir: str,
    previous_law_names: set[str],
    articles: list[dict],
) -> dict:
    updated = {}
    for key, entries in current.items():
        retained = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("source_law_dir") == law_dir:
                continue
            if entry.get("source_law") in previous_law_names:
                continue
            retained.append(entry)
        if retained:
            updated[key] = retained

    for article in articles:
        updated = _add_reverse_entries(
            updated,
            source_law=law_name,
            source_law_dir=law_dir,
            source_article=article["article_number"],
            source_article_id=article["article_id"],
            cross_refs=article["cross_refs"],
        )
    return updated


def _remove_reverse_entries_for_article(
    current: dict,
    *,
    source_law: str,
    source_law_dir: str | None,
    source_article: int,
    source_article_id: str,
) -> dict:
    updated = {}
    for key, entries in current.items():
        retained = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            same_article = entry.get("source_article_id") == source_article_id or (
                entry.get("source_article_id") in (None, "") and entry.get("source_article") == source_article
            )
            same_source = entry.get("source_law_dir") == source_law_dir if source_law_dir else entry.get("source_law") == source_law
            if same_article and same_source:
                continue
            retained.append(entry)
        if retained:
            updated[key] = retained
    return updated


def _add_reverse_entries(
    current: dict,
    *,
    source_law: str,
    source_law_dir: str | None,
    source_article: int,
    source_article_id: str,
    cross_refs: list[dict],
) -> dict:
    updated = {key: list(value) for key, value in current.items()}

    for ref in cross_refs:
        target_article_id = ref.get("article_id")
        target_article = ref.get("article")
        if target_article_id in (None, "") and target_article is None:
            continue

        if target_article_id in (None, ""):
            target_article_id = str(target_article)

        target_law = ref.get("law", source_law)
        target_key = f"{target_law}:art{target_article_id}"
        entry = {
            "source_law": source_law,
            "source_article": source_article,
            "source_article_id": source_article_id,
        }
        if source_law_dir:
            entry["source_law_dir"] = source_law_dir

        existing_entries = updated.setdefault(target_key, [])
        if entry not in existing_entries:
            existing_entries.append(entry)

    return updated


def query_reverse_crossrefs(
    law_name: str,
    article: int | str | None = None,
    *,
    index_dir: Path | None = None,
) -> list[dict]:
    """Query who references a given law/article."""
    idx_dir = index_dir or INDEX_DIR
    rev_path = idx_dir / "cross-refs-reverse.json"
    if not rev_path.exists():
        return []

    rev = _safe_read_json(rev_path, default={}, allow_missing=False)
    if article is not None:
        article_id = _canonical_article_key(article)
        key = f"{law_name}:art{article_id}"
        return rev.get(key, [])

    results = []
    prefix = f"{law_name}:art"
    for key, entries in rev.items():
        if key.startswith(prefix):
            results.extend(entries)
    return results


def _canonical_article_key(article: int | str) -> str:
    raw = str(article).strip()
    if "의" in raw:
        return _normalize_article_identifier(raw, "KR")["id"]
    if re.search(r"\(\d+\)$", raw):
        return _normalize_article_identifier(raw, "EU")["id"]
    if re.fullmatch(r"\d+", raw):
        return raw.lstrip("0") or "0"
    return raw
