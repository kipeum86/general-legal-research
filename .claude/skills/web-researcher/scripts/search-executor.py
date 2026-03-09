#!/usr/bin/env python3
"""MCP-backed legal source collector with fallback chain.

Fallback order:
1) tavily-mcp
2) brave-search-mcp
3) fetch-mcp (direct URL fetch from curated list)
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


DEFAULT_PROTOCOL_VERSION = "2024-11-05"
CLIENT_INFO = {"name": "game-legal-research-agent", "version": "0.1.0"}


class MCPError(RuntimeError):
    pass


def _safe_json_dumps(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    return header + body


def _read_one_mcp_message(stream) -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = stream.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        decoded = line.decode("ascii", errors="replace")
        if ":" not in decoded:
            continue
        key, value = decoded.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None
    body = stream.read(content_length)
    if not body:
        return None
    return json.loads(body.decode("utf-8", errors="replace"))


class MCPClient:
    def __init__(self, command: str, startup_timeout_sec: float = 8.0) -> None:
        if not command.strip():
            raise MCPError("Empty MCP server command")
        self.command = command
        self.proc: subprocess.Popen[bytes] | None = None
        self._incoming: queue.Queue[dict[str, Any]] = queue.Queue()
        self._reader: threading.Thread | None = None
        self._req_id = 0
        self._startup_timeout_sec = startup_timeout_sec

    def __enter__(self) -> "MCPClient":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def start(self) -> None:
        if self.proc is not None:
            return
        parts = shlex.split(self.command, posix=(os.name != "nt"))
        self.proc = subprocess.Popen(
            parts,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=False,
            bufsize=0,
        )
        self._reader = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader.start()
        self.initialize(timeout_sec=self._startup_timeout_sec)

    def close(self) -> None:
        if self.proc is None:
            return
        try:
            self.proc.terminate()
            self.proc.wait(timeout=2)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass
        finally:
            self.proc = None

    def _reader_loop(self) -> None:
        assert self.proc is not None
        assert self.proc.stdout is not None
        while True:
            try:
                message = _read_one_mcp_message(self.proc.stdout)
            except Exception:
                break
            if message is None:
                break
            self._incoming.put(message)

    def _send_payload(self, payload: dict[str, Any]) -> None:
        if self.proc is None or self.proc.stdin is None:
            raise MCPError("MCP process not running")
        raw = _safe_json_dumps(payload)
        self.proc.stdin.write(raw)
        self.proc.stdin.flush()

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._send_payload(payload)

    def request(
        self, method: str, params: dict[str, Any] | None = None, timeout_sec: float = 15.0
    ) -> dict[str, Any]:
        self._req_id += 1
        req_id = self._req_id
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._send_payload(payload)

        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            remaining = max(0.0, deadline - time.time())
            try:
                msg = self._incoming.get(timeout=remaining)
            except queue.Empty as exc:
                raise MCPError(f"Timeout waiting for {method}") from exc
            if msg.get("id") != req_id:
                continue
            if "error" in msg:
                raise MCPError(f"{method} failed: {msg['error']}")
            result = msg.get("result")
            if isinstance(result, dict):
                return result
            return {"result": result}
        raise MCPError(f"Timeout waiting for {method}")

    def initialize(self, timeout_sec: float = 15.0) -> None:
        self.request(
            "initialize",
            {
                "protocolVersion": DEFAULT_PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "clientInfo": CLIENT_INFO,
            },
            timeout_sec=timeout_sec,
        )
        self.notify("notifications/initialized", {})

    def list_tools(self) -> list[dict[str, Any]]:
        result = self.request("tools/list", {}, timeout_sec=10.0)
        tools = result.get("tools", [])
        if not isinstance(tools, list):
            return []
        return [t for t in tools if isinstance(t, dict)]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.request("tools/call", {"name": name, "arguments": arguments}, timeout_sec=25.0)


def _pick_tool_name(tools: list[dict[str, Any]], preferred: list[str]) -> str | None:
    names = [str(t.get("name", "")) for t in tools]
    lowered = {n.lower(): n for n in names if n}
    for want in preferred:
        key = want.lower()
        if key in lowered:
            return lowered[key]
    for n in names:
        ln = n.lower()
        if any(token in ln for token in ("search", "web", "query", "fetch", "url")):
            return n
    return names[0] if names else None


def _parse_text_json(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return value


def _extract_payload(result: dict[str, Any]) -> Any:
    if "structuredContent" in result:
        return result["structuredContent"]
    content = result.get("content")
    if isinstance(content, list):
        texts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_val = block.get("text")
                if isinstance(text_val, str):
                    texts.append(text_val)
        if len(texts) == 1:
            return _parse_text_json(texts[0])
        if texts:
            parsed = [_parse_text_json(t) for t in texts]
            return parsed
    return result


def _as_result_rows(payload: Any, max_results: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add_row(raw: Any) -> None:
        if len(rows) >= max_results:
            return
        if isinstance(raw, str):
            rows.append({"title": "", "url": "", "snippet": raw, "raw": raw})
            return
        if not isinstance(raw, dict):
            rows.append({"title": "", "url": "", "snippet": str(raw), "raw": raw})
            return
        url = str(
            raw.get("url")
            or raw.get("link")
            or raw.get("href")
            or raw.get("source")
            or raw.get("permalink")
            or ""
        )
        title = str(raw.get("title") or raw.get("name") or raw.get("headline") or "")
        snippet = str(
            raw.get("snippet")
            or raw.get("description")
            or raw.get("content")
            or raw.get("text")
            or ""
        )
        rows.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet[:1200],
                "raw": raw,
            }
        )

    if isinstance(payload, dict):
        for key in ("results", "items", "data", "documents", "hits"):
            value = payload.get(key)
            if isinstance(value, list):
                for item in value:
                    add_row(item)
                if rows:
                    return rows[:max_results]
        add_row(payload)
        return rows[:max_results]

    if isinstance(payload, list):
        for item in payload:
            add_row(item)
        return rows[:max_results]

    add_row(payload)
    return rows[:max_results]


def _read_urls_from_markdown(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    urls = re.findall(r"https?://[^\s)>\"]+", text)
    dedup: list[str] = []
    seen: set[str] = set()
    for url in urls:
        cleaned = url.rstrip(".,;")
        if cleaned not in seen:
            seen.add(cleaned)
            dedup.append(cleaned)
    return dedup


def _call_search_tool(
    client: MCPClient, tool_name: str, query: str, max_results: int
) -> tuple[list[dict[str, Any]], str]:
    arg_sets = [
        {"query": query, "max_results": max_results},
        {"query": query, "limit": max_results},
        {"search_query": query, "max_results": max_results},
        {"q": query, "count": max_results},
        {"query": query},
    ]
    errors: list[str] = []
    for args in arg_sets:
        try:
            result = client.call_tool(tool_name, args)
            payload = _extract_payload(result)
            rows = _as_result_rows(payload, max_results=max_results)
            return rows, ""
        except Exception as exc:
            errors.append(str(exc))
    return [], "; ".join(errors)


def _call_fetch_tool(
    client: MCPClient, tool_name: str, urls: list[str], max_results: int
) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for url in urls[:max_results]:
        arg_sets = [{"url": url}, {"uri": url}, {"link": url}]
        ok = False
        for args in arg_sets:
            try:
                result = client.call_tool(tool_name, args)
                payload = _extract_payload(result)
                snippet = ""
                if isinstance(payload, dict):
                    snippet = str(payload.get("content") or payload.get("text") or payload)[:1200]
                elif isinstance(payload, list):
                    snippet = json.dumps(payload, ensure_ascii=False)[:1200]
                else:
                    snippet = str(payload)[:1200]
                rows.append({"title": "", "url": url, "snippet": snippet, "raw": payload})
                ok = True
                break
            except Exception as exc:
                errors.append(f"{url}: {exc}")
        if not ok:
            continue
    return rows, errors


def _run_with_server(
    server_name: str,
    server_cmd: str,
    query: str,
    max_results: int,
    source_urls: list[str],
) -> tuple[list[dict[str, Any]], str]:
    preferred_map = {
        "tavily-mcp": ["tavily_search", "search", "tavily-search", "web_search"],
        "brave-search-mcp": ["brave_web_search", "search", "web_search"],
        "fetch-mcp": ["fetch", "read_url", "get_url"],
    }
    with MCPClient(server_cmd) as client:
        tools = client.list_tools()
        preferred = preferred_map.get(server_name, ["search", "fetch"])
        tool_name = _pick_tool_name(tools, preferred)
        if not tool_name:
            raise MCPError(f"{server_name}: no callable tools found")
        if server_name == "fetch-mcp":
            rows, errors = _call_fetch_tool(client, tool_name, source_urls, max_results=max_results)
            return rows, "; ".join(errors)
        rows, err = _call_search_tool(client, tool_name, query, max_results=max_results)
        return rows, err


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MCP search fallback chain")
    parser.add_argument("query", help="Search query text")
    parser.add_argument("--max-results", type=int, default=8)
    parser.add_argument(
        "--source-urls-file",
        default=str(
            Path(__file__).resolve().parents[1]
            / "references"
            / "legal-source-urls.md"
        ),
    )
    parser.add_argument(
        "--tavily-cmd",
        default=os.getenv("TAVILY_MCP_SERVER_CMD", "tavily-mcp").strip(),
        help="Command to start tavily MCP server",
    )
    parser.add_argument(
        "--brave-cmd",
        default=os.getenv("BRAVE_MCP_SERVER_CMD", "brave-search-mcp").strip(),
        help="Command to start brave MCP server",
    )
    parser.add_argument(
        "--fetch-cmd",
        default=os.getenv("FETCH_MCP_SERVER_CMD", "fetch-mcp").strip(),
        help="Command to start fetch MCP server",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    source_urls = _read_urls_from_markdown(Path(args.source_urls_file))
    chain = [
        ("tavily-mcp", args.tavily_cmd),
        ("brave-search-mcp", args.brave_cmd),
        ("fetch-mcp", args.fetch_cmd),
    ]

    attempts: list[dict[str, Any]] = []
    selected_engine = "none"
    selected_rows: list[dict[str, Any]] = []

    for server_name, server_cmd in chain:
        if not server_cmd:
            attempts.append(
                {"server": server_name, "status": "skipped", "reason": "missing command"}
            )
            continue
        try:
            rows, soft_error = _run_with_server(
                server_name=server_name,
                server_cmd=server_cmd,
                query=args.query,
                max_results=max(1, args.max_results),
                source_urls=source_urls,
            )
            if rows:
                selected_engine = server_name
                selected_rows = rows
                attempts.append(
                    {
                        "server": server_name,
                        "status": "ok",
                        "result_count": len(rows),
                        "warning": soft_error or "",
                    }
                )
                break
            attempts.append(
                {
                    "server": server_name,
                    "status": "empty",
                    "reason": soft_error or "no rows returned",
                }
            )
        except Exception as exc:
            attempts.append({"server": server_name, "status": "error", "reason": str(exc)})

    response: dict[str, Any] = {
        "query": args.query,
        "engine": selected_engine,
        "results": selected_rows[: args.max_results],
        "attempts": attempts,
    }

    if selected_engine == "none":
        response["fallback_urls"] = source_urls
        response[
            "message"
        ] = "Source collection unavailable. Please verify directly at fallback URLs."

    json.dump(response, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
