# citation-auditor vendor stamp

This directory was populated by `scripts/vendor-into.sh` from the citation-auditor repo.

- Version: **v1.3.0**
- Source commit: 6adf638
- Source tag:    v1.2.0
- Vendored at:   2026-04-24 (copied from game-legal-research vendor drop, commit 970b1ed)
- Target:        /Users/kpsfamily/코딩 프로젝트/general-legal-research

To update this vendor copy, run `./scripts/vendor-into.sh /Users/kpsfamily/코딩 프로젝트/general-legal-research` from the citation-auditor repo (latest version).

Do not hand-edit files under `.claude/skills/citation-auditor/` or `.claude/skills/verifiers/` — they will be overwritten on the next vendor run. If you need to customize a verifier, copy it to a new folder under `.claude/skills/verifiers/my-<name>/` instead.

Local integration patch applied in this repository:
- Normalized workflow references to conditional Step 9.
- Fixed the UK verifier routing regex.

Carry these changes upstream before the next vendor refresh, or re-apply them after vendoring.
