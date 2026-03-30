# kordoc Integration Evaluation Log

Date: 2026-03-31
Status: Recommended for partial adoption
Source reviewed: `https://github.com/chrisryugj/kordoc`

## Context

This note records the assessment made after reviewing whether `kordoc` should be introduced into this repository.

Current repository strength:

- Legal research workflow orchestration
- Official-source-first collection via `korean-law-mcp` and Open Law API
- Local `library/` ingestion based on `MarkItDown`

Current repository gap:

- No general `.hwp` / `.hwpx` ingestion path in `library-ingest.py`
- Korean public-sector document parsing is weaker than the legal research stack

## Recommendation

Adopt `kordoc` as a document parsing layer, not as a replacement for the legal research engine.

Recommended role for `kordoc`:

- Add `.hwp` and `.hwpx` support to `library/` ingestion
- Optionally handle Korean government-style PDFs when table or form extraction matters
- Expose structured parsing only where the workflow benefits from it

Not recommended:

- Replacing `korean-law-mcp`
- Replacing Open Law API retrieval
- Replacing the official-source-first research model
- Fully replacing `MarkItDown` for all document types

## Why This Fits

### 1. It fills a real gap in the current repo

`scripts/library-ingest.py` currently supports:

- `.pdf`
- `.docx`
- `.pptx`
- `.xlsx`
- `.html`

It explicitly marks the following as unsupported:

- `.hwp`
- `.hwpx`

That means the current project can research Korean law well, but still has a weak path for ingesting many Korean source documents and annex materials that arrive as Hancom files.

### 2. `kordoc` is broader than a simple format converter

Based on the reviewed repository, `kordoc` provides:

- `HWP/HWPX/PDF -> Markdown`
- structured blocks (`IRBlock[]`)
- metadata extraction
- document comparison
- form field extraction
- page-range parsing
- MCP server support

This makes it useful not only for conversion, but also for structured downstream analysis when needed.

### 3. It matches the project's existing operating model

This repository already uses MCP-backed tools through `.mcp.json`, including `korean-law-mcp` via `npx`.

Because `kordoc` also ships an MCP server (`kordoc-mcp`), it can be introduced in a way that is operationally consistent with the current toolchain.

## Important Boundary

`kordoc` should be treated as a parsing and document-structure tool.

It should not become the authority layer for legal research.

Authoritative legal content should still come from:

- official portals
- `korean-law-mcp`
- Open Law API
- other primary legal sources already prioritized by this project

In other words:

- use `kordoc` to parse documents better
- do not use `kordoc` to replace official-law retrieval and verification

## Recommended Integration Shape

### Phase 1

Add `kordoc` only for `.hwp` / `.hwpx` ingestion.

Target:

- `scripts/library-ingest.py`

Behavior:

- keep `MarkItDown` as the default path for current supported formats
- route `.hwp` / `.hwpx` files through `kordoc`
- store original file, converted Markdown, and parse warnings together where practical

### Phase 2

Experiment with `kordoc` for Korean public-sector PDFs only when one of these is true:

- tables are important
- forms are important
- `MarkItDown` output is poor

This should be opt-in first, not a silent replacement.

### Phase 3

Only after Phase 1 and 2 prove useful, consider exposing `kordoc-mcp` to the agent layer.

Possible uses at that stage:

- table extraction during source review
- form extraction from administrative templates
- document diff for regulation version comparison or annex comparison

## Risks and Cautions

### 1. Do not collapse source authority into parser output

Parsed Markdown is still a derived artifact.

Source grading should remain tied to:

- the original document
- its provenance
- official publisher status

not merely to the text emitted by the parser.

### 2. Avoid premature full replacement

`MarkItDown` still fits the repository well for general-purpose:

- PDF
- DOCX
- PPTX
- HTML-ish ingestion flows

Replacing it everywhere would add migration cost without clear upside.

### 3. Keep the legal workflow stable

The repository's advantage is not document parsing alone.
Its main advantage is the source-grounded legal workflow and verification model.

The integration should protect that.

## Bottom Line

`kordoc` looks worth introducing, but narrowly and deliberately.

Best framing:

- yes to Korean document parsing expansion
- no to research-engine replacement

Best first move:

1. add `kordoc` support to `library-ingest.py` for `.hwp/.hwpx`
2. keep `MarkItDown` for existing default paths
3. validate results on real Korean government documents before broader rollout
