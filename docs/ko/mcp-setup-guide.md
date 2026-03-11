**Language:** [**한국어**](mcp-setup-guide.md) | [English](../en/mcp-setup-guide.md)

# MCP Setup Guide (Windows, Beginner)

> **[README](README.md)** | **[How to Use](how-to-use.md)** | **[Disclaimer](disclaimer.md)**

이 가이드는 이 프로젝트에서 사용하는 두 가지 MCP 경로를 설명합니다.

1. `legal-skills` (AgentSkills/Case.dev): 법률 스킬 탐색용
2. 웹 리서치 MCP 체인 (`tavily -> brave -> fetch`): `search-executor.py`에서 사용

## A. Legal Skills MCP (Recommended First)

### 1) Get API key

1. `https://console.case.dev` 열기
2. 계정 생성 또는 로그인
3. API 키 생성
4. 키 복사

### 2) Set environment variable (Windows PowerShell)

```powershell
setx CASE_API_KEY "YOUR_REAL_KEY"
$env:CASE_API_KEY = "YOUR_REAL_KEY"
```

참고:

- `setx`는 이후 열리는 모든 터미널에 영구적으로 적용됩니다.
- `$env:...`는 현재 터미널 세션에만 즉시 적용됩니다.

### 3) Register MCP server in Codex

```powershell
codex mcp add legal-skills --url https://skills.case.dev/api/mcp --bearer-token-env-var CASE_API_KEY
```

이미 추가했다면 아래 명령으로 확인할 수 있습니다.

```powershell
codex mcp list
codex mcp get legal-skills
```

### 4) Restart Codex

MCP 연결을 올바르게 불러오려면 현재 Codex 세션을 종료한 뒤 새로 시작해야 합니다.

## B. Web Research MCP Chain (for this repository scripts)

현재 스크립트:

- `.claude/skills/web-researcher/scripts/search-executor.py`
- 폴백 순서: `tavily-mcp -> brave-search-mcp -> fetch-mcp`

### 1) Install Node.js LTS

1. `https://nodejs.org/`에서 Node.js LTS 다운로드 및 설치
2. 새 PowerShell을 열고 확인

```powershell
node -v
npm -v
npx -v
```

### 2) Set MCP launch commands

`search-executor.py`가 사용할 실행 명령을 설정합니다.

```powershell
setx TAVILY_MCP_SERVER_CMD "tavily-mcp"
setx BRAVE_MCP_SERVER_CMD "brave-search-mcp"
setx FETCH_MCP_SERVER_CMD "fetch-mcp"

$env:TAVILY_MCP_SERVER_CMD = "tavily-mcp"
$env:BRAVE_MCP_SERVER_CMD = "brave-search-mcp"
$env:FETCH_MCP_SERVER_CMD = "fetch-mcp"
```

실제 설치된 명령어 이름이 다를 경우, 해당 환경 변수 값을 맞게 수정하면 됩니다.

### 3) Set provider API keys if required by your MCP servers

예시:

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

예상 결과:

- 성공 시: `"engine": "tavily-mcp"` (또는 brave/fetch)와 `results` 배열이 채워진 JSON이 출력됩니다.
- 실패 시: `"engine": "none"`과 `fallback_urls`를 포함한 JSON이 출력됩니다.

## C. Troubleshooting

- `WinError 2`가 `search-executor` 실행 중 발생:
  - 명령을 찾을 수 없는 상태입니다. 해당 도구를 설치하거나 `*_MCP_SERVER_CMD` 값을 올바르게 수정하세요.
- `401/403`가 legal-skills MCP에서 발생:
  - `CASE_API_KEY`가 설정되지 않았거나 잘못된 값입니다.
- MCP를 추가했는데 목록에 보이지 않음:
  - 터미널을 새로 열고 `codex mcp list`를 다시 실행해 보세요.
- 네트워크/프록시 이슈:
  - `https://skills.case.dev/api/mcp` 및 각 provider endpoint에 접근할 수 있는지 확인하세요.
