---
name: fact-checker
description: >
  Extract verifiable factual anchors from Step 3 source collection output,
  spot-check them against primary sources within a token budget, and produce
  a structured Claim Registry (output/claim-registry.json) with
  Verified / Unverified / Contradicted status per anchor.
  Run as Step 4 — after source collection, before reliability scoring.
---

# Fact-Checker (Step 4)

## Purpose

Intercept hallucinations **before** they propagate into legal analysis.
Focus exclusively on **factual anchors** — discrete, falsifiable claims — not on legal reasoning or interpretation.

---

## Trigger Conditions

**Run** when any of the following is true:
- 2 or more jurisdictions
- Any jurisdiction outside KR (i.e., non-Korean law involved)
- Mode B or D (statute / black-letter research)
- Step 3 produced any source without a confirmed direct-fetch URL

**Skip (pass-through)** when:
- Quick Mode is active, OR
- Single jurisdiction KR-only, AND all sources in Step 3 were directly fetched from law.go.kr or confirmed primary portals

When skipping, write an empty registry and proceed:
```json
{ "skipped": true, "reason": "Quick Mode / KR single-jurisdiction confirmed" }
```

---

## Phase 1 — Anchor Extraction

Scan Step 3 output and extract all **Factual Anchors** into a structured list.

### What IS an anchor (extract these)

| Type | Examples | Priority |
|------|----------|----------|
| `statute_article` | "GDPR Art. 17", "상법 제342조" | HIGH |
| `case_citation` | "Case C-131/12", "대법원 2020다12345" | HIGH |
| `effective_date` | "in force 25 May 2018", "2023년 1월 개정" | HIGH |
| `numerical_threshold` | "72-hour notification", "14-day cooling-off" | HIGH |
| `official_doc_title` | "Regulation (EU) 2016/679", "개인정보 보호법" | MEDIUM |
| `regulatory_body_name` | "ICO", "EDPB", "금융위원회" | MEDIUM |
| `penalty_figure` | "up to €20 million or 4% global turnover" | HIGH |

### What is NOT an anchor (do not extract)

- Legal interpretations, conclusions, or paraphrased analysis
- Claims already directly quoted from a confirmed fetch (mark pre-Verified)
- Hedged statements (`"may apply"`, `"arguably"`, `"some scholars hold"`)

### Output format (internal working list)

```json
{
  "anchors": [
    {
      "id": "A001",
      "type": "statute_article",
      "claim": "GDPR Article 17 grants data subjects a right to erasure",
      "jurisdiction": "EU",
      "source_code": "[P1]",
      "source_url": "https://eur-lex.europa.eu/...",
      "pre_verified": false
    }
  ]
}
```

---

## Phase 2 — Prioritization

Sort anchors for verification in this order:

1. HIGH priority + no source URL → verify first (highest hallucination risk)
2. HIGH priority + source URL but no direct quote → verify next
3. MEDIUM priority + no source URL → verify if budget permits
4. Any anchor already directly quoted from a confirmed fetch → mark `Verified`, skip verification

---

## Phase 3 — Spot-Check (Budget-Constrained)

### Token budget

| Jurisdictions | Max fetches per jurisdiction | Rationale |
|---|---|---|
| 1 | 3 | Baseline |
| 2–3 | 3 per jurisdiction | Standard multi-jurisdiction |
| 4+ | 2 per jurisdiction | Deep-researcher mode; budget tighter |

### Verification procedure per anchor

1. **Source URL available**: fetch the specific article/section; confirm the claim against retrieved text
2. **No source URL**: use one search query to locate the primary source, then fetch; if not found in one attempt → mark `Unverified`
3. **Korean law**: fetch from law.go.kr first; confirm article number and text
4. **EU law**: fetch from eur-lex.europa.eu first
5. **Record result**: `Verified` / `Unverified` / `Contradicted`

### PDF/DOCX Source Verification

When a source URL or file path points to a PDF or DOCX document:

