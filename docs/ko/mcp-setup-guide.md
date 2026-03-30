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

## C. Korean Law MCP Server (law.go.kr — 64개 도구)

`korean-law-mcp` 서버는 한국법 조사를 위한 64개 네이티브 도구를 제공합니다 (법령, 판례, 해석례, 전문기관 결정, chain 워크플로우, 별표/서식 등). `open_law_api.py`와 동일한 law.go.kr Open API를 사용하지만, MCP 서버로 실행되어 Claude Code에서 직접 도구 호출이 가능합니다.

### 1) 사전 요구사항

- Node.js >= 20 (`node -v`로 확인)

### 2) API 키 발급 (열린법령 API와 동일)

1. `https://open.law.go.kr`에서 회원가입 (무료)
2. OC 키 = 이메일 ID 앞부분 (예: `kipeum86@gmail.com` → `kipeum86`)

### 3) `.mcp.json` 설정 (레포를 클론했다면 이미 설정됨)

프로젝트 루트에 `.mcp.json`이 korean-law MCP 서버로 사전 설정되어 있습니다:

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "npx",
      "args": ["-y", "korean-law-mcp@latest"],
      "env": {
        "LAW_OC": "your_oc_key"
      }
    }
  }
}
```

`your_oc_key`를 실제 OC 키로 교체하세요.

### 4) 확인

Claude Code를 재시작합니다. 64개 도구 (예: `search_law`, `get_law_text`, `chain_full_research`)가 사용 가능한 MCP 도구로 표시됩니다.

### 5) 주요 도구

| 도구 | 용도 |
|:-----|:-----|
| `search_law` | 법령 키워드 검색 (약칭 자동 변환) |
| `get_law_text` | MST/lawId로 법령 전문 조회 |
| `get_three_tier` | 3단 위임 추적: 법률 → 시행령 → 시행규칙 |
| `chain_full_research` | 법령+판례+해석례 병렬 통합 검색 (1회 호출) |
| `search_constitutional_decisions` | 헌법재판소 결정 검색 |
| `search_ftc_decisions` | 공정거래위원회 의결 검색 |
| `search_tax_tribunal_decisions` | 조세심판원 결정 검색 |
| `get_annexes` | 별표/서식 추출 (HWPX/HWP 자동 파싱) |
| `compare_old_new` | 법령 신구대조표 |

> **참고:** MCP 서버는 인메모리 캐시를 사용합니다 (세션 종료 시 리셋). 영구 파일 캐싱은 `python3 scripts/open_law_api.py --save`를 사용하세요.

## D. Troubleshooting

- `WinError 2`가 `search-executor` 실행 중 발생:
  - 명령을 찾을 수 없는 상태입니다. 해당 도구를 설치하거나 `*_MCP_SERVER_CMD` 값을 올바르게 수정하세요.
- `401/403`가 legal-skills MCP에서 발생:
  - `CASE_API_KEY`가 설정되지 않았거나 잘못된 값입니다.
- MCP를 추가했는데 목록에 보이지 않음:
  - 터미널을 새로 열고 `codex mcp list`를 다시 실행해 보세요.
- 네트워크/프록시 이슈:
  - `https://skills.case.dev/api/mcp` 및 각 provider endpoint에 접근할 수 있는지 확인하세요.
