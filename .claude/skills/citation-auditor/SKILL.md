---
name: citation-auditor
description: Audit a markdown file by chunking it, extracting claims with structured output, routing each claim to verifier skills, aggregating verdicts, and rendering annotated markdown.
argument-hint: "<file.md>"
disable-model-invocation: true
---

Audit the markdown file at `$0`.

## Invocation Contexts

This skill is invoked in two distinct contexts:

- **Standalone `/audit` (default)**: user-triggered via the `/audit <file.md>` slash command on any existing markdown file. Uses **inline mode** — per-claim badges injected into the body plus a per-claim audit report at the end. Does not alter `output/checkpoint.json`.
- **Workflow Step 9 (automatic)**: invoked by the main orchestrator after Step 8 for Mode B/C/D or memo/opinion deliverables (see `CLAUDE.md` §5 Step 9). Uses **append mode** — body preserved with only `[Unverified]` / `[Partially Unverified]` tags on failing claims, plus a `## 부록: 검증 로그 (Citation Audit Log)` appendix table at the end. The rendered output replaces the Step 7 draft as the final saved artifact.

The only procedural difference between the two contexts is the `--mode` flag passed to `render` in step 13 below. Steps 1–12 are identical.

## Procedure

1. Confirm `$0` exists and is a markdown file. If it does not, stop and ask for a valid path.
2. Run:
   `python3 -m citation_auditor chunk "$0" --max-tokens 3000`
3. Parse stdout as JSON with the schema `{ "chunks": [...] }`.
4. For each chunk, extract only factual, citation-bearing claims using structured output with this schema:
   - `text: string`
   - `sentence_span: { start: integer, end: integer }`
   - `claim_type: factual | citation | quantitative | temporal | other`
   - `suggested_verifier: string | null`
5. Do not extract speculation, forecasts, rumors, advocacy, or soft prediction language such as:
   - `전망이다`
   - `예상된다`
   - `업계 관계자에 따르면`
   - `가능성이 있다`
   Unless the sentence also contains a concrete verifiable factual assertion that stands on its own.
6. Keep claim offsets chunk-relative. Do not convert them to document offsets yourself.
7. Route each claim to verifier skills:
   - If `suggested_verifier` is set and exactly matches a loaded verifier skill name, use it.
   - Otherwise test the claim text against each verifier skill frontmatter `patterns` using case-insensitive regex matching and use every match.
   - If nothing matches, fall back to `general-web`.
8. For each `(claim, verifier)` pair, use the Task tool to dispatch a subagent that loads that verifier skill and receives the claim JSON.
9. Require each verifier subagent to return only this JSON:
   `{ "label": "...", "rationale": "...", "supporting_urls": ["..."], "authority": 0.0 }`
10. `supporting_urls` may contain either clickable source URLs or plain-language source references when no stable URL exists. Preserve them verbatim and do not invent clickable URLs for non-linkable sources such as precedent search-result IDs.
11. Build aggregate input JSON locally. The exact top-level shape is `{ "verdicts": [ <bundle>, ... ] }` where each `<bundle>` covers one `(chunk, claim)` pair and holds all verifier candidates for that claim. Do not invent other top-level keys.

    **Exact schema (copy this structure):**
    ```json
    {
      "verdicts": [
        {
          "chunk": { "index": 0, "text": "<full chunk text>", "segments": [ { "chunk_start": 0, "chunk_end": 44, "document_start": 0, "document_end": 44 } ] },
          "claim": { "text": "<claim sentence>", "sentence_span": { "start": 64, "end": 268 }, "claim_type": "citation", "suggested_verifier": "us-law" },
          "candidates": [
            {
              "claim": { "text": "<same claim as above>", "sentence_span": { "start": 64, "end": 268 }, "claim_type": "citation", "suggested_verifier": "us-law" },
              "verifier_name": "us-law",
              "authority": 0.9,
              "label": "contradicted",
              "rationale": "<Korean rationale from verifier>",
              "evidence": [ { "url": "https://..." } ]
            }
          ]
        }
      ]
    }
    ```

    Rules:
    - One bundle per `(chunk, claim)` pair. If the same claim has two verifiers, put both candidates inside the same bundle's `candidates` array — do NOT create a second bundle for the same claim.
    - The top-level `claim` inside each bundle is the canonical claim; each candidate's `claim` must match it verbatim.
    - `evidence` items require a non-empty `url` string. If the verifier returned `supporting_urls: []`, emit `"evidence": []` — do not emit `[{"url": ""}]`.
    - `label` must be one of `verified` / `contradicted` / `unknown`.
    - `authority` must match the verifier skill's declared authority value.

12. Write that JSON to a temp file and run:
    `python3 -m citation_auditor aggregate <tmpfile>`
13. Write the aggregate output to a temp file and run:
    - Standalone `/audit`: `python3 -m citation_auditor render "$0" <aggfile>` (inline mode is default).
    - Workflow Step 9: `python3 -m citation_auditor render "$0" <aggfile> --mode=append`.
14. Return only the final annotated markdown unless the user explicitly asked for intermediate JSON. In the Step 9 context, the orchestrator replaces the Step 7 draft with this output and saves as the final artifact.
15. If claim extraction validation fails, retry once with a repair prompt. If it still fails, skip that chunk and note it briefly.
16. If a verifier subagent returns invalid JSON, drop that candidate instead of inventing a verdict.
17. If a line was skipped because it is a forecast, opinion, rumor, or unattributed speculation, treat that as expected behavior rather than an extraction failure.
18. If the user asks why a forecast or opinion line was not audited, explain that this plugin audits verifiable factual claims and citations, not predictions or commentary.
