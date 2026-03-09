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
- `grade_rationale` (one line)
- optional tags (`[Industry Self-Regulatory Body]`, `[Unverified]`, `[Unresolved Conflict]`)

Read `references/scoring-rubric.md`.

## Rules

1. Grade every source without exception.
2. No conclusion may rely solely on D-grade material.
3. Mark bias-prone practitioner sources with explicit caveat.
4. If grading is inconsistent, retry once and normalize.
