"""
Korean Open Law API (열린법령 API) CLI wrapper for on-demand legal research.

Provides structured access to law.go.kr's DRF API for:
  - Law search & full text retrieval
  - Article-level text lookup
  - Case law search & full text
  - Legal interpretations search

Usage:
    python3 scripts/open_law_api.py search-law "개인정보 보호법"
    python3 scripts/open_law_api.py get-law --id 001823
    python3 scripts/open_law_api.py get-law --mst 262575
    python3 scripts/open_law_api.py get-article --id 001823 --article 17
    python3 scripts/open_law_api.py search-cases "개인정보 유출"
    python3 scripts/open_law_api.py get-case --id 228541
    python3 scripts/open_law_api.py search-interpretations "자동차"

Environment:
    OPEN_LAW_OC  — API key (OC parameter). Falls back to .env file in project root.

No external dependencies — uses only Python standard library.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_SEARCH = "http://www.law.go.kr/DRF/lawSearch.do"
BASE_SERVICE = "http://www.law.go.kr/DRF/lawService.do"
DEFAULT_DISPLAY = 20
MAX_DISPLAY = 100
REQUEST_TIMEOUT = 30  # seconds


def _load_oc() -> str:
    """Resolve OC key from env var or .env file."""
    oc = os.environ.get("OPEN_LAW_OC")
    if oc:
        return oc
    # Try .env in project root
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPEN_LAW_OC=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("ERROR: OPEN_LAW_OC not set. Set env var or add to .env file.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# API call helpers
# ---------------------------------------------------------------------------

def _fetch_xml(url: str) -> ET.Element:
    """Fetch URL and parse as XML. Returns root Element."""
    req = urllib.request.Request(url, headers={"User-Agent": "LegalResearchAgent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} for {url}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed — {e.reason}", file=sys.stderr)
        sys.exit(1)
    return ET.fromstring(data)


def _build_search_url(target: str, oc: str, **kwargs) -> str:
    params = {"OC": oc, "target": target, "type": "XML"}
    params.update({k: v for k, v in kwargs.items() if v is not None})
    return f"{BASE_SEARCH}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"


def _build_service_url(target: str, oc: str, **kwargs) -> str:
    params = {"OC": oc, "target": target, "type": "XML"}
    params.update({k: v for k, v in kwargs.items() if v is not None})
    return f"{BASE_SERVICE}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"


def _text(el: ET.Element | None, tag: str) -> str:
    """Safely extract text from child element."""
    if el is None:
        return ""
    child = el.find(tag)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def _pad6(n: int) -> str:
    """Pad article/paragraph/clause number to 6 digits."""
    return str(n).zfill(6)


def _slugify_law_name(name: str) -> str:
    """Create a filesystem-safe directory name from a Korean law name.

    Keeps Korean characters, digits, and hyphens. Replaces whitespace/special
    chars with hyphens and collapses consecutive hyphens.
    """
    slug = re.sub(r"[^\w가-힣-]", "-", name)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "unknown-law"


def _normalize_kr_article_id(value: str | int) -> str:
    """Normalize Korean article identifiers like 17 or 39의3."""
    raw = str(value).strip()
    match = re.fullmatch(r"(?:제\s*)?(\d+)(?:조)?(?:의\s*(\d+))?", raw)
    if not match:
        return raw
    base = int(match.group(1))
    suffix = int(match.group(2)) if match.group(2) else None
    return str(base) if suffix is None else f"{base}의{suffix}"


def _kr_article_fields(value: str | int) -> dict:
    article_id = _normalize_kr_article_id(value)
    match = re.fullmatch(r"(\d+)(?:의(\d+))?", article_id)
    if not match:
        raise ValueError(f"Unsupported article identifier: {value!r}")
    base = int(match.group(1))
    suffix = int(match.group(2)) if match.group(2) else None
    return {
        "article_number": base,
        "article_id": article_id,
        **({"article_suffix": suffix} if suffix is not None else {}),
    }


def _save_law_articles(
    law_name: str,
    source_id: str,
    articles_data: list[dict],
    *,
    replace_existing: bool,
) -> str:
    """Persist articles to library/grade-a/ using legal_store.

    Returns the law_dir name used.
    """
    from legal_store import save_law_articles

    law_dir = _slugify_law_name(law_name)
    save_law_articles(
        law_name=law_name,
        law_dir=law_dir,
        jurisdiction="KR",
        source="law.go.kr",
        source_id=source_id,
        articles=articles_data,
        replace_existing=replace_existing,
    )

    return law_dir


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_search_law(args):
    """Search laws by keyword."""
    oc = _load_oc()
    url = _build_search_url(
        "law", oc,
        query=args.query,
        display=str(min(args.display, MAX_DISPLAY)),
        page=str(args.page),
        sort=args.sort or "efYd",
    )
    root = _fetch_xml(url)

    total = _text(root, "totalCnt")
    print(f"=== 법령 검색 결과 (총 {total}건, {args.page}페이지) ===\n")

    for item in root.iter("law"):
        law_id = _text(item, "법령ID")
        mst = _text(item, "법령일련번호")
        name = _text(item, "법령명한글")
        kind = _text(item, "법종구분")
        ministry = _text(item, "소관부처명")
        enforce_date = _text(item, "시행일자")
        promulgate_date = _text(item, "공포일자")
        amend_type = _text(item, "제개정구분명")

        print(f"  [{law_id}] {name}")
        print(f"    MST: {mst} | 법종: {kind} | 소관: {ministry}")
        print(f"    시행일: {enforce_date} | 공포일: {promulgate_date} | {amend_type}")
        print()

    if total == "0":
        print("  (검색 결과 없음)")


def cmd_get_law(args):
    """Get full text of a specific law."""
    oc = _load_oc()
    kwargs = {}
    if args.id:
        kwargs["ID"] = args.id
    elif args.mst:
        kwargs["MST"] = args.mst
    else:
        print("ERROR: --id or --mst required", file=sys.stderr)
        sys.exit(1)

    url = _build_service_url("law", oc, **kwargs)
    root = _fetch_xml(url)

    # Law metadata
    name = _text(root, "기본정보/법령명_한글") or _text(root, "법령명_한글")
    kind = _text(root, "기본정보/법종구분") or _text(root, "법종구분")
    promulgate_no = _text(root, "기본정보/공포번호") or _text(root, "공포번호")
    promulgate_date = _text(root, "기본정보/공포일자") or _text(root, "공포일자")
    enforce_date = _text(root, "기본정보/시행일자") or _text(root, "시행일자")
    ministry = _text(root, "기본정보/소관부처명") or _text(root, "소관부처명")

    source_id = args.id or args.mst or ""

    # Collect structured article data
    articles_data = []
    for jo in root.iter("조문단위"):
        jo_no = _text(jo, "조문번호")
        jo_title = _text(jo, "조문제목")
        jo_content = _text(jo, "조문내용")
        jo_enforce = _text(jo, "조문시행일자")

        # Build full content string (article + paragraphs + clauses + items)
        content_parts = []
        if jo_content:
            content_parts.append(jo_content)

        paragraphs = []
        for hang in jo.findall("항"):
            hang_no = _text(hang, "항번호")
            hang_content = _text(hang, "항내용")
            clauses = []
            for ho in hang.findall("호"):
                ho_content = _text(ho, "호내용")
                items = []
                for mok in ho.findall("목"):
                    mok_content = _text(mok, "목내용")
                    if mok_content:
                        items.append(mok_content)
                if ho_content:
                    clause_entry = {"content": ho_content}
                    if items:
                        clause_entry["items"] = items
                    clauses.append(clause_entry)
            para_entry = {}
            if hang_no:
                para_entry["number"] = hang_no
            if hang_content:
                para_entry["content"] = hang_content
                content_parts.append(f"  {hang_content}")
            if clauses:
                para_entry["clauses"] = clauses
                for cl in clauses:
                    content_parts.append(f"    {cl['content']}")
                    for it in cl.get("items", []):
                        content_parts.append(f"      {it}")
            if para_entry:
                paragraphs.append(para_entry)

        article_fields = _kr_article_fields(jo_no)

        article_record = {
            **article_fields,
            "title": jo_title,
            "content": "\n".join(content_parts),
            "enforce_date": jo_enforce,
        }
        if paragraphs:
            article_record["paragraphs"] = paragraphs
        articles_data.append(article_record)

    # Collect 부칙 (supplementary provisions)
    buchik_data = []
    for buchik in root.iter("부칙단위"):
        buchik_date = _text(buchik, "공포일자")
        buchik_no = _text(buchik, "공포번호")
        buchik_content = _text(buchik, "부칙내용")
        buchik_hangs = []
        for hang in buchik.findall("항"):
            hang_content = _text(hang, "항내용")
            if hang_content:
                buchik_hangs.append(hang_content)
        if buchik_content or buchik_hangs:
            buchik_data.append({
                "date": buchik_date,
                "number": buchik_no,
                "content": buchik_content,
                "paragraphs": buchik_hangs,
            })

    # --json output
    if getattr(args, "json", False):
        output = {
            "law_name": name,
            "kind": kind,
            "ministry": ministry,
            "promulgate_date": promulgate_date,
            "promulgate_no": promulgate_no,
            "enforce_date": enforce_date,
            "source_id": source_id,
            "articles": articles_data,
            "supplementary_provisions": buchik_data,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # Default human-readable output (preserves original behavior)
        print(f"=== {name} ===")
        print(f"법종: {kind} | 소관: {ministry}")
        print(f"공포: {promulgate_date} (제{promulgate_no}호) | 시행: {enforce_date}")
        print("=" * 60)

        for art in articles_data:
            jo_no = art["article_id"]
            jo_title = art["title"]
            jo_enforce = art.get("enforce_date", "")
            header = f"\n제{jo_no}조"
            if jo_title:
                header += f"({jo_title})"
            if jo_enforce:
                header += f"  [시행 {jo_enforce}]"
            print(header)
            if art["content"]:
                print(art["content"])

        for b in buchik_data:
            if b["content"]:
                print(f"\n[부칙] ({b['date']}, 제{b['number']}호)")
                print(b["content"])
            for h in b.get("paragraphs", []):
                print(f"  {h}")

    # --save to library/grade-a/
    if getattr(args, "save", False):
        from legal_store import StoreError

        try:
            law_dir = _save_law_articles(name, source_id, articles_data, replace_existing=True)
        except StoreError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"\n[Saved] {len(articles_data)} articles → library/grade-a/{law_dir}/", file=sys.stderr)


def cmd_get_article(args):
    """Get specific article text by fetching full law and filtering."""
    oc = _load_oc()
    # Fetch full law text, then filter to target article
    url = _build_service_url("law", oc, ID=args.id)
    root = _fetch_xml(url)

    name = _text(root, "기본정보/법령명_한글") or _text(root, "법령명_한글")
    ministry = _text(root, "기본정보/소관부처") or _text(root, "소관부처")
    target_no = _normalize_kr_article_id(args.article)

    found = False
    for jo in root.iter("조문단위"):
        jo_no = _text(jo, "조문번호")
        jo_article_id = _normalize_kr_article_id(jo_no)
        if jo_article_id != target_no:
            continue
        found = True
        jo_title = _text(jo, "조문제목")
        jo_content = _text(jo, "조문내용")
        jo_enforce = _text(jo, "조문시행일자")

        # Build structured data
        content_parts = []
        if jo_content:
            content_parts.append(jo_content)

        paragraphs = []
        for hang in jo.findall("항"):
            hang_no = _text(hang, "항번호")
            hang_content = _text(hang, "항내용")
            clauses = []
            for ho in hang.findall("호"):
                ho_content = _text(ho, "호내용")
                items = []
                for mok in ho.findall("목"):
                    mok_content = _text(mok, "목내용")
                    if mok_content:
                        items.append(mok_content)
                if ho_content:
                    clause_entry = {"content": ho_content}
                    if items:
                        clause_entry["items"] = items
                    clauses.append(clause_entry)
            para_entry = {}
            if hang_no:
                para_entry["number"] = hang_no
            if hang_content:
                para_entry["content"] = hang_content
                content_parts.append(f"  {hang_content}")
            if clauses:
                para_entry["clauses"] = clauses
                for cl in clauses:
                    content_parts.append(f"    {cl['content']}")
                    for it in cl.get("items", []):
                        content_parts.append(f"      {it}")
            if para_entry:
                paragraphs.append(para_entry)

        article_data = {
            "law_name": name,
            **_kr_article_fields(jo_no),
            "title": jo_title,
            "content": "\n".join(content_parts),
            "enforce_date": jo_enforce,
            "ministry": ministry,
            "source_id": args.id,
        }
        if paragraphs:
            article_data["paragraphs"] = paragraphs

        # --json output
        if getattr(args, "json", False):
            print(json.dumps(article_data, ensure_ascii=False, indent=2))
        else:
            # Default human-readable output
            print(f"=== {name} 제{jo_no}조({jo_title}) ===")
            print(f"시행일: {jo_enforce} | 소관: {ministry}")
            print("-" * 40)
            if article_data["content"]:
                print(article_data["content"])

        # --save single article
        if getattr(args, "save", False):
            from legal_store import StoreError

            try:
                law_dir = _save_law_articles(name, args.id, [article_data], replace_existing=False)
            except StoreError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                sys.exit(1)
            print(f"\n[Saved] 1 article → library/grade-a/{law_dir}/", file=sys.stderr)

        break

    if not found:
        print(f"ERROR: 제{args.article}조를 찾을 수 없습니다 (법령 ID: {args.id})", file=sys.stderr)


def cmd_search_cases(args):
    """Search case law."""
    oc = _load_oc()
    kwargs = {
        "query": args.query,
        "display": str(min(args.display, MAX_DISPLAY)),
        "page": str(args.page),
        "search": "2" if args.fulltext else "1",
    }
    if args.court:
        kwargs["org"] = args.court
    if args.date_range:
        kwargs["prncYd"] = args.date_range

    url = _build_search_url("prec", oc, **kwargs)
    root = _fetch_xml(url)

    total = _text(root, "totalCnt")
    print(f"=== 판례 검색 결과 (총 {total}건, {args.page}페이지) ===\n")

    for item in root.iter("prec"):
        prec_id = _text(item, "판례일련번호")
        case_name = _text(item, "사건명")
        case_no = _text(item, "사건번호")
        court = _text(item, "법원명")
        date = _text(item, "선고일자")
        judgment_type = _text(item, "판결유형")

        print(f"  [{prec_id}] {case_name}")
        print(f"    사건번호: {case_no} | {court} | {date} | {judgment_type}")
        print()

    if total == "0":
        print("  (검색 결과 없음)")


def cmd_get_case(args):
    """Get full case text."""
    oc = _load_oc()
    url = _build_service_url("prec", oc, ID=args.id)
    root = _fetch_xml(url)

    case_name = _text(root, "사건명")
    case_no = _text(root, "사건번호")
    court = _text(root, "법원명")
    date = _text(root, "선고일자")
    case_type = _text(root, "사건종류명")
    judgment_type = _text(root, "판결유형")
    holdings = _text(root, "판시사항")
    summary = _text(root, "판결요지")
    ref_articles = _text(root, "참조조문")
    ref_cases = _text(root, "참조판례")
    full_text = _text(root, "판례내용")

    case_data = {
        "case_name": case_name,
        "case_no": case_no,
        "court": court,
        "date": date,
        "case_type": case_type,
        "judgment_type": judgment_type,
        "holdings": holdings,
        "summary": summary,
        "ref_articles": ref_articles,
        "ref_cases": ref_cases,
        "full_text": full_text,
        "source_id": args.id,
    }

    # --json output
    if getattr(args, "json", False):
        print(json.dumps(case_data, ensure_ascii=False, indent=2))
    else:
        # Default human-readable output
        print(f"=== {case_name} ===")
        print(f"사건번호: {case_no} | {court} | {date}")
        print(f"사건종류: {case_type} | 판결유형: {judgment_type}")
        print("=" * 60)

        if holdings:
            print(f"\n[판시사항]\n{holdings}")
        if summary:
            print(f"\n[판결요지]\n{summary}")
        if ref_articles:
            print(f"\n[참조조문] {ref_articles}")
        if ref_cases:
            print(f"\n[참조판례] {ref_cases}")
        if full_text:
            print(f"\n[판례내용]\n{full_text}")

    # --save: cases are not articles — save as JSON to library/grade-a/
    if getattr(args, "save", False):
        from legal_store import StoreError, save_case_json

        safe_id = re.sub(r"[^\w-]", "_", args.id)
        try:
            case_path = save_case_json(case_id=safe_id, payload=case_data)
        except StoreError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"\n[Saved] case → {case_path}", file=sys.stderr)


def cmd_search_interpretations(args):
    """Search legal interpretations (법령해석례)."""
    oc = _load_oc()
    url = _build_search_url(
        "expc", oc,
        query=args.query,
        display=str(min(args.display, MAX_DISPLAY)),
        page=str(args.page),
    )
    root = _fetch_xml(url)

    total = _text(root, "totalCnt")
    print(f"=== 법령해석례 검색 결과 (총 {total}건, {args.page}페이지) ===\n")

    for item in root.iter("expc"):
        expc_id = _text(item, "법령해석례일련번호")
        case_name = _text(item, "안건명")
        case_no = _text(item, "안건번호")
        inquiry_agency = _text(item, "질의기관명")
        reply_agency = _text(item, "회신기관명")
        reply_date = _text(item, "회신일자")

        print(f"  [{expc_id}] {case_name}")
        print(f"    안건번호: {case_no} | 질의: {inquiry_agency} → 회신: {reply_agency} | {reply_date}")
        print()

    if total == "0":
        print("  (검색 결과 없음)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Korean Open Law API (열린법령 API) CLI wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- search-law --
    p = sub.add_parser("search-law", help="법령 키워드 검색")
    p.add_argument("query", help="검색 키워드")
    p.add_argument("--display", type=int, default=DEFAULT_DISPLAY, help="결과 수 (max 100)")
    p.add_argument("--page", type=int, default=1, help="페이지 번호")
    p.add_argument("--sort", choices=["lasc", "ldes", "dasc", "ddes", "efYd"], default="efYd",
                    help="정렬 (efYd=시행일순)")
    p.set_defaults(func=cmd_search_law)

    # -- get-law --
    p = sub.add_parser("get-law", help="법령 본문 조회 (ID 또는 MST)")
    p.add_argument("--id", help="법령 ID")
    p.add_argument("--mst", help="법령 일련번호 (MST)")
    p.add_argument("--json", action="store_true", help="Output structured JSON")
    p.add_argument("--save", action="store_true", help="Save to library/grade-a/ cache")
    p.set_defaults(func=cmd_get_law)

    # -- get-article --
    p = sub.add_parser("get-article", help="특정 조문 조회")
    p.add_argument("--id", required=True, help="법령 ID")
    p.add_argument("--article", required=True, help="조문 번호 (예: 17, 39의3)")
    p.add_argument("--paragraph", type=int, help="항 번호")
    p.add_argument("--clause", type=int, help="호 번호")
    p.add_argument("--item", help="목 (가, 나, 다...)")
    p.add_argument("--json", action="store_true", help="Output structured JSON")
    p.add_argument("--save", action="store_true", help="Save to library/grade-a/ cache")
    p.set_defaults(func=cmd_get_article)

    # -- search-cases --
    p = sub.add_parser("search-cases", help="판례 키워드 검색")
    p.add_argument("query", help="검색 키워드")
    p.add_argument("--display", type=int, default=DEFAULT_DISPLAY, help="결과 수 (max 100)")
    p.add_argument("--page", type=int, default=1, help="페이지 번호")
    p.add_argument("--fulltext", action="store_true", help="전문 검색 (기본: 사건명)")
    p.add_argument("--court", help="법원 코드 (400201=대법원, 400202=하급심)")
    p.add_argument("--date-range", help="선고일 범위 (예: 20200101~20231231)")
    p.set_defaults(func=cmd_search_cases)

    # -- get-case --
    p = sub.add_parser("get-case", help="판례 본문 조회")
    p.add_argument("--id", required=True, help="판례 일련번호")
    p.add_argument("--json", action="store_true", help="Output structured JSON")
    p.add_argument("--save", action="store_true", help="Save to library/grade-a/ cache")
    p.set_defaults(func=cmd_get_case)

    # -- search-interpretations --
    p = sub.add_parser("search-interpretations", help="법령해석례 검색")
    p.add_argument("query", help="검색 키워드")
    p.add_argument("--display", type=int, default=DEFAULT_DISPLAY, help="결과 수 (max 100)")
    p.add_argument("--page", type=int, default=1, help="페이지 번호")
    p.set_defaults(func=cmd_search_interpretations)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
