---
name: glossary-manager
description: Maintain jurisdiction-aware legal glossary entries with translation-memory consistency and source-backed definitions.
---

# Glossary Manager

Use this skill in Step 5 and Step 6 when terminology appears.

## Input

- Terms extracted during analysis
- Jurisdiction and governance level
- Supporting citation pinpoints

## Output

Update glossary JSON files under:
- `output/glossary/glossary-{jurisdiction-code}.json`

Read schema from `references/glossary-schema.md`.

## Rules

1. Same term in same jurisdiction uses same default translation.
2. If context needs a different translation, record context rule.
3. Mark uncertain terms as `provisional`.
4. Every definition must include a source and pinpoint.
