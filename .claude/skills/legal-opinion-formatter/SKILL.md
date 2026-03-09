---
name: legal-opinion-formatter
description: Format legal research output into a law-firm-grade formal opinion style, with clear issue framing, conclusions, risk grading, and citation-ready references.
---

# Legal Opinion Formatter

Use this skill during Step 6 (Output Generation) when the user asks for:
- "legal opinion"
- "formal opinion"
- "law-firm style"
- polished DOCX memo/opinion formatting

## Inputs

- Step 5 analysis result
- User language and output format
- Jurisdiction scope and as-of date

## Output Goal

Produce a clean legal-opinion document with:
1. Cover/meta block
2. Executive summary
3. Opinion question(s)
4. Jurisdiction-by-jurisdiction analysis
5. Risk matrix and practical recommendations
6. Source/citation section with verification pointers
7. Disclaimer and uncertainty notes

Read `references/format-checklist.md` before formatting.

For full python-docx implementation details, also read `legal-opinion-formatter-SKILL.md` in the same directory.

## Page Size

Default: **A4** (210mm × 297mm) — Korean law firm standard.
Use US Letter only when the user explicitly requests it or the matter is US-domestic.

## Style Rules

1. Keep tone formal and precise; avoid conversational wording.
2. Use concise issue statements and explicit conclusions.
3. Separate "fact", "rule", "analysis", and "recommendation".
4. Mark uncertainty explicitly (`[Unverified]`, `[Unresolved Conflict]` when needed).
5. Keep citation identifiers consistent with project codes (`[P#]`, `[C#]`, `[A#]`, `[S#]`, `[T#]`).
6. **Korean outputs**: formal polite register (`~합니다`, `~습니다`, `~드립니다`, `~입니다`) throughout all body text, headings, and recommendation items. Plain-speech endings are not permitted.
7. **English outputs**: formal opinion-letter register. Address the reader as a client throughout.

## Sample Assets

Use sample files as visual references only:
- Files are located at the skill root (same level as `references/`).
- `test_output_english.docx`
- `test_output_korean.docx`

Do not copy sample facts verbatim into new outputs.
