---
name: web-researcher
description: Collect legal sources through MCP search and fetch, apply retry strategy, and produce metadata-complete source sets for legal analysis.
---

# Web Researcher

Use this skill at Step 3.

## Inputs

- Research plan from Step 2
- Domain checklist per jurisdiction

## Output

`sources[]` with:
- `title`
- `url`
- `issuer`
- `document_type`
- `jurisdiction`
- `publication_date` (if known)
- `effective_date` (if known)
- `accessed_date`
- `language`
- `snippet`
- `full_text` (if fetched)
- `collection_round`
- `source_authority` — classify at collection time:
  - `primary` — official statute text, court decision, regulator original publication, treaty text
  - `secondary` — law-firm memo, academic article, news report, commentary, practitioner guide
  - `mixed` — contains both original text excerpts and editorial analysis (e.g., annotated code)

## Collection Strategy

1. Query official databases first.
2. Collect at least one primary source per core issue.
3. Record complete metadata.
4. Retry up to 3 rounds with materially different keywords.

## Fallback Chain

1. `tavily-mcp`
2. `brave-search-mcp`
3. `fetch-mcp` using curated URLs in `references/legal-source-urls.md`

If all fail, return:
- clear failure note
- direct verification URL list
- unresolved issue list tagged `Unverified`

## Scripts

- Unix-like: `scripts/search-executor.sh`
- Windows PowerShell: `scripts/search-executor.ps1`

Use the script wrapper when deterministic shell execution is preferred.

`search-executor` internally runs `scripts/search-executor.py` and talks to MCP servers over stdio JSON-RPC.

Required server command env vars:
- `TAVILY_MCP_SERVER_CMD`
- `BRAVE_MCP_SERVER_CMD`
- `FETCH_MCP_SERVER_CMD`

Example:
- `TAVILY_MCP_SERVER_CMD="npx -y tavily-mcp"`
- `BRAVE_MCP_SERVER_CMD="npx -y @modelcontextprotocol/server-brave-search"`
- `FETCH_MCP_SERVER_CMD="npx -y @modelcontextprotocol/server-fetch"`

CLI usage:
- Unix: `./scripts/search-executor.sh "EU loot box regulation official text"`
- PowerShell: `.\scripts\search-executor.ps1 -Query "EU loot box regulation official text"`
