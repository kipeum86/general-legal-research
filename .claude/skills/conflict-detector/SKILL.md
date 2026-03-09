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

## Korean-Specific Conflict Rules

When Korean law is involved, apply these additional conflict patterns (see `references/korean-law-reference.md` § 7 for full details):

1. **법률 vs 시행령 (위임한계 초과)**: Check whether the decree exceeds the scope delegated by the parent statute. Tag: `[Unresolved Conflict — 위임한계 초과 의심]`.
2. **법률 vs 지방조례**: Ordinances must stay within the scope of the statute (지방자치법 제28조). Stricter ordinances require explicit statutory delegation.
3. **구법 vs 신법 (경과규정)**: Always check 부칙 transitional provisions — they may preserve old-law application for existing relationships. Tag: `[Unresolved Conflict — 구법/신법 경과규정 확인 필요]`.
4. **일반법 vs 특별법**: Lex specialis prevails (e.g., 신용정보법 over 개인정보 보호법 for financial data). Determine special-law scope first.
