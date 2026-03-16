---
name: source-scorer
description: Assign reliability grades A-D to collected legal sources and enforce no D-grade-only conclusions.
---

# Source Scorer

Use this skill at Step 5.

## Input

- Collected source list from Step 3 (with Step 4 claim registry)

## Output

For each source:
- `reliability_grade` (`A|B|C|D`)
- `source_authority` (`primary|secondary|mixed`) — independent of grade; classifies the source's inherent nature
- `grade_rationale` (one line)
- `laundering_risk` (`true|false`) — flag if secondary source paraphrases primary without pinpoint citation
- optional tags (`[Industry Self-Regulatory Body]`, `[Unverified]`, `[Unresolved Conflict]`)

Read `references/scoring-rubric.md`.

## Source Authority Classification

`source_authority` is **independent** of `reliability_grade`. A Grade B source can be `primary` (e.g., regulator guidance) and a Grade A source can be `mixed` (e.g., annotated official code). The two fields together determine how a source may be used in conclusions:

| `source_authority` | Description | Example |
|---|---|---|
| `primary` | Official original text — statute, regulation, court decision, treaty, agency order | law.go.kr statute text, EUR-Lex regulation, CURIA judgment |
| `secondary` | Interpretation, commentary, or analysis of primary sources | law-firm newsletter, academic article, practitioner guide |
| `mixed` | Contains both original text excerpts and editorial analysis | annotated codes, case-law databases with editorial headnotes |

## Rules

1. Grade every source without exception.
2. **Every key conclusion must be supported by at least one Grade A or B `primary`-authority source.** A conclusion supported only by `secondary` or `mixed` sources — regardless of grade — is incomplete and must be flagged for remediation.
3. Mark bias-prone practitioner sources with explicit caveat.
4. If grading is inconsistent, retry once and normalize.
5. No conclusion may rely solely on D-grade material.
6. For `mixed` sources, clearly distinguish which parts are primary text and which are editorial. Only the primary text portion may support conclusions as primary authority.
7. **Source laundering detection:** If a `secondary` source paraphrases or summarizes a primary source without providing a pinpoint citation (specific article, section, or paragraph reference) to the original, set `laundering_risk: true`. Such sources may NOT be cited as if they were primary authority. When `laundering_risk: true`, the researcher must either (a) locate and directly fetch the underlying primary source, or (b) cite the secondary source transparently as secondary (e.g., "According to [Firm]'s analysis of [Statute]...").
