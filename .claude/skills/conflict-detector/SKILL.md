---
name: conflict-detector
description: Detect legal-source conflicts across definitions, scope, obligations, sanctions, and recency, then produce structured conflict reports.
---

# Conflict Detector

Use this skill during Step 5 when conflicts appear.

## Conflict Types

1. Definitional conflict
2. Scope conflict
3. Obligation conflict
4. Enforcement/sanction conflict
5. Recency conflict
6. Amendment/transitional provision conflict (e.g., old law still applies to existing contracts; new law applies from effective date)

## Output

Use `references/conflict-report-template.md`.

Resolution priority:
1. Legal hierarchy
2. Jurisdictional relevance
3. Recency
4. Original-text support

## Severity Handling

- High severity (obligation/sanction): re-enter Step 3 to collect additional primary sources before concluding.
- Medium severity (amendment/transitional): flag with `[Unresolved Conflict]` and state which period/subject the conflicting provision governs.
- Low severity (definition/recency): mark `[Unresolved Conflict]` when unresolved.

## Cross-Jurisdiction Conflicts

When a conflict exists between primary sources of different jurisdictions (e.g., EU Directive vs. member state implementation, or US federal law vs. state law):
- Document the governance hierarchy explicitly.
- Note whether the higher-level instrument sets a floor or a ceiling for member/state regulation.
- Apply the stricter standard if compliance-focused; apply the lex specialis principle if dispute-focused.
