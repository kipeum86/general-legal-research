**Language:** [English](../../README.md) | [**한국어**](README.md)

# General Legal Research Agent

Claude Code 기반의 증거 중심 국제 법률 리서치 워크플로입니다.

> **[How to Use](how-to-use.md)** | **[Disclaimer](disclaimer.md)** | **[MCP Setup Guide](mcp-setup-guide.md)**

## Overview

`General Legal Research Agent`는 실무 분야와 관할을 가리지 않고 구조화된, 출처 기반의 법률 조사를 수행하도록 설계된 Claude Code 에이전트 스캐폴드입니다. 외부 백엔드 없이 로컬 Claude Code 세션 안에서 작동합니다.

이 에이전트는 사용자별로 설정 가능합니다. 첫 실행 시 간단한 설정 마법사를 통해 이름, 소속, 주요 업무 분야, 선호 관할을 수집하고 이를 `user-config.json`에 저장합니다. 이후 세션에서는 이 설정을 자동으로 불러와 에이전트의 페르소나, 기본 관할, 출력 언어를 별도 입력 없이 개인화합니다.

이 프로젝트는 **법률 자문을 제공하기 위한 도구가 아닙니다**.

## Example Outputs

| 예시 | 설명 |
|------|------|
| [한국어 결과물](https://docs.google.com/document/d/1KBaSeJXEXWDNKoxS2yt0kE6XXjuw5JWw/edit?usp=sharing&ouid=105178834220477378953&rtpof=true&sd=true) | 딥페이크 규제 5개국 비교 분석 (KR, EU, US, JP, UK) |
| [English output](https://docs.google.com/document/d/1HTXCMYERDhHlm40_zSqMrIWATJPTBPOW/edit?usp=sharing&ouid=105178834220477378953&rtpof=true&sd=true) | Deepfake regulation across five jurisdictions (KR, EU, US, JP, UK) |

## Core Design Principles

- **No hallucination**: 검증 가능한 pinpoint citation 없이 법률 주장을 하지 않음
- **Source hierarchy**: 1차 자료(법령, 판례, 행정문서)를 2차 자료보다 우선하며, 신뢰도가 낮은 블로그/위키는 단독 근거로 사용하지 않음
- **Citation integrity**: 모든 핵심 결론은 직접 수집한 1차 소스까지 추적 가능해야 하며, 2차 소스를 1차 소스인 것처럼 인용하는 것을 차단 (소스 세탁 방지)
- **Uncertainty transparency**: 미해결 쟁점은 모두 `[Unverified]` 또는 `[Unresolved Conflict]`로 표시
- **Jurisdiction-first**: `law.go.kr`, `eur-lex.europa.eu`, `congress.gov` 같은 공식 포털을 우선 직접 조회

## Workflow

### Standard: 9 Steps (Step 0 + Steps 1-7)

| Step | Name | Output |
|------|------|--------|
| 0 | User Config Loading | `user-config.json` 로드, 없으면 `/onboard` 자동 실행 |
| 1 | Query Interpretation & Parameter Resolution | 구조화된 파라미터와 가정 |
| 2 | Jurisdiction Mapping & Research Plan | 관할 프로필, 쟁점 체크리스트, 검색 계획 |
| 3 | Source Collection | 메타데이터가 포함된 원문 소스 수집 |
| 3.5 | Factual Claim Spot-Check & Source Laundering Detection | `output/claim-registry.json`에 anchor별 Verified / Unverified / Contradicted 기록 + 소스 세탁 플래그 |
| 4 | Source Reliability Scoring (A-D) | 근거가 포함된 신뢰도 등급표 |
| 5 | Analysis & Issue Structuring | 쟁점 트리, 충돌 리포트, 용어집 업데이트 |
| 6 | Output Generation (Mode A/B/C/D) | 인라인 미리보기 후 확인 시 파일 생성 |
| 7 | Quality-Gate Self-Verification | 통과/실패 및 개선 지시 |

### Quick Mode: 4 Steps (Steps 1 -> 3 -> 6 -> 7)

단일 관할의 간단한 법령 조회처럼 추가 단계들이 실질적인 의미를 갖지 않는 경우, Quick Mode가 자동으로 적용됩니다.

세션 상태는 각 단계 종료 시 `output/checkpoint.json`에 체크포인트됩니다. 중단된 세션은 이어서 재개할 수 있습니다.

## Personal Configuration

이 에이전트는 1인 사용자가 로컬에 설치해 사용하는 방식을 전제로 설계되었습니다. 맞춤 GPT나 Claude Project를 설정하듯, 자신의 실무에 맞게 한 번만 설정해 두면 됩니다.

### How it works

**첫 세션(자동 실행):** `user-config.json`이 없으면 Step 0에서 리서치를 시작하기 전에 설정 마법사를 자동으로 실행합니다. `/onboard`를 수동으로 실행할 필요는 없습니다.

**설정 방식:**

- **[1] Starter template**: 6개 프리셋 중 하나를 바로 선택
- **[2] Custom interview**: 7개 질문에 답하면서 모든 필드를 직접 설정

**Starter templates:**

| # | Template | Primary Jurisdiction | Output Language |
|---|----------|---------------------|-----------------|
| 1 | Korean General Statute | KR | Korean |
| 2 | Korean Startup / VC / Tech | KR (+ US, SG) | Korean |
| 3 | Korean IP Litigation | KR (+ US, EU, JP) | Korean |
| 4 | Korean Employment & Labor | KR | Korean |
| 5 | US Corporate & M&A | US | English |
| 6 | EU Privacy & GDPR | EU (+ UK, US, KR) | English |

**재설정:** 언제든 `/onboard`를 실행해 설정을 바꿀 수 있습니다. 기존 설정을 보여주고 덮어쓰기 전 확인을 받습니다.

### Local-only files (gitignored)

사용자별 데이터는 모두 로컬에만 저장되며 git에는 커밋되지 않습니다.

| Path | Who manages it | Purpose |
|------|----------------|---------|
| `user-config.json` | `/onboard`가 자동 생성 | 페르소나, 기본 관할, 출력 선호 |
| `knowledge/` | 에이전트가 조사 후 자동 생성 | 캐시된 조사 결과, 법령 다이제스트, 검증된 소스 스냅샷 |
| `library/` | 변호사가 수동 업로드 | 자체 법률의견, 판례, 논문, 규정 자료. Step 3에서 Grade A 소스로 취급 |

### `user-config.json` schema

```json
{
  "version": "1.0",
  "persona": {
    "name": "Jane Smith",
    "title": "Associate",
    "firm": "Smith & Partners LLP",
    "bar_admissions": ["US-NY"],
    "specialization": "US Corporate & M&A"
  },
  "practice": {
    "primary_area": "corporate",
    "sub_areas": ["MA_transactions", "PE_VC"],
    "industry_sectors": ["technology", "healthcare"],
    "typical_matters": ["merger_agreement_review", "due_diligence"]
  },
  "jurisdictions": {
    "primary": ["US"],
    "secondary": ["EU", "KR"]
  },
  "research_defaults": {
    "mode": "D",
    "output_format": "docx",
    "output_language": "en"
  },
  "kb": { "index_path": "knowledge/_index.md" },
  "library": { "index_path": "library/_index.md" }
}
```

### `library/` directory

참고자료를 이 디렉터리에 넣어 두면 됩니다. 에이전트는 Step 0에서 `library/_index.md`를 읽고, 인덱싱된 파일을 Step 3 소스 수집 시 Grade A 자료로 취급합니다.

```text
library/
|-- _index.md          # 이 인덱스는 수동 관리
|-- opinions/          # 법률의견서 (내부/외부)
|-- cases/             # 판례 PDF
|-- papers/            # 논문, law review 자료
|-- regulations/       # 규제 가이드라인, 행정 매뉴얼
`-- misc/
```

### `knowledge/` directory

에이전트가 자동 생성하는 디렉터리입니다. 각 리서치 세션 후 검증된 사실, 법령 발췌, 소스 메타데이터를 저장해 이후 세션에서 재사용합니다.

```text
knowledge/
|-- _index.md          # 에이전트가 관리
|-- statutes/
|-- cases/
|-- templates/
`-- precedents/
```

## Output Modes

| Mode | Type | Default format |
|------|------|----------------|
| A | Executive Brief | `.md` |
| B | Comparative Matrix | `.md` |
| C | Enforcement & Case Law | `.md` |
| D | Black-letter & Commentary (long-form) | `.docx` (default) |

지원 포맷: `.md`, `.docx`, `.pdf`, `.pptx`, `.html`, `.txt`

`legal opinion`, `opinion letter`, `formal opinion memo` 형태의 결과물이 필요하면 `legal-opinion-formatter` 스킬이 로펌 스타일의 A4 `python-docx` 문서를 생성합니다.

## Architecture

```text
Main agent (CLAUDE.md orchestrator)
  |-- Skills: 8 core + 15 specialist (read inline per step)
  `-- Sub-agent: deep-researcher
      (activated when >=3 jurisdictions, >8 sources, or >~20,000 words)
```

### Core Skills (Steps 0-7)

| Skill | Step |
|-------|------|
| `onboard` | 0 |
| `query-interpreter` | 1 |
| `jurisdiction-mapper` | 2 |
| `web-researcher` | 3 |
| `fact-checker` | 3.5 |
| `source-scorer` | 4 |
| `conflict-detector` + `glossary-manager` | 5 |
| `output-generator` | 6 |
| `quality-checker` | 7 |

### Specialist Skills (routed by topic)

| Skill | Trigger topic |
|-------|---------------|
| `legal-opinion-formatter` | legal opinion, opinion letter, formal opinion |
| `legal-research` | 리서치 방법론, authority validation |
| `legal-research-summary` + `client-memo` | 조사 요약, 메모 출력 |
| `regulatory-summary` + `compliance-summaries` | 시장 진입, 규제기관 의무 |
| `gambling-law-summary` | 도박, loot box, 게임 라이선스 |
| `privacy-law-updates` + `cyber-law-compliance-summary` | 데이터 / 프라이버시 |
| `antitrust-investigation-summary` | 독점규제 / 경쟁법 |
| `ip-infringement-analysis` | IP 집행, 분쟁 리스크 |
| `terms-of-service` + `api-acceptable-use-policy` | 플랫폼 / 사용자 정책 |
| `judgment-summary` + `case-briefs` | 판례 요약 |

## Source Reliability & Citation Model

**Reliability grades:**

| Grade | Description |
|-------|-------------|
| A | 공식 1차 자료(법령, 판례, 행정문서, 규제기관 문서), 또는 변호사가 업로드한 `library/` 자료 |
| B | 신뢰도 높은 2차 자료(동료심사 논문, 주요 실무가 출판물. 비공식 번역본은 최대 B) |
| C | 중간 신뢰도. 편향 메모 필요 |
| D | 낮은 신뢰도. 어떤 결론의 단독 근거로도 사용 불가 |

**Source authority 분류:** 모든 소스는 등급(A~D)과 별도로 `primary`(공식 원문), `secondary`(해석/해설), `mixed`(혼합)로 분류됩니다. 핵심 결론에는 반드시 직접 수집한 Grade A/B `primary` 소스가 필요합니다. `laundering_risk` 플래그가 붙은 2차 소스는 1차 소스로 인용할 수 없습니다.

**Citation codes:** `[P#]` 법률/규정 | `[T#]` 조약 | `[C#]` 판례 | `[A#]` 행정자료 | `[S#]` 2차 자료

**Special tags:** `[Industry Self-Regulatory Body]` | `[Unverified]` | `[Unresolved Conflict]`

## Jurisdiction Coverage

직접 fetch가 허용된 공식 법률 포털(17개 이상):

| Region | Portal |
|--------|--------|
| Korea | law.go.kr, supremecourt.go.kr |
| EU | eur-lex.europa.eu |
| US | congress.gov, ecfr.gov, federalregister.gov |
| UK | legislation.gov.uk |
| Germany | gesetze-im-internet.de |
| Japan | laws.e-gov.go.jp, moj.go.jp |
| France | legifrance.gouv.fr |
| Spain | boe.es |
| Italy | gazzettaufficiale.it |
| China | flk.npc.gov.cn |
| Singapore | sso.agc.gov.sg |
| Australia | legislation.gov.au |
| Canada | laws-lois.justice.gc.ca |
| Brazil | planalto.gov.br |

추가적인 실무가/해설 출처는 `.claude/skills/web-researcher/references/legal-source-urls.md`에 정리되어 있습니다.

## Repository Structure

```text
/project-root
|-- CLAUDE.md                          # main orchestrator (start here)
|-- user-config.json                   # gitignored; auto-generated by /onboard
|-- .gitignore
|-- .env.example                       # MCP API key template
|-- .claude/
|   |-- settings.local.json            # WebFetch domain allowlist
|   |-- agents/
|   |   `-- deep-researcher/AGENT.md
|   `-- skills/
|       |-- onboard/                   # /onboard skill + 6 starter templates
|       |-- query-interpreter/
|       |-- jurisdiction-mapper/
|       |-- web-researcher/
|       |-- source-scorer/
|       |-- conflict-detector/
|       |-- glossary-manager/
|       |-- output-generator/
|       |-- quality-checker/
|       |-- legal-opinion-formatter/   # includes python-docx generator
|       `-- [15 specialist skills]/
|-- knowledge/                         # gitignored; agent-generated KB
|   |-- _index.md
|   |-- statutes/
|   |-- cases/
|   |-- templates/
|   `-- precedents/
|-- library/                           # gitignored; attorney-curated materials (Grade A)
|   |-- _index.md
|   |-- opinions/
|   |-- cases/
|   |-- papers/
|   |-- regulations/
|   `-- misc/
|-- scripts/
|   |-- install-agentskills-set.ps1
|   |-- render_professional_legal_opinion_docx.py
|   `-- render_acp_comparison_docx.py
|-- references/
|   `-- korean-law-reference.md        # Korean law research guide
|-- output/
|   |-- glossary/glossary-global.json
|   `-- reports/                       # generated output files (gitignored)
`-- docs/
    |-- en/
    |   |-- README.md                  # compatibility bridge to root README
    |   |-- how-to-use.md
    |   |-- disclaimer.md
    |   `-- mcp-setup-guide.md
    |-- ko/
    |   |-- README.md
    |   |-- how-to-use.md
    |   |-- disclaimer.md
    |   `-- mcp-setup-guide.md
    |-- how-to-use.md                  # compatibility bridge
    |-- disclaimer.md                  # compatibility bridge
    `-- mcp-setup-guide.md             # compatibility bridge
```

## How to Use

### Requirements

- [Claude Code](https://claude.ai/code) CLI 설치 및 로그인
- Python 3 + `python-docx` (DOCX 출력용): `pip install python-docx`
- 선택 사항: MCP 검색 제공자 API 키 (`.env.example`, `mcp-setup-guide.md` 참고)

### Running a research task

1. 이 저장소를 클론한 뒤 Claude Code로 열어 둡니다.
2. **첫 세션만:** 에이전트가 자동으로 onboard 설정 마법사를 실행합니다. 스타터 템플릿을 고르거나 7개의 짧은 질문에 답하면 됩니다. 보통 2분 정도 걸리며 로컬에 `user-config.json`이 생성됩니다.
3. 한국어 또는 영어 자연어로 조사 질문을 입력합니다.
4. 에이전트가 전체 9단계 워크플로 또는 간단한 조회라면 Quick Mode를 실행한 뒤 결과물을 생성합니다.
5. 세션이 끊기면 다음 시작 시 `output/checkpoint.json` 기준으로 이어서 진행할 수 있습니다.

설정을 다시 바꾸고 싶다면 언제든 `/onboard`를 실행하면 됩니다.

**예시 질문:**

```text
한국 개인정보보호법상 가명처리 요건과 GDPR 제4조 제5호를 비교하고,
KR-EU 공동 컨트롤러에 적용되는 컴플라이언스 갭을 분석해 주세요.
```

```text
현재 시행 중이거나 규칙 제정이 진행 중인 미국 연방 AI 책임 규율 체계를 요약해 주세요.
```

```text
델라웨어 법인이 한국 자회사를 주식매수 방식으로 인수할 때 필요한
이사회 승인 요건을 분석하고, CFIUS 또는 공정거래위원회 신고 기준 해당 여부를 검토해 주세요.
```

```text
당사 SaaS 플랫폼의 데이터 현지화 아키텍처가 브라질 LGPD 제33조
국외 이전 요건을 충족하는지에 대한 법률의견서를 작성해 주세요.
```

### Local-Only vs MCP-Connected

| Mode | What works | What doesn't |
|------|------------|--------------|
| Local-only | 허용된 법률 포털 직접 URL fetch, skill dispatch, 결과물 생성 | 키워드 검색 (`tavily` / `brave`) |
| MCP-connected | 키워드 검색까지 포함한 전체 워크플로 | `.env` API 키 필요 |

## Development Roadmap

1. 9단계 워크플로에 대한 반복 가능한 통합 테스트 추가
2. 더 많은 관할 조합에 대한 conflict-resolution heuristic 확장
3. 실제 production MCP connector 추가 (현재 script stub 대체)
4. checkpoint / glossary JSON 산출물에 대한 CI schema validation 추가
5. `legal-source-urls.md`의 관할 범위 확대 (India, Netherlands, Mexico 등)
6. `knowledge/` 관리를 위한 `/kb add`, `/kb search`, `/kb status` 명령 구현
7. Step 7 완료 후 `knowledge/_index.md` 자동 업데이트

## Disclaimer

이 프로젝트는 법률 리서치 워크플로를 지원하기 위한 도구입니다. 법률 자문을 제공하지 않습니다.
실제 법적 판단은 해당 관할의 자격 있는 전문가와 상의해야 합니다.

## License

MIT. 자세한 내용은 `LICENSE`를 참고하세요.
