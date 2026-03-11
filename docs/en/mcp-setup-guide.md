**Language:** [한국어](../ko/mcp-setup-guide.md) | [**English**](mcp-setup-guide.md)

# MCP Setup Guide (Windows, Beginner)

> **[README](../../README.md)** | **[How to Use](how-to-use.md)** | **[Disclaimer](disclaimer.md)**

This guide covers the two MCP paths used in this project:

1. `legal-skills` (AgentSkills/Case.dev) for legal skill discovery
2. The web-research MCP chain (`tavily -> brave -> fetch`) used by `search-executor.py`

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

## C. Troubleshooting

- `WinError 2` when running `search-executor`:
  - The command was not found. Install the tool or fix `*_MCP_SERVER_CMD`.
- `401/403` from the legal-skills MCP:
  - `CASE_API_KEY` is missing or invalid.
- Added MCP but not visible:
  - Restart the terminal and run `codex mcp list` again.
- Network or proxy issues:
  - Test access to `https://skills.case.dev/api/mcp` and the provider endpoints.
