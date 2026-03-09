---
name: output-generator
description: Generate mode-specific legal research deliverables, enforce citation style, and handle file format confirmation and save flow.
---

# Output Generator

Use this skill at Step 7.

## Inputs

- Analysis result (Step 6)
- Selected **mode** (A/B/C/D or auto) — controls structure and depth
- Selected **format** (`.md`/`.docx`/`.pdf`/`.html` etc.) — controls file type
- Output language

**Mode and format are independent.** Confirm each separately. Mode D + `.docx` is the default for Kim Jaesik's statute-research work.

## Tone & Audience

Every output is a **client-facing memorandum or opinion letter**:

- **Korean**: formal polite register throughout — `~합니다`, `~습니다`, `~드립니다`, `~입니다`. Body text must not use informal or plain-speech endings.
- **English**: formal memo/opinion register. No casual phrasing or draft-note style.
- Address the reader as a client. Frame findings as professional analysis, not researcher notes.

## Mandatory Sections

Every output must include:
1. Scope & as-of date
2. Conclusion summary
3. Issue tree
4. Detailed analysis
5. Counter-analysis (per conclusion, per `references/counter-analysis-checklist.md`)
6. Practical implications (client-actionable takeaways)
7. Annotated bibliography
8. Verification guide

## Mode-Specific References

- **Mode B (Comparative Matrix):** Also read `references/comparative-framework.md` for standardized comparison axes and divergence commentary rules.

## Templates

- `references/mode-a-template.md`
- `references/mode-b-template.md`
- `references/mode-c-template.md`
- `references/mode-d-template.md`
- `references/citation-format-guide.md`

If output intent matches legal opinion deliverables (`법률 의견서`, `opinion letter`, `legal opinion`, `formal opinion`, `opinion memo`), ALWAYS read BOTH:
- `.claude/skills/legal-opinion-formatter/SKILL.md` (routing overview and style rules)
- `.claude/skills/legal-opinion-formatter/legal-opinion-formatter-SKILL.md` (full python-docx implementation)

This is a mandatory routing rule for opinion-letter style outputs.

## Format & Save Rules

1. First query in session: ask preferred file format.
2. Later queries: confirm previous format.
3. Show inline preview first.
4. Save only after explicit confirmation.
5. If file name collides, append `_v2`, `_v3`, etc.

## Scripts

- Unix-like: `scripts/file-converter.sh`
- Windows PowerShell: `scripts/file-converter.ps1`

Use the converter wrapper when deterministic file conversion dispatch is needed.
