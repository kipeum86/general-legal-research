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

    print(f"=== {name} ===")
    print(f"법종: {kind} | 소관: {ministry}")
    print(f"공포: {promulgate_date} (제{promulgate_no}호) | 시행: {enforce_date}")
    print("=" * 60)

    # Articles — XML uses <조문단위> with nested <항>, <호>, <목>
    for jo in root.iter("조문단위"):
        jo_no = _text(jo, "조문번호")
        jo_title = _text(jo, "조문제목")
        jo_content = _text(jo, "조문내용")
        jo_enforce = _text(jo, "조문시행일자")

        header = f"\n제{jo_no}조"
        if jo_title:
            header += f"({jo_title})"
        if jo_enforce:
            header += f"  [시행 {jo_enforce}]"
        print(header)
        if jo_content:
            print(jo_content)

        # 항 (paragraphs)
        for hang in jo.findall("항"):
            hang_no = _text(hang, "항번호")
            hang_content = _text(hang, "항내용")
            if hang_content:
                print(f"  {hang_content}")

            # 호 (clauses) within 항
            for ho in hang.findall("호"):
                ho_content = _text(ho, "호내용")
                if ho_content:
                    print(f"    {ho_content}")

                # 목 (items) within 호
                for mok in ho.findall("목"):
                    mok_content = _text(mok, "목내용")
                    if mok_content:
                        print(f"      {mok_content}")

    # 부칙 (Supplementary provisions)
    for buchik in root.iter("부칙단위"):
        buchik_date = _text(buchik, "공포일자")
        buchik_no = _text(buchik, "공포번호")
        buchik_content = _text(buchik, "부칙내용")
        if buchik_content:
            print(f"\n[부칙] ({buchik_date}, 제{buchik_no}호)")
            print(buchik_content)
        # Also check 항 within 부칙
        for hang in buchik.findall("항"):
            hang_content = _text(hang, "항내용")
            if hang_content:
                print(f"  {hang_content}")


def cmd_get_article(args):
    """Get specific article text by fetching full law and filtering."""
    oc = _load_oc()
    # Fetch full law text, then filter to target article
    url = _build_service_url("law", oc, ID=args.id)
    root = _fetch_xml(url)

    name = _text(root, "기본정보/법령명_한글") or _text(root, "법령명_한글")
    ministry = _text(root, "기본정보/소관부처") or _text(root, "소관부처")
    target_no = str(args.article)

    found = False
    for jo in root.iter("조문단위"):
        jo_no = _text(jo, "조문번호")
        if jo_no != target_no:
            continue
        found = True
        jo_title = _text(jo, "조문제목")
        jo_content = _text(jo, "조문내용")
        jo_enforce = _text(jo, "조문시행일자")

        print(f"=== {name} 제{jo_no}조({jo_title}) ===")
        print(f"시행일: {jo_enforce} | 소관: {ministry}")
        print("-" * 40)

        if jo_content:
            print(jo_content)

        for hang in jo.findall("항"):
            hang_content = _text(hang, "항내용")
            if hang_content:
                print(f"  {hang_content}")

            for ho in hang.findall("호"):
                ho_content = _text(ho, "호내용")
                if ho_content:
                    print(f"    {ho_content}")

                for mok in ho.findall("목"):
                    mok_content = _text(mok, "목내용")
                    if mok_content:
                        print(f"      {mok_content}")
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
    p.set_defaults(func=cmd_get_law)

    # -- get-article --
    p = sub.add_parser("get-article", help="특정 조문 조회")
    p.add_argument("--id", required=True, help="법령 ID")
    p.add_argument("--article", type=int, required=True, help="조문 번호 (예: 17)")
    p.add_argument("--paragraph", type=int, help="항 번호")
    p.add_argument("--clause", type=int, help="호 번호")
    p.add_argument("--item", help="목 (가, 나, 다...)")
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
