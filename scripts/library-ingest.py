"""
Library ingestion pipeline: processes files from library/inbox/,
converts PDF/DOCX/PPTX to Markdown, auto-classifies source grade (A/B/C),
generates YAML frontmatter, places into library/grade-{a,b,c}/, and updates indexes.

Usage:
    python3 scripts/library-ingest.py
    python3 scripts/library-ingest.py --library-dir library/ --knowledge-dir knowledge/

Dependencies:
    pip install 'markitdown[pdf,docx]'
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".html"}
PASSTHROUGH_EXTENSIONS = {".md", ".txt"}
UNSUPPORTED_EXTENSIONS = {".hwp", ".hwpx"}
CONVERTED_SUBDIR = "library-converted"

# --- Grade classification signals ---

GRADE_A_SIGNALS = [
    # Korean statute patterns
    r"법률\s*제\d+호",
    r"대통령령\s*제\d+호",
    r"조례\s*제\d+호",
    r"고시\s*제\d{4}[-‐]\d+호",
    r"훈령\s*제\d+호",
    r"예규\s*제\d+호",
    # Korean official publishers
    r"법제처|국가법령정보센터|law\.go\.kr|moleg\.go\.kr",
    r"국회|대법원|헌법재판소",
    # Guideline indicators + gov body
    r"(안내서|가이드라인|해설서).{0,30}(위원회|부|처|청|원)",
    # Foreign official sources
    r"Official\s+Gazette|Federal\s+Register|EUR-Lex",
    r"Public\s+Law\s+\d+[-‐]\d+",
    r"Directive\s+\d{4}/\d+/E[CU]",
    r"Regulation\s+\(E[CU]\)\s+\d{4}/\d+",
]

GRADE_B_SIGNALS = [
    # Korean case numbers
    r"대법원\s*\d{4}[가-힣]{1,2}\d+",
    r"헌법재판소\s*\d{4}헌[가-힣]\d+",
    r"의결\s*제\d{4}[-‐]\d+[-‐]\d+호",
    # Law firm domains / headers
    r"kimchang\.com|bkl\.co\.kr|leeko\.com|shinkim\.com|yulchon\.com|hwawoo\.com",
    r"Client\s+Alert|Legal\s+Update|법률\s*뉴스레터",
    # Legal media
    r"법률신문|대한변호사협회|법률타임즈",
    # Regulatory interpretations
    r"유권해석|질의회신|비조치의견서",
]

GRADE_C_SIGNALS = [
    r"Abstract|초록",
    r"References|참고문헌",
    r"KCI|RISS|SSRN|Google\s+Scholar",
    r"법학연구|정보법학|Law\s+Review|Journal\s+of",
    r"석사|박사|학위논문|thesis|dissertation",
    r"Commentary|Treatise|주석서",
]

GRADE_D_SIGNALS = [
    r"위키백과|나무위키|Wikipedia",
    r"네이버\s*블로그|티스토리|velog\.io",
]


def _ensure_markitdown():
    """Import markitdown or exit with install instructions."""
    try:
        from markitdown import MarkItDown
        return MarkItDown()
    except ImportError:
        print(
            "ERROR: markitdown is not installed.\n"
            "Run:  pip install 'markitdown[pdf,docx]'\n"
            "Or with venv:  source .venv/bin/activate && pip install 'markitdown[pdf,docx]'",
            file=sys.stderr,
        )
        sys.exit(1)


def _extract_title(md_text: str, fallback: str) -> str:
    """Extract title from first Markdown heading, or use filename as fallback."""
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("# ").strip()
    return fallback


def _classify_grade(text: str) -> tuple[str, str]:
    """Classify source grade based on content signals. Returns (grade, confidence)."""
    text_sample = text[:5000]

    a_hits = sum(1 for p in GRADE_A_SIGNALS if re.search(p, text_sample, re.IGNORECASE))
    b_hits = sum(1 for p in GRADE_B_SIGNALS if re.search(p, text_sample, re.IGNORECASE))
    c_hits = sum(1 for p in GRADE_C_SIGNALS if re.search(p, text_sample, re.IGNORECASE))
    d_hits = sum(1 for p in GRADE_D_SIGNALS if re.search(p, text_sample, re.IGNORECASE))

    if d_hits > 0 and a_hits == 0 and b_hits == 0:
        return "D", "high"

    if a_hits >= 2:
        return "A", "high"
    if a_hits == 1 and b_hits == 0:
        return "A", "medium"
    if b_hits >= 2:
        return "B", "high"
    if b_hits == 1 and a_hits == 0:
        return "B", "medium"
    if c_hits >= 2:
        return "C", "high"
    if c_hits == 1:
        return "C", "medium"
    if a_hits == 1:
        return "A", "low"
    if b_hits == 1:
        return "B", "low"

    return "?", "low"


def _make_slug(title: str) -> str:
    """Generate a filename-safe slug from title. Preserves Korean characters."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w가-힣\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug[:80] if slug else "untitled"


