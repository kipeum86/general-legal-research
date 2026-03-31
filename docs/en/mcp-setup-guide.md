**Language:** [한국어](../ko/mcp-setup-guide.md) | [**English**](mcp-setup-guide.md)

# MCP Setup Guide (Windows, Beginner)

> **[README](../../README.md)** | **[How to Use](how-to-use.md)** | **[Disclaimer](disclaimer.md)**

This guide covers the MCP/parser integrations most commonly used in this project:

1. `legal-skills` (AgentSkills/Case.dev) for legal skill discovery
2. The web-research MCP chain (`tavily -> brave -> fetch`) used by `search-executor.py`
3. Korean law retrieval and document parsing via `korean-law-mcp` and `kordoc`

## A. Legal Skills MCP (Recommended First)

### 1) Get API key

1. Open `https://console.case.dev`
2. Create an account or sign in
3. Create an API key
4. Copy the key

### 2) Set environment variable (Windows PowerShell)

```powershell
setx CASE_API_KEY "YOUR_REAL_KEY"
$env:CASE_API_KEY = "YOUR_REAL_KEY"
```

Notes:

- `setx` makes the value persistent for new terminals
- `$env:...` applies it to the current terminal immediately

### 3) Register MCP server in Codex

```powershell
codex mcp add legal-skills --url https://skills.case.dev/api/mcp --bearer-token-env-var CASE_API_KEY
```

If it is already added, verify it with:

```powershell
codex mcp list
codex mcp get legal-skills
```

### 4) Restart Codex

Close the current Codex session and start a new one so the MCP connection is picked up cleanly.

## B. Web Research MCP Chain (for this repository scripts)

Current script:

- `.claude/skills/web-researcher/scripts/search-executor.py`
- Fallback order: `tavily-mcp -> brave-search-mcp -> fetch-mcp`

### 1) Install Node.js LTS

1. Download and install Node.js LTS from `https://nodejs.org/`
2. Open a new PowerShell and verify:

```powershell
node -v
npm -v
npx -v
```

### 2) Set MCP launch commands

Set the commands used by `search-executor.py`:

```powershell
setx TAVILY_MCP_SERVER_CMD "tavily-mcp"
setx BRAVE_MCP_SERVER_CMD "brave-search-mcp"
setx FETCH_MCP_SERVER_CMD "fetch-mcp"

$env:TAVILY_MCP_SERVER_CMD = "tavily-mcp"
$env:BRAVE_MCP_SERVER_CMD = "brave-search-mcp"
$env:FETCH_MCP_SERVER_CMD = "fetch-mcp"
```

If your installed command names differ, set these variables to the exact launch command.

### 3) Set provider API keys if required by your MCP servers

Example:

```powershell
setx TAVILY_API_KEY "YOUR_TAVILY_KEY"
setx BRAVE_API_KEY "YOUR_BRAVE_KEY"
$env:TAVILY_API_KEY = "YOUR_TAVILY_KEY"
$env:BRAVE_API_KEY = "YOUR_BRAVE_KEY"
```

### 4) Test the script

```powershell
cd "C:\path\to\general-legal-research"
.\.claude\skills\web-researcher\scripts\search-executor.ps1 -Query "GDPR data processing requirements official text"
```

Expected output:

- Success: JSON with `"engine": "tavily-mcp"` (or brave/fetch) and non-empty `results`
- Failure: JSON with `"engine": "none"` plus `fallback_urls`

## C. Korean Law MCP Server (law.go.kr — 64 tools)

The `korean-law-mcp` server provides 64 native tools for Korean law research (statutes, cases, interpretations, tribunal decisions, chain workflows, annexes, and more). It connects to the same law.go.kr Open API used by `open_law_api.py`, but runs as an MCP server so Claude Code can invoke tools directly.

- GitHub: `https://github.com/chrisryugj/korean-law-mcp`
- In this repository, it is wired through `.mcp.json`.

### 1) Prerequisites

- Node.js >= 20 (`node -v` to check)

### 2) Get API key (same as Open Law API)

1. Register at `https://open.law.go.kr` (free)
2. Your OC key is the local-part of the email ID registered with the service.
3. In docs, examples, and commits, use a placeholder such as `your_openlaw_oc` instead of a real identifier.

### 3) Configure `.mcp.json` (already done if you cloned the repo)

The project root contains `.mcp.json` with the korean-law MCP server pre-configured:

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "npx",
      "args": ["-y", "korean-law-mcp@latest"],
      "env": {
        "LAW_OC": "your_openlaw_oc"
      }
    }
  }
}
```

Replace `your_openlaw_oc` locally with your own OC key. Avoid committing personal identifiers into the repository.

### 4) Verify

Restart Claude Code. The 64 tools (e.g., `search_law`, `get_law_text`, `chain_full_research`) should appear as available MCP tools.

### 5) Key tools

| Tool | Purpose |
|:-----|:--------|
| `search_law` | Search statutes by keyword (auto-resolves abbreviations) |
| `get_law_text` | Retrieve full statute text by MST/lawId |
| `get_three_tier` | Trace 3-tier delegation: Act → Decree → Rules |
| `chain_full_research` | One-call parallel search across statutes, cases, and interpretations |
| `search_constitutional_decisions` | Constitutional Court decisions |
| `search_ftc_decisions` | Fair Trade Commission decisions |
| `search_tax_tribunal_decisions` | Tax Tribunal decisions |
| `get_annexes` | Extract annexes (별표/서식) from HWPX/HWP files |
| `compare_old_new` | Old vs new article comparison table |

> **Note:** The MCP server uses in-memory caching (resets on session end). For persistent file-based caching, use `python3 scripts/open_law_api.py --save`.

## D. Optional: `kordoc` Document Parser (HWP/HWPX)

`kordoc` is not a replacement for `korean-law-mcp`; it is a separate parser for Korean public-sector documents.

- GitHub: `https://github.com/chrisryugj/kordoc`
- Typical use: convert `.hwp`, `.hwpx`, and some Korean PDFs into Markdown/structured output
- How this repo uses it by default: via `library-ingest.py` as a CLI, rather than as an always-on MCP server
- Open Law API key not required: `kordoc` itself does not use the law.go.kr OC credential

Default launch example:

```bash
npx -y -p kordoc -p pdfjs-dist kordoc
```

If your MCP setup guide introduces Korean law tooling, it helps to mention `kordoc` alongside `korean-law-mcp` so users understand the split between official-law retrieval and document parsing.

## E. Troubleshooting

- `WinError 2` when running `search-executor`:
  - The command was not found. Install the tool or fix `*_MCP_SERVER_CMD`.
- `401/403` from the legal-skills MCP:
  - `CASE_API_KEY` is missing or invalid.
- Added MCP but not visible:
  - Restart the terminal and run `codex mcp list` again.
- Network or proxy issues:
  - Test access to `https://skills.case.dev/api/mcp` and the provider endpoints.
