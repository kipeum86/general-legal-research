# General Legal Research Agent

Evidence-based international legal research workflow, powered by Claude Code.

> **[How to Use](docs/how-to-use.md)** · **[Disclaimer](docs/disclaimer.md)** · **[MCP Setup Guide](docs/mcp-setup-guide.md)**

## Overview

`General Legal Research Agent` is a Claude Code agent scaffold that performs structured, source-grounded legal research across any practice area and jurisdiction. It runs entirely within your local Claude Code session — no external backend required.

The agent persona is **Kim Jaesik (김재식)**, a 5th-year Associate at **Law Firm Pearl (법무법인 진주)**, specializing in domestic and international statute/regulation research (국내외 법률/법령 조사).

This project is **not** designed to provide legal advice.

## Core Design Principles

- **No hallucination**: no legal claim without a verifiable, pinpoint-cited source
- **Source hierarchy**: primary sources (statutes, cases, agency documents) over secondary; low-trust blogs/wikis excluded as sole basis
- **Uncertainty transparency**: all unresolved findings tagged `[Unverified]` or `[Unresolved Conflict]`
- **Jurisdiction-first**: official legal portals fetched directly (law.go.kr, eur-lex.europa.eu, congress.gov, etc.)

## Workflow

### Standard: 8 Steps

| Step | Name | Output |
|------|------|--------|
| 1 | Query Interpretation & Parameter Resolution | Structured parameters + assumptions |
| 2 | Jurisdiction Mapping & Research Plan | Jurisdiction profile, domain checklist, search plan |
| 3 | Source Collection | Raw sources with metadata |
| 3.5 | Factual Claim Spot-Check | `output/claim-registry.json` — Verified / Unverified / Contradicted per anchor |
| 4 | Source Reliability Scoring (A–D) | Graded source list with rationale |
| 5 | Analysis & Issue Structuring | Issue tree, conflict report, glossary updates |
| 6 | Output Generation (Mode A/B/C/D) | Inline preview → file on confirmation |
| 7 | Quality-Gate Self-Verification | Pass/fail with remediation |

### Quick Mode: 4 Steps (Steps 1 → 3 → 6 → 7)

For simple, single-jurisdiction statute lookups where Steps 2, 3.5, 4, and 5 would add overhead without meaningful benefit.

Session state is checkpointed at the end of every step (`output/checkpoint.json`). Interrupted sessions can be resumed.

## Output Modes

| Mode | Type | Default format |
|------|------|----------------|
| A | Executive Brief | `.md` |
| B | Comparative Matrix | `.md` |
| C | Enforcement & Case Law | `.md` |
| D | Black-letter & Commentary (long-form) | `.docx` ← default |

Supported file formats: `.md`, `.docx`, `.pdf`, `.pptx`, `.html`, `.txt`

For legal opinion deliverables (`법률 의견서`, `legal opinion`, `opinion letter`), the `legal-opinion-formatter` skill generates a python-docx A4 document in law-firm style.

## Architecture

```
Main agent (CLAUDE.md orchestrator)
  └── Skills: 8 core + 15 specialist (read inline per step)
  └── Sub-agent: deep-researcher (activated when ≥3 jurisdictions, >8 sources, or >~20,000 words)
```

### Core Skills (`steps 1–7`)

| Skill | Step |
|-------|------|
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
| `legal-opinion-formatter` | 법률 의견서, opinion letter, formal opinion |
| `legal-research` | Research methodology, authority validation |
| `legal-research-summary` + `client-memo` | Research digest, memo output |
| `regulatory-summary` + `compliance-summaries` | Market entry, regulator obligations |
| `gambling-law-summary` | Gambling, loot boxes, gaming licensing |
| `privacy-law-updates` + `cyber-law-compliance-summary` | Data / privacy |
| `antitrust-investigation-summary` | Antitrust / competition |
| `ip-infringement-analysis` | IP enforcement, dispute risk |
| `terms-of-service` + `api-acceptable-use-policy` | Platform/user policy terms |
| `judgment-summary` + `case-briefs` | Case-law synthesis |