def _unique_path(target: Path) -> Path:
    """Return a unique path by appending -2, -3, etc. if target exists."""
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _detect_document_type(text: str, grade: str) -> str:
    """Detect document type from content."""
    sample = text[:3000]

    if re.search(r"법률\s*제\d+호|Public\s+Law|Act\s+No\.", sample):
        return "statute"
    if re.search(r"대통령령\s*제\d+호|시행령|Enforcement\s+Decree", sample):
        return "enforcement_decree"
    if re.search(r"안내서|가이드라인|해설서|Guidelines?|Guidance", sample, re.IGNORECASE):
        return "guideline"
    if re.search(r"조약|Convention|Treaty|Protocol", sample, re.IGNORECASE):
        return "treaty"
    if re.search(r"판결|판례|대법원\s*\d{4}|Judgment|Opinion of the Court", sample):
        return "precedent"
    if re.search(r"의결|결정|처분|Decision\s+No\.", sample):
        return "decision"
    if re.search(r"뉴스레터|Client\s+Alert|Legal\s+Update|Newsletter", sample, re.IGNORECASE):
        return "newsletter"
    if re.search(r"논문|학위|Abstract|thesis|dissertation", sample, re.IGNORECASE):
        return "paper"
    if re.search(r"의견서|Opinion\s+Letter|Legal\s+Opinion", sample, re.IGNORECASE):
        return "opinion"

    return "article"


def _detect_jurisdiction(text: str) -> str:
    """Detect jurisdiction from content."""
    sample = text[:3000]

    if re.search(r"법률\s*제|대통령령|법제처|law\.go\.kr|대한민국", sample):
        return "KR"
    if re.search(r"EUR-Lex|Directive\s+\d{4}/\d+|GDPR|European\s+Union", sample, re.IGNORECASE):
        return "EU"
    if re.search(r"U\.?S\.?\s+Code|Federal\s+Register|Congress|USC\s*§", sample, re.IGNORECASE):
        return "US"
    if re.search(r"法律第|e-Gov|日本", sample):
        return "JP"
    if re.search(r"legislation\.gov\.uk|Parliament|United\s+Kingdom", sample, re.IGNORECASE):
        return "UK"

    return ""


def _extract_cited_articles(text: str) -> list[str]:
    """Extract cited article numbers from text."""
    articles = set()
    for m in re.finditer(r"제(\d+)조(?:의(\d+))?", text):
        art = f"제{m.group(1)}조"
        if m.group(2):
            art += f"의{m.group(2)}"
        articles.add(art)
    for m in re.finditer(r"Article\s+(\d+)", text, re.IGNORECASE):
        articles.add(f"Article {m.group(1)}")
    for m in re.finditer(r"§\s*(\d+[\w.]*)", text):
        articles.add(f"§ {m.group(1)}")
    return sorted(articles)


def _extract_date(text: str) -> str:
    """Extract publication date from text."""
    sample = text[:3000]

    for pattern in [
        r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일",
        r"(\d{4})\.(\d{1,2})\.(\d{1,2})",
        r"(\d{4})-(\d{2})-(\d{2})",
    ]:
        m = re.search(pattern, sample)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return ""


def _extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """Extract keywords from legal text."""
    sample = text[:5000]
    candidates = set()

    legal_terms_kr = [
        "개인정보", "정보주체", "동의", "제3자 제공", "위탁", "파기", "가명정보",
        "과징금", "시정명령", "고시", "가이드라인", "시행령", "시행규칙",
        "손해배상", "근로자", "사업주", "계약", "합병", "인수", "특허",
        "상표", "저작권", "공정거래", "독점", "부정경쟁",
    ]
    legal_terms_en = [
        "compliance", "regulation", "enforcement", "penalty", "data protection",
        "personal data", "consent", "processor", "controller", "breach",
        "intellectual property", "patent", "trademark", "copyright",
        "antitrust", "merger", "acquisition",
    ]

    for term in legal_terms_kr + legal_terms_en:
        if term.lower() in sample.lower():
            candidates.add(term)

    return sorted(candidates)[:max_keywords]


