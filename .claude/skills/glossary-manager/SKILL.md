---
name: glossary-manager
description: Maintain jurisdiction-aware legal glossary entries with translation-memory consistency and source-backed definitions.
---

# Glossary Manager

Use this skill in Step 6 and Step 7 when terminology appears.

## Input

- Terms extracted during analysis
- Jurisdiction and governance level
- Supporting citation pinpoints

## Output

Update glossary JSON files under:
- `output/glossary/glossary-{jurisdiction-code}.json`

Read schema from `references/glossary-schema.md`.

## Pre-Seeded Glossaries

- `output/glossary/glossary-kr.json` — 15 core Korean legal terms with mistranslation risks (법률, 시행령, 시행규칙, 고시, 판결, 의뢰인, 당사자, 과태료, 벌금, 과징금, 가명정보, 개인정보처리자, 정보주체, 법인, 법률자문).

When Korean law is involved, always load `glossary-kr.json` first. Use existing entries as-is unless the research context requires a different translation — in that case, add a context rule rather than overwriting the standard translation.

## Rules

1. Same term in same jurisdiction uses same default translation.
2. If context needs a different translation, record context rule.
3. Mark uncertain terms as `provisional`.
4. Every definition must include a source and pinpoint.
5. Check pre-seeded glossary before creating a new entry for the same term.
