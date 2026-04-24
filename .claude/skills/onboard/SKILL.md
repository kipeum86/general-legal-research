---
name: onboard
description: 최초 1회 인터뷰를 통해 user-config.json을 생성하고 knowledge/ 및 library/ 디렉토리를 초기화한다.
---

# Onboard

## Runtime Rule

Use this file as the compact onboarding checklist. Load
`references/packs/onboard.md` only when Step 0 auto-onboarding or manual `/onboard`
actually runs.

## Trigger

- Automatic: Step 0 calls this skill when `user-config.json` is missing.
- Manual: the user runs `/onboard` to reset configuration.

## Purpose

Collect the user's practice area, jurisdictions, and output defaults; write
`user-config.json`; initialize `knowledge/` and `library/`.

## Execution Checklist

Read `references/packs/onboard.md` and apply its detailed template, interview,
schema, directory, and completion-message rules.

1. Check whether `user-config.json` exists.
2. If it exists, summarize the current config and ask whether to reconfigure.
   - If the user declines, stop and keep the existing config.
   - If the user agrees, continue.
3. Ask the user to choose:
   - `[1] 템플릿 선택`
   - `[2] 직접 설정`
4. For template onboarding:
   - Show the six starter templates.
   - Read the selected file under `.claude/skills/onboard/templates/`.
   - Use it as the base `user-config.json`.
5. For custom onboarding:
   - Ask the seven interview questions from the reference pack.
   - Apply explicit defaults for missing answers.
6. Write `user-config.json` at the project root.
7. Initialize `knowledge/` and `library/` without overwriting existing user files.
8. Print the completion summary and library ingest hint.

## Output Contract

On completion, the repo should contain:

- `user-config.json`
- `knowledge/_index.md`
- `knowledge/statutes/`
- `knowledge/cases/`
- `knowledge/templates/`
- `knowledge/precedents/`
- `library/_index.md`
- `library/inbox/`
- `library/inbox/_processed/`
- `library/inbox/_failed/`
- `library/grade-a/`
- `library/grade-b/`
- `library/grade-c/`

`user-config.json` must include:

- `version`
- `created`
- `persona.name`
- `persona.title`
- `persona.firm`
- `practice.primary_area`
- `jurisdictions.primary`
- `research_defaults.mode`
- `research_defaults.output_format`
- `research_defaults.output_language`
- `kb.index_path`
- `library.index_path`

## Failure Handling

- Missing interview answer: apply the reference-pack default and disclose `[기본값 적용: ...]`.
- Existing directories: never overwrite user content; create only missing directories or missing `_index.md`.
- File write failure: report the path, check permissions, retry once, then give manual creation guidance.

## Quality Check

- [ ] `user-config.json` exists.
- [ ] `persona.name`, `jurisdictions.primary`, and `research_defaults.output_language` are filled.
- [ ] `knowledge/_index.md` exists.
- [ ] `library/_index.md` exists.
- [ ] Completion message was printed.
