# Game Legal Research Agent

Evidence-based international legal research workflow for the game industry.

## Overview

`Game Legal Research Agent` is an implementation scaffold for a legal research assistant specialized in game-related regulation across jurisdictions.

This project is designed for:

- In-house legal counsel and business/legal operations in game companies
- Cross-jurisdiction legal/regulatory comparison
- Source-grounded internal decision support

This project is **not** designed to provide legal advice.

## Current Repository Status

This repository now includes an **operational local MVP scaffold** based on the design spec.

Included now:

- `game-legal-research-agent-design.md`: integrated design document
- `CLAUDE.md`: main orchestrator instructions
- `.claude/skills/*`: modular skill set (Step 1-7)
- `.claude/skills/*` (external): selected AgentSkills legal modules for specialist tasks
- `.claude/agents/deep-researcher/AGENT.md`: optional sub-agent definition
- `output/*`: checkpoint and intermediate artifact templates
- `scripts/install-agentskills-set.ps1`: helper script to install selected external legal skills
- `.env.example`: environment variable template for optional MCP integrations
- `docs/mcp-setup-guide.md`: beginner setup guide for MCP integration
- `docs/agentskills-installed.md`: installed AgentSkills set + install command
- `LICENSE`: MIT license

## Core Design Principles

- No legal advice: research and analysis support only
- Anti-hallucination: no legal claim without verifiable source
- Source hierarchy enforced:
  - Primary: statute/regulation/case law/agency original documents
  - Secondary: academic or practitioner materials
  - Excluded as basis: low-trust summaries/blog/wiki-style sources
- Pinpoint citations required: article/section/page/paragraph
- Uncertainty transparency: unresolved findings must be tagged and explained

## End-to-End Workflow (7 Steps)

1. Query Interpretation & Parameter Resolution
2. Jurisdiction Mapping & Research Plan
3. Source Collection (web research)
4. Source Reliability Scoring (A-D)
5. Analysis & Issue Structuring
6. Output Generation (Mode A/B/C/D + file format)
7. Quality-Gate Self-Verification

Checkpointing is part of the design (`output/checkpoint.json`) to support resume after interruptions.

## Output Modes

- Mode A: Executive Brief
- Mode B: Comparative Matrix
- Mode C: Enforcement & Case Law
- Mode D: Black-letter & Commentary (long-form, file output default)

Supported output formats (design target):

- `.md`, `.pdf`, `.docx`, `.pptx`, `.html`, `.txt`

## Source Reliability & Citation Model

Reliability grade:

- A: official primary source
- B: high-quality secondary source
- C: medium reliability (bias note required)
- D: low reliability (not allowed as sole basis)

Citation codes:

- `[P#]`: legislation/regulation
- `[T#]`: treaty/convention
- `[C#]`: case law/decision
- `[A#]`: administrative document
- `[S#]`: academic/practitioner source

Special tags:

- `[Industry Self-Regulatory Body]`
- `[Unverified]`
- `[Unresolved Conflict]`

## Architecture

Single main agent + one optional sub-agent:

- Main agent: orchestrates the full workflow
- Sub-agent (`deep-researcher`): activated for multi-jurisdiction/high-volume source analysis

Core skill modules:

- `query-interpreter`
- `jurisdiction-mapper`
- `web-researcher`
- `source-scorer`
- `conflict-detector`
- `glossary-manager`
- `output-generator`
- `quality-checker`

Specialist external legal skills are also installed under `.claude/skills/` (e.g., legal research, regulatory/compliance, privacy, antitrust, IP, memo/case summary templates).

## Repository Structure

```text
/project-root
├── .env.example
├── CLAUDE.md
├── .claude/
│   ├── skills/
│   └── agents/
├── scripts/
├── output/
│   ├── reports/
│   └── glossary/
└── docs/
```

## Scope (Regulatory Domains)

1. Gambling & chance mechanics (loot box/gacha)
2. Consumer protection & advertising
3. Minors & online safety
4. Privacy & data
5. Platform/app store policies
6. IP & UGC
7. Esports & tournaments
8. Virtual assets & digital items
9. Competition/antitrust
10. Labor/freelancer (game-industry-specific context only)

## How to Use This Repository

1. Read `CLAUDE.md` (runtime orchestration rules).
2. Start Codex in this directory and issue your research task in natural language.
3. The agent executes the 7-step workflow and uses `.claude/skills/*` as dispatch targets.
4. Use `output/checkpoint.json` to resume interrupted sessions.
5. Keep `game-legal-research-agent-design.md` as the authoritative design reference.

### Local-Only vs MCP-Connected

- Local-only mode works without external API keys by using the installed local skills.
- MCP-connected mode is optional and documented in `docs/mcp-setup-guide.md`.

## Development Roadmap (Next)

1. Replace MCP script stubs with production connectors per provider environment.
2. Add repeatable integration tests for the 7-step workflow.
3. Add robust format export backends for PDF/DOCX/PPTX.
4. Add CI checks for linting, schema validation, and artifact consistency.
5. Expand jurisdiction-specific legal source references and conflict-resolution heuristics.

## Disclaimer

This project supports legal research workflows. It does not provide legal advice.
For legal decisions, consult qualified counsel in the relevant jurisdiction.

## License

MIT. See `LICENSE`.

