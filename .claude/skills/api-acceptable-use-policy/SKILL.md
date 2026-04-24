---
name: api-acceptable-use-policy
description: >
  Drafts a standalone API Acceptable Use Policy (AUP) for incorporation by
  reference into a master API license or terms-of-service agreement. Produces a
  publication-ready template with prohibited-use matrix, developer security
  checklist, graduated enforcement framework, AI/ML training restrictions, and
  versioning playbook. Trigger when a user needs to draft or update an API AUP,
  separate behavioral rules from core API terms, define prohibited API uses,
  add enforcement or change-management mechanics, or mentions acceptable use
  policy, developer security requirements, or API enforcement.
tags:
  - drafting
  - policy
  - transactional
---

# API Acceptable Use Policy

## Runtime Rule

Use this file as the compact API AUP drafting checklist. Load
`references/packs/api-acceptable-use-policy.md` only when drafting or revising an
API Acceptable Use Policy.

## Purpose

Draft a standalone AUP that is incorporated by reference into a master agreement.
Keep fast-changing behavioral and security rules in the AUP while stable commercial
and contractual rights stay in the master agreement.

## Execution Checklist

Read `references/packs/api-acceptable-use-policy.md` and apply its detailed intake,
allocation, matrix, template, post-draft, and pitfalls rules.

1. Run pre-draft intake unless the user says `use defaults` or `just draft`.
2. Apply defaults and label them when the user omits details.
3. Map AUP vs. master agreement scope using the allocation table.
4. Build a prohibited-use matrix with severity and enforcement treatment.
5. Include developer security requirements.
6. Define graduated enforcement with immediate suspension for severe violations.
7. Define versioning and notice mechanics.
8. Generate a publication-ready AUP template with all `[BRACKETED]` placeholders.
9. Run post-draft alignment questions.
10. Include the required disclaimer in every output.

## Intake Fields

Ask for:

- company legal name
- API/product name
- authentication method
- access model
- use model
- data categories
- policy positions on scraping, benchmarking, AI/ML training, caching, and bug bounty
- `SECURITY_EMAIL`
- `SUPPORT_EMAIL`
- `LEGAL_EMAIL`
- rate-limit documentation URL

Defaults:

- governing law: U.S. state TBD; B2B developers
- API category: general SaaS
- access model: public/self-service
- data scope: personal data possible; no PHI/PCI/children's data
- AI/ML training: prohibited unless expressly authorized in writing
- routine changes: effective upon posting
- material adverse changes: 30 days' advance notice
- emergency changes: immediate
- enforcement: graduated; immediate suspension for severe/security violations

## Output Contract

The deliverable must include:

- AUP-to-license allocation summary
- prohibited-use section
- security requirements
- rate limits / caching / fair use section
- monitoring and enforcement section
- versioning and change notice section
- contact section
- post-draft alignment questions when appropriate
- all unresolved placeholders in `[BRACKETED]` form

## Quality Checklist

- [ ] No conflict between AUP and master agreement.
- [ ] Prohibited uses include severity and enforcement action.
- [ ] Security requirements cover credentials, TLS, and incident reporting.
- [ ] Enforcement includes cure, throttle, suspension, termination, and appeal mechanics.
- [ ] Versioning includes notice channels, material-change standard, and archive URL.
- [ ] AI/ML restriction aligns with commercial intent.
- [ ] Rate limits reference documentation URL instead of hard-coded numbers.
- [ ] Monitoring disclosure coordinates with the master agreement.
- [ ] All `[BRACKETED]` placeholders are clear.

## Required Disclaimer

> THIS POLICY IS A DRAFTING AID AND REQUIRES REVIEW BY QUALIFIED LEGAL COUNSEL BEFORE PUBLICATION. IT DOES NOT CONSTITUTE LEGAL ADVICE.
