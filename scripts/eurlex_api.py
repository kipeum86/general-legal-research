"""
EUR-Lex SOAP Webservice CLI wrapper for on-demand EU law retrieval.

Provides structured access to EUR-Lex SOAP API for:
  - Expert search queries (EU legislation, directives, regulations)
  - Document retrieval by CELEX number
  - Common shortcuts (GDPR, AI Act, DSA, etc.)

Usage:
    python3 scripts/eurlex_api.py search "SELECT DN, TI WHERE DN = 32016R0679"
    python3 scripts/eurlex_api.py get-document 32016R0679
    python3 scripts/eurlex_api.py search-title "General Data Protection Regulation"
    python3 scripts/eurlex_api.py search-title "artificial intelligence" --year 2024

Environment:
    EURLEX_USERNAME  — EUR-Lex webservice username
    EURLEX_PASSWORD  — EUR-Lex webservice password

Dependencies:
    pip install zeep python-dotenv
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from zeep import Client as ZeepClient
    from zeep.wsse.username import UsernameToken
except ImportError:
    print("ERROR: zeep not installed. Run: pip install zeep", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WSDL_URL = "https://eur-lex.europa.eu/EURLexWebService?wsdl"


def _load_credentials() -> tuple[str, str]:
    """Resolve EUR-Lex credentials from env vars or .env file."""
    if load_dotenv:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    username = os.environ.get("EURLEX_USERNAME")
    password = os.environ.get("EURLEX_PASSWORD")
    if not username or not password:
        print("ERROR: EURLEX_USERNAME and EURLEX_PASSWORD not set.", file=sys.stderr)
        print("Set env vars or add to .env file.", file=sys.stderr)
        sys.exit(1)
    return username, password


def _create_client(username: str, password: str) -> ZeepClient:
    """Create SOAP client with WS-Security authentication."""
    return ZeepClient(WSDL_URL, wsse=UsernameToken(username, password))


def _format_results(raw_results) -> list[dict]:
    """Parse SOAP response into clean document list."""
    if raw_results is None:
        return []

    serialized = raw_results
    if hasattr(raw_results, '__dict__'):
        from zeep.helpers import serialize_object
        serialized = serialize_object(raw_results)

    try:
        results_list = serialized["body"]["searchResults"]["result"]
        if not isinstance(results_list, list):
            results_list = [results_list]
    except (KeyError, TypeError):
        return []

    docs = []
    for item in results_list:
        try:
            content = item.get("content", {})
            notice = content.get("NOTICE", {})

            celex = notice.get("ID_CELEX", {}).get("VALUE", "")

            # Extract title
            expressions = notice.get("EXPRESSION", [])
            if not isinstance(expressions, list):
                expressions = [expressions]
            title = ""
            for expr in expressions:
                titles = expr.get("EXPRESSION_TITLE", [])
                if not isinstance(titles, list):
                    titles = [titles]
                for t in titles:
                    if t and t.get("VALUE"):
                        title = t["VALUE"].strip()
                        break
                if title:
                    break

            # Extract document links
            links = item.get("document_link", [])
            if not isinstance(links, list):
                links = [links]
            html_link = ""
            for link in links:
                if link and link.get("TYPE") == "html":
                    html_link = link.get("URL", "")
                    break

            if celex:
                docs.append({
                    "celex": celex,
                    "title": title,
                    "url": html_link,
                })
        except (KeyError, TypeError, IndexError):
            continue

    return docs


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_search(args):
    """Execute expert search query."""
    username, password = _load_credentials()
    client = _create_client(username, password)

    print(f"=== EUR-Lex Expert Search ===", file=sys.stderr)
    print(f"Query: {args.query}", file=sys.stderr)

    try:
        response = client.service.doQuery(
            expertQuery=args.query,
            page=args.page,
            pageSize=args.page_size,
            searchLanguage=args.lang,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    docs = _format_results(response)

    print(f"=== EUR-Lex 검색 결과 ({len(docs)}건) ===\n")
    for doc in docs:
        print(f"  [{doc['celex']}] {doc['title']}")
        if doc['url']:
            print(f"    URL: {doc['url']}")
        print()

    if not docs:
        print("  (검색 결과 없음)")


def cmd_get_document(args):
    """Get document by CELEX number."""
    username, password = _load_credentials()
    client = _create_client(username, password)

    celex = args.celex
    query = f"DN = '{celex}'"

    print(f"=== EUR-Lex Document: {celex} ===", file=sys.stderr)

    try:
        response = client.service.doQuery(
            expertQuery=query,
            page=1,
            pageSize=1,
            searchLanguage=args.lang,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    docs = _format_results(response)

    if docs:
        doc = docs[0]
        print(f"=== {doc['title']} ===")
        print(f"CELEX: {doc['celex']}")
        if doc['url']:
            print(f"URL: {doc['url']}")
    else:
        print(f"ERROR: Document {celex} not found", file=sys.stderr)


def cmd_search_title(args):
    """Search by title keywords."""
    username, password = _load_credentials()
    client = _create_client(username, password)

    # Build expert query for title search
    words = args.keywords.split()
    title_clause = " AND ".join(f"TI ~ {w}" for w in words)
    query = f"SELECT DN, TI WHERE {title_clause}"

    if args.year:
        query += f" AND DD >= {args.year}0101"

    if args.doc_type:
        type_map = {
            "regulation": "R",
            "directive": "L",
            "decision": "D",
        }
        code = type_map.get(args.doc_type.lower(), args.doc_type)
        query += f" AND FM = {code}"

    print(f"=== EUR-Lex Title Search ===", file=sys.stderr)
    print(f"Query: {query}", file=sys.stderr)

    try:
        response = client.service.doQuery(
            expertQuery=query,
            page=args.page,
            pageSize=args.page_size,
            searchLanguage=args.lang,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    docs = _format_results(response)

    print(f"=== EUR-Lex 제목 검색 결과 ({len(docs)}건) ===\n")
    for doc in docs:
        print(f"  [{doc['celex']}] {doc['title']}")
        if doc['url']:
            print(f"    URL: {doc['url']}")
        print()

    if not docs:
        print("  (검색 결과 없음)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

EXPERT_QUERY_HELP = """
EUR-Lex Expert Query Syntax examples:
  DN = '32016R0679'                          — GDPR by CELEX
  DN = 32024R*                               — All 2024 regulations
  TI ~ 'artificial intelligence'             — Title contains phrase
  SELECT DN, TI WHERE TI ~ data AND DD >= 20240101  — Title + date filter
  FM = R AND DD >= 20230101                  — Regulations from 2023+

