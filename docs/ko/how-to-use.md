**Language:** [**한국어**](how-to-use.md) | [English](../en/how-to-use.md)

# How to Use | General Legal Research Agent

> **[README](README.md)** | **[Disclaimer](disclaimer.md)** | **[MCP Setup Guide](mcp-setup-guide.md)**

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) 설치 및 로그인
- Python 3 의존성: `pip install -r requirements.txt`
- 선택 사항: 웹 리서치 강화를 위한 MCP 서버 API 키. 자세한 내용은 [MCP Setup Guide](mcp-setup-guide.md) 참고

## Quick Start

1. 프로젝트 루트 디렉터리에서 터미널을 엽니다.
2. Claude Code를 실행합니다.

   ```bash
   claude
   ```

3. 한국어 또는 영어 자연어로 리서치 질문을 입력합니다. 예시:
   - "개인정보보호법 제28조의2의 가명정보 처리 요건과 EU GDPR 가명처리 규정을 비교 분석해줘."
   - "Summarize US federal AI liability frameworks currently in effect or under active rulemaking."
   - "브라질 LGPD 적용 범위와 일반적 국외이전 체계를 법률 의견서 형식으로 작성해줘."

4. 에이전트는 다음의 8단계 워크플로를 자동으로 수행합니다 (memo/opinion 결과물의 경우 Step 9 자동 추가).

   | Step | What happens |
   |------|--------------|
   | 1 | 질문을 구조화된 파라미터로 해석 |
   | 2 | 관련 관할을 매핑하고 조사 계획 수립 |
   | 3 | 웹 리서치(MCP 또는 직접 포털 fetch)로 소스 수집 |
   | 4 | 사실 주장 spot-check로 hallucination 차단 |
   | 5 | 각 소스의 신뢰도를 A-D로 평가 |
   | 6 | 쟁점 분석, 충돌 탐지, 용어집 업데이트 |
   | 7 | 결과물 생성 (인라인 미리보기 포함) |
   | 8 | 최종 quality gate 수행, 최대 두 번까지 보정 |
   | 9 | *(조건부)* memo/opinion 결과물에 대한 citation audit — 최종 산출물에 **검증 로그 (Citation Audit Log)** appendix 자동 부록 |

5. 안내가 표시되면 원하는 출력 포맷을 선택합니다: `.md`, `.pdf`, `.docx`, `.pptx`, `.html`, `.txt`

## Output Modes

| Mode | Best for |
|------|----------|
| A - Executive Brief | 의사결정자용 빠른 개요 |
| B - Comparative Matrix | 관할별 나란히 비교 |
| C - Enforcement & Case Law | 소송/집행 중심 판례 요약 |
| D - Black-letter & Commentary | 조문과 해설을 포함한 심층 분석 (기본값) |

Mode D가 기본값입니다. 이 에이전트가 법령과 규정 조사에 특화되어 있기 때문입니다. 원하면 언제든 다른 모드를 지정할 수 있습니다.

## Quick Mode

단일 관할의 간단한 사실 조회에는 에이전트가 자동으로 Quick Mode를 적용합니다.

- Steps 1 -> 3 -> 7 -> 8만 실행합니다. Steps 2, 4, 5, 6은 생략합니다.
- 응답 시작 부분에 `[Quick Mode: single-issue lookup]`를 표시합니다.
- 1-2개 소스만으로 답을 확인할 수 없으면 표준 워크플로로 자동 전환됩니다.

## Citation Audit

Citation audit는 두 가지 방식으로 작동합니다.

- **자동 (Step 9)** — Mode B/C/D 또는 memo/opinion 결과물의 경우, Step 8 이후 citation audit이 자동 실행되어 최종 저장된 산출물에 **검증 로그 (Citation Audit Log)** appendix가 자동 포함됩니다. 별도 명령 불필요.
- **수동 (`/audit`)** — 외부에서 생성된 문서를 포함, 기존 markdown 파일에 대한 citation audit을 실행합니다.
  ```bash
  /audit path/to/deliverable.md
  ```
  클레임별 inline 판정이 주석으로 달린 annotated markdown을 반환합니다.

두 경로 모두 동일한 관할별 verifier(`korean-law`, `us-law`, `eu-law`, `uk-law`, `scholarly`, `wikipedia`, `general-web`)를 사용합니다. Step 9는 verifier routing, 상세 판정 상태, coverage metrics, source degradation note를 담은 `output/claim-registry.json`과 `output/citation-audit-{session_id}.metadata.json`도 함께 생성합니다. 예측·의견·루머는 의도적으로 제외되며, 검증 가능한 사실/인용 클레임만 대상으로 합니다.

한국법 인용 감사에는 `korean-law-mcp` 사용을 강력 권장합니다. 없으면 한국 법령·판례 verifier 결과가 audit metadata에서 degraded 상태(`source_unavailable` / `verifier_unavailable`)로 표시될 수 있습니다.

## Resuming Interrupted Sessions

세션이 중단되면 진행 상황이 `output/checkpoint.json`에 저장됩니다. 다음 실행 시 이어서 진행할지 여부를 확인합니다.

## Local-Only vs MCP-Connected Mode

| Mode | What works | What doesn't |
|------|------------|--------------|
| Local-only | 열린법령 API로 한국 법령·판례 조회, 허용된 법률 포털 직접 URL fetch, skill dispatch, 결과물 생성 | 키워드 검색 (`tavily` / `brave`), korean-law MCP 도구 |
| MCP-connected | korean-law MCP (한국법 64개 도구) + 키워드 검색 + PDF/DOCX 변환 포함 전체 워크플로 | API 키 + Node.js 필요. [MCP Setup Guide](mcp-setup-guide.md) 참고 |

## Tips

- **관할을 구체적으로 적기**: 국가나 지역을 명시할수록 성능이 좋아집니다.
- **출력 모드를 직접 요청하기**: 예를 들어 "comparative matrix로 작성" 또는 "Mode B로 해줘"처럼 지정할 수 있습니다.
- **법률의견서 형식 요청하기**: "법률 의견서" 또는 "legal opinion"이라고 쓰면 정식 opinion formatter를 사용합니다.
- **용어집 확인하기**: 관할별 법률 용어 번역은 `output/glossary/`에 저장되어 다음 세션에서 재사용됩니다.
- **한국 법률 질의는 `korean-law` MCP 서버를 우선 사용** (64개 도구 — 전문기관 결정, chain 리서치 포함)하고, 파일 캐싱은 `open_law_api.py`로 합니다. **EU 법률 질의는 EUR-Lex를 우선 조회**합니다.
- **모든 결과물은 최종 검토 필요**: 이 프로젝트는 리서치 도구이며 법률 판단의 대체재가 아닙니다. 자세한 내용은 [Disclaimer](disclaimer.md) 참고
