# Fact-Checker Reference Pack

This pack contains the detailed Step 4 verification rules. It is loaded only when
`.claude/skills/fact-checker/SKILL.md` determines that Step 4 should run.

## Purpose

Intercept hallucinations before they propagate into legal analysis. Focus exclusively
on factual anchors: discrete, falsifiable claims that can be checked against a
primary source or a clearly identified secondary source.

## Phase 1 — Anchor Extraction

Scan Step 3 output and extract factual anchors into a structured working list.

### Anchor Types

| Type | Examples | Priority |
|---|---|---|
| `statute_article` | `GDPR Art. 17`, `상법 제342조` | HIGH |
| `case_citation` | `Case C-131/12`, `대법원 2020다12345` | HIGH |
| `effective_date` | `in force 25 May 2018`, `2023년 1월 개정` | HIGH |
| `numerical_threshold` | `72-hour notification`, `14-day cooling-off` | HIGH |
| `official_doc_title` | `Regulation (EU) 2016/679`, `개인정보 보호법` | MEDIUM |
| `regulatory_body_name` | `ICO`, `EDPB`, `금융위원회` | MEDIUM |
| `penalty_figure` | `up to EUR 20 million or 4% global turnover` | HIGH |
| `operative_language` | Safe harbor conditions, definition clauses, directly quoted operative statutory text | HIGH |

Extract `operative_language` only when Step 3 directly quotes or closely paraphrases
a specific legal-text phrase. Do not use it for general summaries of a statute's
purpose or effect.

Representative `operative_language` targets:

- Safe harbor conditions
- Scope carve-outs
- Core definition language
- Operative verbs such as `shall notify` or `is not required to`
- Threshold qualifiers such as `not encrypted` or `exceeds 500 records`

### Non-Anchors

Do not extract:

- Legal interpretations or conclusions
- General analysis
- Claims already directly quoted from a confirmed fetch; mark these pre-verified
- Hedged statements such as `may apply`, `arguably`, or `some scholars hold`