def _grade_subfolder(grade: str, doc_type: str) -> str:
    """Determine the subfolder within grade-{a,b,c}/."""
    if grade == "A":
        mapping = {
            "statute": "statutes",
            "enforcement_decree": "statutes",
            "guideline": "guidelines",
            "treaty": "treaties",
        }
        return mapping.get(doc_type, "official")
    elif grade == "B":
        mapping = {
            "decision": "decisions",
            "precedent": "precedents",
            "newsletter": "commentary",
            "article": "commentary",
            "opinion": "opinions",
        }
        return mapping.get(doc_type, "misc")
    elif grade == "C":
        mapping = {
            "paper": "academic",
            "article": "academic",
        }
        return mapping.get(doc_type, "misc")
    return "misc"


def _generate_frontmatter(
    title: str,
    slug: str,
    grade: str,
    confidence: str,
    doc_type: str,
    jurisdiction: str,
    original_format: str,
    text: str,
) -> str:
    """Generate YAML frontmatter for a converted document."""
    now = datetime.now(timezone.utc).isoformat()
    date = _extract_date(text)
    keywords = _extract_keywords(text)
    articles = _extract_cited_articles(text)

    lines = [
        "---",
        f'source_id: "{grade.lower()}-{doc_type}-{slug}"',
        f'slug: "{slug}"',
        f'title_kr: "{title}"',
        f'title_en: ""',
        f'document_type: "{doc_type}"',
        f'source_grade: "{grade}"',
        f'publisher: ""',
        f'author: ""',
        f'published_date: "{date}"',
        f'source_url: ""',
        f'original_format: "{original_format}"',
        f'ingested_at: "{now}"',
        f'jurisdiction: "{jurisdiction}"',
        f"keywords: {json.dumps(keywords, ensure_ascii=False)}",
        f"topics: []",
        f"cited_articles: {json.dumps(articles, ensure_ascii=False)}",
        f"char_count: {len(text)}",
        f'verification_status: "UNVERIFIED"',
        f'grade_confidence: "{confidence}"',
        "---",
        "",
    ]
    return "\n".join(lines)


def _convert_file(md_converter, src: Path) -> tuple[str, str]:
    """Convert a file to Markdown text. Returns (text, status)."""
    if src.suffix.lower() in PASSTHROUGH_EXTENSIONS:
        return src.read_text(encoding="utf-8"), "ok"

    result = md_converter.convert(str(src))
    text = result.text_content or ""

    if len(text.strip()) < 50:
        return "", "failed"

    return text, "ok"


