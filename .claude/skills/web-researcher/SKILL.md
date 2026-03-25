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

### Korean Law (KR jurisdiction) — API-first

For Korean statute, case law, and interpretation queries, **always use the Open Law API first**:

1. **`scripts/open_law_api.py`** — on-demand API calls to law.go.kr DRF
   - `search-law` → 법령 키워드 검색 (returns law ID, MST, enforcement date, ministry)
   - `get-law --id {ID}` → 법령 전문 조회 (structured: 조문, 항, 호, 목, 부칙)
   - `get-article --id {ID} --article {N}` → 특정 조문만 조회
   - `search-cases` → 판례 키워드 검색
   - `get-case --id {ID}` → 판례 전문 (판시사항, 판결요지, 참조조문)
   - `search-interpretations` → 법령해석례 검색

   **Usage:** `python3 scripts/open_law_api.py <command> [args]`

   **Workflow:**
   1. `search-law "법률명"` → get law ID from results
   2. `get-law --id {ID}` → full text with structured articles
   3. `get-article --id {ID} --article {N}` → specific article only (token-efficient)

2. If API returns empty/error → fall back to `tavily-mcp` / `brave-search-mcp`
3. Last resort: `fetch-mcp` using curated URLs in `references/legal-source-urls.md`

### All other jurisdictions

1. `tavily-mcp`
2. `brave-search-mcp`
3. `fetch-mcp` using curated URLs in `references/legal-source-urls.md`

If all fail, return:
- clear failure note
- direct verification URL list
- unresolved issue list tagged `Unverified`

## PDF/DOCX Source Handling

When a source URL points to a PDF or DOCX document, convert it to Markdown using the MarkItDown MCP tool before processing.

### Detection Triggers

- URL ends with `.pdf` or `.docx`
- law.go.kr download links (often serve PDF)
- EUR-Lex PDF versions (URLs containing `/TXT/PDF/`)
- Agency guidance documents (commonly distributed as PDF)

### Conversion Procedure

1. Call `mcp__markitdown__convert_to_markdown` with the source URI (supports `http://`, `https://`, `file://`)
2. Store the returned Markdown as `full_text` in the source record
3. Extract `snippet` from the first 1200 characters of meaningful content (skip headers/footers/boilerplate)
4. Set `document_type` to reflect original format (e.g., `statute_pdf`, `guidance_pdf`, `opinion_docx`)

### Metadata Enrichment

After conversion, scan the Markdown output for embedded metadata:
- Title (first `#` heading or document title)
- Publication/effective date
- Issuer (agency, court, or legislature name)

Populate `publication_date`, `effective_date`, and `issuer` from the extracted content. Set `accessed_date` to current date.

### Failure Handling

- If MarkItDown conversion fails → fall back to `fetch-mcp` for the HTML version of the same source
- If converted text is < 100 characters → treat as extraction failure (likely a scanned/image-only PDF)
- Mark failed sources as `[Unverified — PDF text extraction failed]` and preserve the direct URL for manual verification

### Token Budget Awareness

- For large PDFs (converted text > 10,000 words): store only the relevant sections (articles, clauses) in `full_text`
- Use heading structure from the Markdown output to identify and extract relevant portions
- Always record the source URL so the full document remains accessible for verification

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