1. **Before verification**, convert the document to Markdown using `mcp__markitdown__convert_to_markdown` with the source URI
2. **Search the converted text** for the specific claim being verified:
   - For `statute_article` anchors: search for the article number (e.g., "제17조", "Article 17")
   - For `case_citation` anchors: search for the case number
   - For `numerical_threshold` anchors: search for the specific number
   - For `effective_date` anchors: search for date patterns
3. **Text matching rules:**
   - Exact article number match required for `statute_article` anchors
   - Date must match within the same document section for `effective_date` anchors
   - Numerical values must match exactly for `numerical_threshold` anchors
4. **If the PDF is from `library/`:**
   - Check `knowledge/library-converted/` for an existing Markdown version first
   - If available, use the pre-converted version (saves a conversion call)
   - If not available, convert inline using markitdown
5. **Failure handling:**
   - If markitdown fails to convert the PDF → mark the anchor as `Unverified — PDF text extraction failed`
   - Do not count a failed PDF conversion against the token budget

### Status definitions

| Status | Meaning |
|---|---|
| `Verified` | Source text confirms the claim within acceptable paraphrase |
| `Unverified` | Could not confirm within budget — not necessarily wrong |
| `Contradicted` | Source text materially conflicts with the stated claim |

---

## Phase 3.5 — Source Laundering Detection

**Purpose:** Detect cases where secondary sources are being used as if they were primary authority, or where primary source content has been laundered through secondary interpretations without direct verification.

### Detection Patterns

Scan all sources collected in Step 3 for these three patterns:

| Pattern | ID | Description | Action |
|---|---|---|---|
| **Interpretation presented as fact** | `interpretation_unverified` | A secondary source's interpretation of a statute/regulation is stated as the law itself, without the primary source having been directly fetched and confirmed | Flag; fetch primary source to verify |
| **Phantom citation** | `phantom_citation` | A source cites a specific article/section number but the cited primary source was never actually fetched or confirmed in Step 3 | Flag; fetch the cited primary source |
| **Source laundering** | `laundering_risk` | A secondary source paraphrases primary source content without pinpoint citation, and the analysis relies on this paraphrase as if it were the original text | Flag; either fetch primary or re-attribute to secondary |

### Procedure

1. For each source in Step 3 output where `source_authority == "secondary"` or `source_authority == "mixed"`:
   - Check if any conclusion or factual claim in the working notes relies on this source **as if it were primary authority**
   - Check if the source paraphrases a primary source without providing a pinpoint citation (specific article, section, paragraph)
   - Check if the corresponding primary source was actually fetched and confirmed in Step 3

2. For each detected pattern:
   - Record in the claim registry with pattern ID
   - If budget permits: fetch the underlying primary source to resolve
   - If budget exhausted: flag as `[Unverified — primary source not directly confirmed]`

3. **Blocking rule:** A conclusion that relies solely on a `laundering_risk` source without any directly-fetched primary source backing is **not permitted** to proceed to Step 5. Either:
   - Fetch the primary source (preferred), or
   - Re-attribute the claim transparently to the secondary source (e.g., "According to [Source]'s analysis..."), or
   - Mark the conclusion as `[Unverified]`

### Output (appended to claim registry)

```json
{
  "source_laundering_check": {
    "sources_scanned": 8,
    "flags": [
      {
        "source_code": "[S2]",
        "pattern": "laundering_risk",
        "description": "Law firm newsletter paraphrases GDPR Art. 17 requirements without pinpoint; primary text not fetched",
        "resolution": "Fetched GDPR Art. 17 directly from EUR-Lex; confirmed substance",
        "resolved": true
      },
      {
        "source_code": "[S4]",
        "pattern": "interpretation_unverified",
        "description": "Blog post claims '개인정보 보호법 제39조의3' requires X; article not directly verified",
        "resolution": "Marked [Unverified] — budget exhausted",
        "resolved": false
      }
    ],
    "summary": "2 flags detected, 1 resolved, 1 marked Unverified"
  }
}
```