## Source Reliability & Citation Model

**Reliability grades:**

| Grade | Description |
|-------|-------------|
| A | Official primary source (statute, case, agency document, regulatory body) |
| B | High-quality secondary (peer-reviewed, major practitioner publication; unofficial translations max B) |
| C | Medium reliability — bias note required |
| D | Low reliability — not allowed as sole basis for any conclusion |

**Citation codes:** `[P#]` legislation/regulation · `[T#]` treaty · `[C#]` case law · `[A#]` administrative · `[S#]` secondary

**Special tags:** `[Industry Self-Regulatory Body]` · `[Unverified]` · `[Unresolved Conflict]`

## Jurisdiction Coverage

Official legal portals pre-approved for direct fetch (17+ jurisdictions):

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

Additional practitioner/commentary sources are listed in `.claude/skills/web-researcher/references/legal-source-urls.md`.

## Repository Structure

```
/project-root
├── CLAUDE.md                          ← main orchestrator (start here)
├── .gitignore
├── .env.example                       ← MCP API key template
├── .claude/
│   ├── settings.local.json            ← WebFetch domain allowlist
│   ├── agents/
│   │   └── deep-researcher/AGENT.md
│   └── skills/
│       ├── query-interpreter/
│       ├── jurisdiction-mapper/
│       ├── web-researcher/
│       ├── source-scorer/
│       ├── conflict-detector/
│       ├── glossary-manager/
│       ├── output-generator/
│       ├── quality-checker/
│       ├── legal-opinion-formatter/   ← includes python-docx generator
│       └── [15 specialist skills]/
├── scripts/
│   ├── install-agentskills-set.ps1
│   ├── render_professional_legal_opinion_docx.py
│   └── render_acp_comparison_docx.py
├── references/
│   └── korean-law-reference.md        ← Korean law research guide (법원체계, 판례, 규제기관, 용어)
├── output/
│   ├── glossary/glossary-global.json
│   └── reports/                       ← generated output files (gitignored)
└── docs/
    ├── how-to-use.md
    ├── disclaimer.md
    ├── mcp-setup-guide.md
    └── agentskills-installed.md
```

## How to Use

### Requirements

- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- Python 3 + `python-docx` (for DOCX output): `pip install python-docx`
- Optional: MCP search provider API keys (see `.env.example` and `docs/mcp-setup-guide.md`)

### Running a research task

1. Open this directory in Claude Code.
2. Issue your research question in natural language — Korean or English.
3. The agent runs the full 8-step workflow (or Quick Mode for simple lookups) and produces the deliverable.
4. For interrupted sessions, resume from `output/checkpoint.json` at session start.

**Example prompts:**

```
개인정보보호법 제28조의2에 따른 가명정보 처리 요건을 EU GDPR 가명처리 규정과 비교 분석해줘.
```

```
Summarize US federal AI liability frameworks currently in effect or under active rulemaking.
```

```
브라질 LGPD 적용 범위와 위반 시 과징금 체계를 법률 의견서 형식으로 작성해줘.
```

### Local-Only vs MCP-Connected

| Mode | What works | What doesn't |
|------|-----------|--------------|
| Local-only | Direct URL fetch from whitelisted legal portals, skill dispatch, output generation | Keyword search (tavily/brave) |
| MCP-connected | Full workflow including search | Requires API keys in `.env` |

## Development Roadmap

1. Add repeatable integration tests for the 8-step workflow
2. Expand conflict-resolution heuristics for more jurisdiction pairs
3. Add production MCP connectors (replace script stubs)
4. Add CI schema validation for checkpoint and glossary JSON artifacts
5. Expand `legal-source-urls.md` for additional jurisdictions (India, Netherlands, Mexico, etc.)

## Disclaimer

This project supports legal research workflows. It does not provide legal advice.
For legal decisions, consult qualified counsel in the relevant jurisdiction.

## License

MIT. See `LICENSE`.