### Working List Shape

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
    },
    {
      "id": "A008",
      "type": "operative_language",
      "claim": "Cal. Civ. Code §1798.82(h)(1) defines PI to include data 'not encrypted or redacted'",
      "quoted_text": "not encrypted or redacted",
      "parent_statute": "Cal. Civ. Code §1798.82(h)(1)",
      "similar_statutes": ["Cal. Civ. Code §1798.81.5(d)(1)(A)"],
      "jurisdiction": "US-CA",
      "source_code": "[P3]",
      "source_url": "https://leginfo.legislature.ca.gov/...",
      "pre_verified": false
    }
  ]
}
```

For `operative_language` anchors, include:

- `quoted_text`: exact phrase to compare at word level
- `parent_statute`: subsection to which the phrase is attributed
- `similar_statutes`: adjacent or related statutes that cover the same subject

## Phase 2 — Prioritization

Sort anchors in this order:

1. HIGH priority with no source URL
2. HIGH priority with source URL but no direct quote
3. MEDIUM priority with no source URL, if budget permits
4. Confirmed direct quotes, marked `Verified` without additional fetch

## Phase 3 — Spot-Check

### Token Budget

| Jurisdictions | Max fetches per jurisdiction | Rationale |
|---|---:|---|
| 1 | 3 | Baseline |
| 2-3 | 3 | Standard multi-jurisdiction workflow |
| 4+ | 2 | Deep-researcher mode; tighter budget |

### Verification Procedure

For each prioritized anchor:

1. If a source URL is available, fetch the specific article or section and confirm the claim against retrieved text.
2. If no source URL is available, use one search query to locate the primary source and then fetch it.
3. If the primary source cannot be located in one attempt, mark `Unverified`.
4. For Korean law, fetch law.go.kr first.
5. For EU law, fetch EUR-Lex first.
6. Record `Verified`, `Unverified`, or `Contradicted`.

### PDF/DOCX Source Verification

When a source URL or file path points to a PDF or DOCX:

1. Convert the document to Markdown using `mcp__markitdown__convert_to_markdown`.
2. If the source is from `library/`, check `knowledge/library-converted/` first.
3. Search the converted text for the specific claim:
   - `statute_article`: article number, such as `제17조` or `Article 17`
   - `case_citation`: case number
   - `numerical_threshold`: exact number
   - `effective_date`: date pattern in the same document section
4. If conversion fails, mark `Unverified — PDF text extraction failed`.
5. Do not count a failed PDF/DOCX conversion against the token budget.

### Status Definitions

| Status | Meaning |
|---|---|
| `Verified` | Source text confirms the claim within acceptable paraphrase |
| `Unverified` | Could not confirm within budget; not necessarily wrong |
| `Contradicted` | Source text materially conflicts with the stated claim |

## Phase 3.3 — Similar-Statute Cross-Check

Trigger this phase when at least one `operative_language` anchor has a non-empty
`similar_statutes` list.

For each `operative_language` anchor:

1. Fetch or reuse the primary-source text for `parent_statute`.
2. Confirm that `quoted_text` appears in that subsection verbatim, allowing trivial whitespace or punctuation variance.
3. If not found, search adjacent subsections of the same statute.
4. If still not found, search each statute in `similar_statutes`.
5. If the phrase appears elsewhere, mark `Contradicted` and record the actual location.
6. If the phrase appears nowhere, mark `Contradicted — quoted language not located in primary source`.
7. Do not count this check against the per-jurisdiction token budget.

Create an internal Similar-Statute Disambiguation Table:

| Quoted Phrase | Attributed To | Actually Found In | Match? |
|---|---|---|---|
| `not encrypted or redacted` | §1798.82(h)(1) | §1798.81.5(d)(1)(A) | MISMATCH |
| `first name or first initial and last name` | §1798.82(h)(1) | §1798.82(h)(1) | OK |

When any row is `MISMATCH`:

- Set the affected anchor to `Contradicted`.
- Record the exact location in the claim registry `note`.
- Compare against the Step 3 Statute Boundary Table if one exists.

Append this shape to the claim registry when applicable:

```json
{
  "similar_statute_check": {
    "anchors_checked": 2,
    "mismatches": [
      {
        "anchor_id": "A008",
        "quoted_text": "not encrypted or redacted",
        "attributed_to": "Cal. Civ. Code §1798.82(h)(1)",
        "actually_found_in": "Cal. Civ. Code §1798.81.5(d)(1)(A)",
        "status": "Contradicted"
      }
    ]
  }
}
```

## Phase 3.5 — Source Laundering Detection

### Purpose

Detect when secondary sources are being used as if they were primary authority, or
when primary-source content has been laundered through secondary interpretations
without direct verification.

### Detection Patterns

| Pattern | ID | Description | Action |
|---|---|---|---|
| Interpretation presented as fact | `interpretation_unverified` | A secondary source's interpretation is stated as law without fetching the primary source | Flag and fetch primary source |
| Phantom citation | `phantom_citation` | A source cites an article or section that Step 3 never fetched or confirmed | Flag and fetch cited primary source |
| Source laundering | `laundering_risk` | A secondary source paraphrases primary source content without pinpoint citation and the analysis relies on it as original text | Flag; fetch primary or re-attribute |

### Procedure

For each Step 3 source with `source_authority == "secondary"` or `source_authority == "mixed"`:

1. Check whether any conclusion relies on the source as if it were primary authority.
2. Check whether the source paraphrases a primary source without a pinpoint citation.
3. Check whether the corresponding primary source was fetched and confirmed in Step 3.
4. Record each pattern in the claim registry.
5. If budget permits, fetch the underlying primary source.
6. If budget is exhausted, flag `[Unverified — primary source not directly confirmed]`.

Blocking rule: a conclusion that relies solely on a `laundering_risk` source is not
permitted to proceed to Step 5 until one of these occurs:

- The primary source is fetched.
- The claim is re-attributed transparently to the secondary source.
- The conclusion is marked `[Unverified]`.

Append this shape to the claim registry:

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

## Phase 5 — Inline Summary

After writing the registry, print:

```text
[Step 4 — Fact-Check Complete]
Anchors checked: 12 | Verified: 9 | Unverified: 2 | Contradicted: 1
Source laundering flags: 2 (1 resolved, 1 unresolved)
Registry: output/claim-registry.json

Contradicted (1): A003 — Schrems II case number corrected (C-312/18 -> C-311/18)
Unverified (2): A007 (US — CCPA §1798.100 text unconfirmed), A011 (JP — Act No. 57 date unconfirmed)
Laundering (1 unresolved): [S4] — 개인정보 보호법 제39조의3 interpretation from blog, primary not fetched
Similar-statute cross-check: 2 anchors checked, 0 mismatches
```

## Contradicted Anchor Handling

If `contradicted_count > 0`:

1. Correct the contradicted anchor in working notes before proceeding to Step 5.
2. Check materiality.
3. If the correction changes the legal conclusion, run a partial Step 3 loop-back for the affected jurisdiction only, max one loop.
4. If the correction is minor, fix inline and continue.
5. Document the correction in the registry `note` field.
6. Step 8 must verify that no `Contradicted` anchor remains uncorrected.

## Failure Handling

| Condition | Response |
|---|---|
| Budget exhausted, HIGH-priority anchors still unverified | Mark remaining as `Unverified`, proceed, flag in Step 8 |
| Source unreachable | Try one alternative URL; if still unreachable, mark `Unverified` |
| Search returns no primary source result | Mark `Unverified`, do not guess |
| No anchors found in Step 3 output | Pass through with empty registry; proceed to Step 5 |
| Step 3 output entirely from confirmed primary fetches | Mark all as pre-verified; populate registry; proceed to Step 5 |