def _update_index(library_dir: Path, all_entries: list[dict]) -> None:
    """Update library/_index.md with grade-organized entries."""
    index_path = library_dir / "_index.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sections = {"A": [], "B": [], "C": []}

    # Collect existing entries from grade folders
    for grade_letter in ["a", "b", "c"]:
        grade_dir = library_dir / f"grade-{grade_letter}"
        if not grade_dir.exists():
            continue
        for md_file in sorted(grade_dir.rglob("*.md")):
            rel = md_file.relative_to(library_dir)
            title = _extract_title(md_file.read_text(encoding="utf-8", errors="ignore"), md_file.stem)
            sections[grade_letter.upper()].append(
                f"| {title} | | | `{rel}` | |"
            )

    # Add new entries
    for entry in all_entries:
        if entry["status"] != "ok":
            continue
        grade = entry["grade"]
        if grade not in sections:
            continue
        row = f"| {entry['title']} | {entry['doc_type']} | {entry.get('jurisdiction', '')} | `{entry['destination']}` | {entry['ingested_at'][:10]} |"
        sections[grade].append(row)

    header = f"# Library Index\n\nAuto-generated by ingest. Do not edit manually.\nLast updated: {now}\n\n"

    body = ""
    for grade, label in [("A", "Primary Sources"), ("B", "Secondary Sources"), ("C", "Academic / Reference")]:
        body += f"## Grade {grade} — {label}\n\n"
        body += "| Title | Type | Jurisdiction | File | Ingested |\n"
        body += "|:------|:-----|:-------------|:-----|:---------|\n"
        # Deduplicate by file path
        seen = set()
        for row in sections[grade]:
            file_col = row.split("|")[4].strip() if len(row.split("|")) > 4 else ""
            if file_col not in seen:
                seen.add(file_col)
                body += row + "\n"
        body += "\n"

    index_path.write_text(header + body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest library/inbox/ files into graded folders")
    parser.add_argument(
        "--library-dir",
        type=Path,
        default=Path("library"),
        help="Path to library directory (default: library/)",
    )
    parser.add_argument(
        "--knowledge-dir",
        type=Path,
        default=Path("knowledge"),
        help="Path to knowledge directory (default: knowledge/)",
    )
    args = parser.parse_args()

    library_dir: Path = args.library_dir
    knowledge_dir: Path = args.knowledge_dir
    inbox_dir = library_dir / "inbox"

    if not inbox_dir.exists():
        print(f"inbox/ directory not found at {inbox_dir}. Nothing to ingest.")
        sys.exit(0)

    # Scan inbox (exclude _processed and _failed)
    source_files = []
    for f in inbox_dir.rglob("*"):
        if not f.is_file():
            continue
        rel_to_inbox = str(f.relative_to(inbox_dir))
        if rel_to_inbox.startswith("_processed") or rel_to_inbox.startswith("_failed"):
            continue
        if f.name.startswith("."):
            continue
        source_files.append(f)

    if not source_files:
        print("inbox is empty. Nothing to ingest.")
        sys.exit(0)

    md_converter = _ensure_markitdown()
    converted_dir = knowledge_dir / CONVERTED_SUBDIR
    converted_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = inbox_dir / "_processed"
    processed_dir.mkdir(exist_ok=True)
    failed_dir = inbox_dir / "_failed"
    failed_dir.mkdir(exist_ok=True)

    print(f"Found {len(source_files)} file(s) in inbox.")

    results = []
    for src in sorted(source_files):
        ext = src.suffix.lower()

        # Check unsupported
        if ext in UNSUPPORTED_EXTENSIONS:
            print(f"  SKIP (unsupported: {ext}): {src.name} — PDF/DOCX로 변환 후 다시 넣어주세요")
            continue

        if ext not in SUPPORTED_EXTENSIONS and ext not in PASSTHROUGH_EXTENSIONS:
            print(f"  SKIP (unknown format: {ext}): {src.name}")
            continue

        # Check file size
        size_mb = src.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            print(f"  WARNING: {src.name} is {size_mb:.1f}MB (> 50MB). Skipping — confirm manually.")
            continue

        print(f"  CONVERT: {src.name} ... ", end="", flush=True)

        try:
            text, status = _convert_file(md_converter, src)
            if status == "failed" or len(text.strip()) < 50:
                print("FAILED (text too short)")
                shutil.move(str(src), str(failed_dir / src.name))
                results.append({"source": src.name, "status": "failed", "reason": "text too short"})
                continue

            # Classify
            grade, confidence = _classify_grade(text)

            if grade == "D":
                print(f"REJECTED (Grade D)")
                results.append({"source": src.name, "status": "rejected", "grade": "D"})
                shutil.move(str(src), str(failed_dir / src.name))
                continue

            if grade == "?":
                print(f"UNKNOWN GRADE (confidence: {confidence})")
                grade = "C"  # Default to C for CLI mode; agent mode asks user
                confidence = "low"

            doc_type = _detect_document_type(text, grade)
            jurisdiction = _detect_jurisdiction(text)
            title = _extract_title(text, src.stem)
            slug = _make_slug(title)

            # Generate frontmatter
            frontmatter = _generate_frontmatter(
                title, slug, grade, confidence, doc_type, jurisdiction,
                ext.lstrip("."), text,
            )
            full_content = frontmatter + text

            # Determine destination
            subfolder = _grade_subfolder(grade, doc_type)
            dest_dir = library_dir / f"grade-{grade.lower()}" / subfolder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = _unique_path(dest_dir / f"{slug}.md")
            dest_path.write_text(full_content, encoding="utf-8")

            # Copy to knowledge/library-converted/ for agent search
            converted_path = converted_dir / f"{slug}.md"
            converted_path = _unique_path(converted_path)
            converted_path.write_text(full_content, encoding="utf-8")

            # Move original to _processed
            shutil.move(str(src), str(processed_dir / src.name))

            rel_dest = dest_path.relative_to(library_dir)
            print(f"OK → grade-{grade.lower()}/{subfolder}/ [{confidence}]")

            results.append({
                "source": src.name,
                "status": "ok",
                "grade": grade,
                "confidence": confidence,
                "doc_type": doc_type,
                "jurisdiction": jurisdiction,
                "title": title,
                "destination": str(rel_dest),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
            })

        except Exception as e:
            print(f"FAILED: {e}")
            shutil.move(str(src), str(failed_dir / src.name))
            results.append({"source": src.name, "status": "failed", "reason": str(e)})

    # Update index
    _update_index(library_dir, results)

    # Summary
    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "failed"]
    rejected = [r for r in results if r["status"] == "rejected"]

    print(f"\n{'='*50}")
    print(f"Ingest complete: {len(ok)} ok, {len(failed)} failed, {len(rejected)} rejected")
    for r in ok:
        print(f"  ✅ Grade {r['grade']}: {r['source']} → {r['destination']}")
    for r in failed:
        print(f"  ❌ Failed: {r['source']} ({r.get('reason', 'unknown')})")
    for r in rejected:
        print(f"  🚫 Rejected: {r['source']} (Grade D)")

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