Common CELEX prefixes:
  3 = EU secondary legislation (regulations, directives, decisions)
  1 = Treaties
  6 = Case law (CJEU)

Document type codes (FM):
  R = Regulation, L = Directive, D = Decision
"""


def main():
    parser = argparse.ArgumentParser(
        description="EUR-Lex SOAP API CLI wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXPERT_QUERY_HELP,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- search --
    p = sub.add_parser("search", help="Expert search query (raw EUR-Lex syntax)")
    p.add_argument("query", help="EUR-Lex expert query string")
    p.add_argument("--lang", default="en", help="Search language (default: en)")
    p.add_argument("--page", type=int, default=1, help="Page number")
    p.add_argument("--page-size", type=int, default=10, help="Results per page")
    p.set_defaults(func=cmd_search)

    # -- get-document --
    p = sub.add_parser("get-document", help="Get document by CELEX number")
    p.add_argument("celex", help="CELEX number (e.g., 32016R0679 for GDPR)")
    p.add_argument("--lang", default="en", help="Language (default: en)")
    p.set_defaults(func=cmd_get_document)

    # -- search-title --
    p = sub.add_parser("search-title", help="Search by title keywords")
    p.add_argument("keywords", help="Title keywords (e.g., 'artificial intelligence')")
    p.add_argument("--year", help="Filter from year (e.g., 2024)")
    p.add_argument("--doc-type", choices=["regulation", "directive", "decision"],
                    help="Document type filter")
    p.add_argument("--lang", default="en", help="Language (default: en)")
    p.add_argument("--page", type=int, default=1, help="Page number")
    p.add_argument("--page-size", type=int, default=10, help="Results per page")
    p.set_defaults(func=cmd_search_title)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
