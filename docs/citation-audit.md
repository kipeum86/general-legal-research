# Citation Audit Canonical Spec

**Status:** canonical project spec for citation audit behavior.
**Scope:** standalone `/audit`, workflow Step 9, DOCX handoff, sidecar artifacts, and Korean-law MCP degradation.

This document is the single source of truth for citation audit behavior. Runtime prompts and public docs should link here instead of restating the full procedure.

---

## 1. Invocation Contexts

| Context | Trigger | Output mode | Checkpoint behavior |
|---|---|---|---|
| Standalone `/audit <file.md>` | User explicitly runs `/audit` on an existing Markdown file | Inline badges plus per-claim audit report | Must not edit `output/checkpoint.json` |
| Workflow Step 9 | Automatic for Mode B/C/D or memo/opinion deliverables after Step 8 | Append mode: body preserved, failing claims tagged, appendix added | Must update `output/checkpoint.json` |

Step 9 is skipped for Mode A briefs unless the user requested a memo/opinion deliverable.

---

## 2. Workflow Step 9 Contract

Step 9 uses the vendored `citation-auditor` skill for claim extraction, verifier dispatch, aggregation, and Markdown rendering. Project-specific hardening lives in project-owned wrappers:

- `scripts/citation_audit_backend.py`
- `scripts/citation_audit_artifacts.py`
- `scripts/docx_citation_appendix.py`
- `scripts/render_professional_legal_opinion_docx.py`

Required Step 9 commands:

```bash
python3 -m citation_auditor aggregate <aggregate-input.json>
python3 scripts/citation_audit_backend.py enrich output/citation-audit-{session_id}.json \
  --registry-out output/claim-registry.json \
  --metadata-out output/citation-audit-{session_id}.metadata.json \
  --project-root . \
  --korean-law-mcp-available auto
```

If `enrich` rejects the aggregate shape, record Step 9 as `failed` or `partial`; do not mark the audit as complete.

---

## 3. Output Artifacts

| Artifact | Required when | Purpose |
|---|---|---|
| `output/citation-audit-{session_id}.json` | Every Step 9 run | Raw aggregated verdict JSON |
| `output/claim-registry.json` | Every Step 9 run after enrichment | Stable claim IDs, routing reasons, verdicts, normalized status |
| `output/citation-audit-{session_id}.metadata.json` | Every Step 9 run after enrichment | Metrics, MCP availability, source degradation |
| `output/citation-audit-{session_id}.md` | Unsupported final formats | Sidecar appendix |

Deprecated fallback:

- `output/citation-audit-latest.json` is only allowed when a renderer is explicitly invoked with `--use-latest-audit`.

---

## 4. Format Support Matrix

| Final format | Integration level | Required behavior |
|---|---|---|
| `.md` | Full append-mode integration | Render with `python3 -m citation_auditor render <draft.md> <aggregated.json> --mode=append` and replace the draft |
| `.docx` | Full appendix integration through adapter | Pass `--audit-json` or `--session-id` to `scripts/render_professional_legal_opinion_docx.py` |
| `.pdf` | Sidecar only | Write aggregate JSON and sidecar appendix Markdown; notify user |
| `.pptx` | Sidecar only | Write aggregate JSON and sidecar appendix Markdown; notify user |
| `.html` | Sidecar only | Write aggregate JSON and sidecar appendix Markdown; notify user |
| `.txt` | Sidecar only | Write aggregate JSON and sidecar appendix Markdown; notify user |

DOCX renderers must use `scripts/docx_citation_appendix.py` rather than hand-rolling an audit table.

---

## 5. Detailed Status Model

The project-owned backend normalizes vendored verdict output into these statuses:

| Status | Meaning |
|---|---|
| `verified` | Source evidence supports the claim |
| `contradicted` | Source evidence conflicts with the claim |
| `unsupported` | Verifier ran but no supporting evidence was found |
| `source_unavailable` | A needed source could not be retrieved |
| `verifier_unavailable` | No verifier result was produced |
| `not_a_legal_claim` | Claim should not be audited as a legal/factual claim |
| `unknown` | Residual unresolved state |

Checkpoint summaries should use the full metadata `metrics` object, not only `{verified, contradicted, unknown}`.

The metadata metrics object includes:

- `total_claims`
- `audited_claims`
- `verified`
- `contradicted`
- `unsupported`
- `source_unavailable`
- `verifier_unavailable`
- `unknown`
- `tool_failures`
- `coverage_ratio`

---

## 6. Korean-Law MCP Degradation

`korean-law-mcp` is strongly recommended for Korean-law citation auditing.

When a Korean-law claim is routed but MCP availability is missing, false, or only placeholder-configured, metadata must include:

```json
{
  "scope": "korean-law",
  "reason": "korean-law MCP unavailable or not declared available; primary-law verification may degrade to unknown.",
  "affected_claim_ids": ["..."]
}
```

Final DOCX appendices should show this degradation in the audit status block.

---

## 7. 한국어 요약

이 문서는 citation audit의 공식 규약입니다.

- `/audit <file.md>`는 수동 실행이며 checkpoint를 수정하지 않습니다.
- Workflow Step 9는 Mode B/C/D 또는 memo/opinion 산출물에 자동 실행되며 checkpoint를 갱신합니다.
- Step 9는 항상 raw aggregate JSON, claim registry, metadata sidecar를 남겨야 합니다.
- `.md`와 `.docx`는 최종 산출물에 audit appendix를 직접 포함합니다.
- `.pdf`, `.pptx`, `.html`, `.txt`는 현재 sidecar appendix로 제공합니다.
- 한국법 인용 감사에는 `korean-law-mcp` 사용을 강력 권장하며, 미사용 또는 placeholder 설정이면 metadata와 appendix에 degradation을 표시합니다.