---

## Phase 4 — Claim Registry Output

Write `output/claim-registry.json`:

```json
{
  "generated_at": "YYYY-MM-DD",
  "step": "4",
  "jurisdictions_covered": ["EU", "US", "KR"],
  "budget_used": { "EU": 3, "US": 2, "KR": 1 },
  "summary": {
    "total": 12,
    "verified": 9,
    "unverified": 2,
    "contradicted": 1
  },
  "anchors": [
    {
      "id": "A001",
      "type": "statute_article",
      "claim": "GDPR Article 17 grants data subjects a right to erasure",
      "jurisdiction": "EU",
      "status": "Verified",
      "verified_source": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679",
      "note": "Confirmed: Art. 17(1) text retrieved directly"
    },
    {
      "id": "A002",
      "type": "numerical_threshold",
      "claim": "72-hour breach notification to supervisory authority",
      "jurisdiction": "EU",
      "status": "Verified",
      "verified_source": "https://eur-lex.europa.eu/...",
      "note": "Confirmed: GDPR Art. 33(1)"
    },
    {
      "id": "A003",
      "type": "case_citation",
      "claim": "Schrems II — Case C-312/18",
      "jurisdiction": "EU",
      "status": "Contradicted",
      "verified_source": "https://curia.europa.eu/...",
      "note": "CORRECTION: Actual case number is C-311/18, not C-312/18. Prior output had wrong number."
    }
  ]
}
```

---

## Phase 5 — Inline Summary

After writing the registry, print to conversation:

```
[Step 4 — Fact-Check Complete]
Anchors checked: 12 | Verified: 9 | Unverified: 2 | Contradicted: 1
Source laundering flags: 2 (1 resolved, 1 unresolved)
Registry: output/claim-registry.json

⚠ Contradicted (1): A003 — Schrems II case number corrected (C-312/18 → C-311/18)
Unverified (2): A007 (US — CCPA §1798.100 text unconfirmed), A011 (JP — Act No. 57 date unconfirmed)
⚠ Laundering (1 unresolved): [S4] — 개인정보 보호법 제39조의3 interpretation from blog, primary not fetched
```

---

## Contradicted Anchor Handling

If `contradicted_count > 0`:

1. **Correct immediately** in working notes before proceeding to Step 5
2. **Materiality check**:
   - If correction changes the legal conclusion → trigger **partial Step 3 loop-back** (affected jurisdiction only, max 1 loop)
   - If correction is minor (typo in case number, article number off-by-one) → fix inline, continue
3. **Document the correction** in the registry `note` field
4. Step 8 Quality Gate will verify that no `Contradicted` anchor remains uncorrected in final output

---

## Downstream Usage (Steps 5–8)

- **Step 5** (Reliability Scoring): use registry status to inform source grading. A source with Contradicted anchors cannot be Grade A.
- **Step 6** (Analysis): tag analysis claims with registry IDs where applicable (e.g., `[A001: Verified]`). Promote `Unverified` anchors to `[Unverified]` inline tags.
- **Step 7** (Output): do not expose registry IDs in client-facing output; translate to `[Unverified]` tags only.
- **Step 8** (Quality Gate): confirm `contradicted_count == 0` in final output. If any Contradicted anchor is still uncorrected → block delivery.

---

## Failure Handling

| Condition | Response |
|---|---|
| Budget exhausted, HIGH-priority anchors still unverified | Mark remaining as `Unverified`, proceed, flag in Step 8 |
| Source unreachable | Try one alternative URL; if still unreachable → `Unverified` |
| Search returns no primary source result | Mark `Unverified`, do not guess |
| No anchors found in Step 3 output | Pass-through with empty registry; proceed to Step 5 |
| Step 3 output entirely from confirmed primary fetches | Mark all as pre-Verified; registry populated, Step 5 proceeds |
