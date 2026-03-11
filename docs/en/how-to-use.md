**Language:** [한국어](../ko/how-to-use.md) | [**English**](how-to-use.md)

# How to Use | General Legal Research Agent

> **[README](../../README.md)** | **[Disclaimer](disclaimer.md)** | **[MCP Setup Guide](mcp-setup-guide.md)**

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- Python 3 + `python-docx` (for DOCX output): `pip install python-docx`
- Optional MCP server API keys for enhanced web research. See the [MCP Setup Guide](mcp-setup-guide.md)

## Quick Start

1. Open a terminal in the project root directory.
2. Launch Claude Code:

   ```bash
   claude
   ```

3. Ask your research question in natural language, in Korean or English. Examples:
   - "Compare pseudonymization requirements under Korea's Personal Information Protection Act and the GDPR."
   - "Summarize US federal AI liability frameworks currently in effect or under active rulemaking."
   - "Draft a formal opinion letter on the scope of Brazil LGPD and its cross-border transfer framework."

4. The agent automatically executes the following 8-step workflow:

   | Step | What happens |
   |------|--------------|
   | 1 | Parses your query into structured parameters |
   | 2 | Maps relevant jurisdictions and builds a research plan |
   | 3 | Collects sources via web research (MCP or direct portal fetch) |
   | 4 | Spot-checks factual claims to intercept hallucinations |
   | 5 | Grades each source for reliability (A-D) |
   | 6 | Analyzes issues, detects conflicts, and updates the glossary |
   | 7 | Generates your deliverable with an inline preview |
   | 8 | Runs a final quality gate with up to two remediation rounds |

5. Choose your preferred output format when prompted: `.md`, `.pdf`, `.docx`, `.pptx`, `.html`, `.txt`

## Output Modes

| Mode | Best for |
|------|----------|
| A - Executive Brief | Quick overview for decision-makers |
| B - Comparative Matrix | Side-by-side jurisdiction comparison |
| C - Enforcement & Case Law | Litigation-focused case summaries |
| D - Black-letter & Commentary | Deep dive with statutory text and analysis (default) |

Mode D is the default because the agent is optimized for statute and regulation research. You can request a different mode at any time.

## Quick Mode

For simple, single-jurisdiction factual lookups, the agent automatically applies Quick Mode:

- Runs Steps 1 -> 3 -> 7 -> 8 only, skipping Steps 2, 4, 5, and 6
- States `[Quick Mode: single-issue lookup]` at the start of the response
- Falls back to the full 8-step workflow if the answer cannot be confirmed from 1-2 sources

## Resuming Interrupted Sessions

If a session is interrupted, progress is saved to `output/checkpoint.json`. On the next launch, the agent offers to resume where it left off.

## Local-Only vs MCP-Connected Mode

| Mode | What works | What doesn't |
|------|------------|--------------|
| Local-only | Direct URL fetch from whitelisted legal portals, skill dispatch, output generation | Keyword search (`tavily` / `brave`) |
| MCP-connected | Full workflow including keyword search | Requires API keys. See the [MCP Setup Guide](mcp-setup-guide.md) |

## Tips

- **Be specific about jurisdictions**: the agent performs best when you name the countries or regions you care about.
- **Ask for a specific output mode** if you have a preference, such as "give me a comparative matrix" or "use Mode B".
- **Request a legal opinion format** by saying "legal opinion" or "formal opinion letter" so the formatter uses the A4 law-firm layout.
- **Check the glossary**: jurisdiction-specific legal term translations are stored in `output/glossary/` and reused across sessions.
- **Korean law queries** are routed to `law.go.kr` first, and **EU law queries** to EUR-Lex first.
- **Review every output**: this is a research tool, not a substitute for legal judgment. See the [Disclaimer](disclaimer.md)
