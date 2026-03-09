# How to Use — General Legal Research Agent

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- Python 3 + `python-docx` (for DOCX output): `pip install python-docx`
- (Optional) MCP server API keys for enhanced web research — see [MCP Setup Guide](mcp-setup-guide.md)

## Quick Start

1. Open a terminal in the project root directory.
2. Launch Claude Code:
   ```bash
   claude
   ```
3. Ask your research question in natural language (Korean or English). Examples:
   - "개인정보보호법 제28조의2에 따른 가명정보 처리 요건을 EU GDPR 가명처리 규정과 비교 분석해줘."
   - "Summarize US federal AI liability frameworks currently in effect or under active rulemaking."
   - "브라질 LGPD 적용 범위와 위반 시 과징금 체계를 법률 의견서 형식으로 작성해줘."

4. The agent will execute an 8-step workflow automatically:

   | Step | What happens |
   |------|-------------|
   | 1 | Parses your query into structured parameters |
   | 2 | Maps relevant jurisdictions and builds a research plan |
   | 3 | Collects sources via web research (MCP or direct portal fetch) |
   | 3.5 | Spot-checks factual claims to intercept hallucinations |
   | 4 | Grades each source for reliability (A–D) |
   | 5 | Analyzes issues, detects conflicts, updates glossary |
   | 6 | Generates your deliverable (with inline preview) |
   | 7 | Final quality gate — up to two remediation rounds |

5. Choose your preferred output format when prompted (`.md`, `.pdf`, `.docx`, `.pptx`, `.html`, `.txt`).

## Output Modes

| Mode | Best for |
|------|----------|
| A — Executive Brief | Quick overview for decision-makers |
| B — Comparative Matrix | Side-by-side jurisdiction comparison |
| C — Enforcement & Case Law | Litigation-focused case summaries |
| D — Black-letter & Commentary | Deep-dive with full statutory text and analysis (default) |

Mode D is the default, reflecting the agent's specialization in statute/regulation research. You can request a different mode at any time.

## Quick Mode

For simple, single-jurisdiction factual lookups, the agent automatically applies Quick Mode:
- Runs Steps 1 → 3 → 6 → 7 only (skips Steps 2, 3.5, 4, 5).
- Stated at the start of the response as `[Quick Mode: single-issue lookup]`.
- Falls back to the full 8-step workflow if the answer cannot be confirmed from 1–2 sources.

## Resuming Interrupted Sessions

If a session is interrupted, the agent saves progress to `output/checkpoint.json`. On the next launch, it will offer to resume from where it left off.

## Local-Only vs MCP-Connected Mode

| Mode | What works | What doesn't |
|------|-----------|--------------|
| Local-only | Direct URL fetch from whitelisted legal portals, skill dispatch, output generation | Keyword search (tavily/brave) |
| MCP-connected | Full workflow including keyword search | Requires API keys — see [MCP Setup Guide](mcp-setup-guide.md) |

## Tips

- **Be specific about jurisdictions** — the agent performs best when you name the countries or regions you care about.
- **Ask for a specific output mode** if you have a preference (e.g., "give me a comparative matrix" or "Mode B로 해줘").
- **Request a legal opinion format** by saying "법률 의견서" or "legal opinion" — the agent will use the formal opinion formatter with A4 layout.
- **Check the glossary** — jurisdiction-specific legal term translations are saved in `output/glossary/` and reused across sessions.
- **Korean law queries** are routed to 국가법령정보센터 (law.go.kr) first; **EU law** to EUR-Lex first.
- **Review all outputs** — this is a research tool, not a substitute for legal judgment. See the [Disclaimer](disclaimer.md).
