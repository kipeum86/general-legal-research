---
name: quality-checker
description: Run the 12-item legal research quality gate and decide pass/fail with remediation steps.
---

# Quality Checker

Use this skill at Step 7 before delivery.

## 12-Item Checklist

1. Every key conclusion has primary-source support.
2. Legal hierarchy is not conflated.
3. Amendment/effective dates and currency are checked; temporal tags applied where relevant (`[Recently Amended]`, `[Pending Amendment]`, `[Not Yet In Force]`, `[Repealed]`).
4. Jurisdiction level is accurate.
5. Uncertain claims are clearly marked.
6. Pinpoints and verification guide are present.
7. No D-grade source is sole basis of any conclusion.
8. Every key conclusion has at least one counter-argument or risk scenario (per `references/counter-analysis-checklist.md`).
9. Practical Implications section is present and addresses client-actionable takeaways.
10. Executive summary / conclusion summary is consistent with the detailed analysis — no conclusion in the summary that is unsupported or contradicted in the body.
11. Every key conclusion is supported by at least one Grade A or Grade B source (not only C/D).
12. No `[Material Risk]` finding is omitted from the executive summary / conclusion summary.

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
