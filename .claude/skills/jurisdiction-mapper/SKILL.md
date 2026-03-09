---
name: jurisdiction-mapper
description: Build jurisdiction profiles, map applicable regulatory domains, and produce a source-first research plan after query interpretation.
---

# Jurisdiction Mapper

Use this skill at Step 2 after Step 1 parameters are resolved.

## Inputs

- Step 1 structured parameters

## Outputs

1. Jurisdiction profile per target jurisdiction:
- governance layers (federal/state/supranational)
- relevant regulator types

2. Regulatory domain checklist:
- relevant domain IDs (from the ten-domain catalog)
- one-line rationale
- preferred primary source type

3. Research plan:
- search keyword sets
- source-priority order
- expected conflicts or uncertainty hotspots

Read `references/domain-checklist-template.md`.

## Rules

1. Identify at least one domain from the ten-domain set.
2. Separate governance levels for federal jurisdictions.
3. Prefer primary sources in plan (statute/regulation/case/agency).
4. Include an `uncertain_domains` list if relevance is unclear.
5. On failure, broaden scope once, then proceed with uncertainty tags.
