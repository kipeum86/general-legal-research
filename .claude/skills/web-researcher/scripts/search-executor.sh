#!/usr/bin/env bash
set -euo pipefail

# MCP wrapper (tavily -> brave -> fetch).
# Configure commands via env vars:
# - TAVILY_MCP_SERVER_CMD
# - BRAVE_MCP_SERVER_CMD
# - FETCH_MCP_SERVER_CMD

QUERY="${1:-}"
if [[ -z "$QUERY" ]]; then
  echo "usage: search-executor.sh \"query text\"" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/search-executor.py" "$QUERY"
