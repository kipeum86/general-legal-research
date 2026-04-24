# Project Overrides

This directory is reserved for project-owned notes, patches, and overlay instructions that should survive vendor refreshes.

Do not edit vendored citation-auditor skill files directly:

- `.claude/skills/citation-auditor/`
- `.claude/skills/verifiers/`

For citation audit changes, keep project-specific integration code in `scripts/` when possible. If a future change requires modifying vendored skill text or verifier routing, document the intended override here first and then choose one of:

1. upstream the change to the vendor source,
2. maintain a project fork,
3. add a project-owned wrapper that leaves the vendor copy unchanged.

Keep boundary decisions in this file or in another public-safe project document before changing vendored files.
