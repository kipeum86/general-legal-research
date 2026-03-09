---
name: quality-checker
description: Run the 7-item legal research quality gate and decide pass/fail with remediation steps.
---

# Quality Checker

Use this skill at Step 7 before delivery.

## 7-Item Checklist

1. Every key conclusion has primary-source support.
2. Legal hierarchy is not conflated.
3. Amendment/effective dates and currency are checked.
4. Jurisdiction level is accurate.
5. Uncertain claims are clearly marked.
6. Pinpoints and verification guide are present.
7. No D-grade source is sole basis of any conclusion.

## Output Format

```json
{
  "quality_gate": "pass|fail",
  "failed_items": [1, 4],
  "remediation_plan": [
    "Re-enter Step 3 for issue X",
    "Patch section Y with new source Z"
  ]
}
```

## Remediation Policy

- Round 1: collect additional sources for failing items.
- Round 2: patch only failing sections.
- If still failing: deliver with `[Unverified]` tags.
