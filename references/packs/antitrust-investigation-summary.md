# Antitrust Investigation Summary Reference Pack

This pack contains detailed internal antitrust investigation memo rules for
`.claude/skills/antitrust-investigation-summary/SKILL.md`.

## Quick Start

Before drafting, collect:

- Investigation charter: directing authority, investigators, dates, privilege posture.
- Factual record: triggering complaint, contracts, communications, product docs, regulator correspondence.
- Interview materials: Upjohn-warned summaries with role, topics, and key assertions.
- Market context: products, monetization, rivals, switching costs, network effects, prior assessments.
- Remediation status: stop-gap steps, policy updates, product or contract changes.
- Procedural posture: anticipated litigation, M&A, preservation holds.

If critical inputs are missing, ask:

```text
To provide a competent risk assessment, I require [specific items].
```

## Section 1 — Privilege Header

Every page should carry:

```text
PRIVILEGED & CONFIDENTIAL / INTERNAL LEGAL WORKFLOW DRAFT
Prepared to support internal legal assessment regarding antitrust
compliance and potential exposure. Intended solely for [Company]
senior leadership and the Board of Directors. Do not forward outside
those who need to know for internal legal review.
```

## Section 2 — Executive Summary

Use BLUF format. Frame each finding as:

```text
Issue -> Key Facts -> Legal Significance -> Risk Level -> Recommended Action
```

Anchor three risk pillars:

- Legal Liability: strength of potential claims.
- Regulatory Scrutiny: DOJ/FTC enforcement probability.
- Reputational Impact: downstream effects on partners, developers, and the public.

## Section 3 — Investigation Scope and Methodology

Cover:

- triggering event
- time period
- products or business units
- conduct categories
- document sources
- custodian and interview counts
- analyses performed
- known gaps

Be specific without creating a discovery roadmap.

## Section 4 — Key Findings

Organize by issue, not by witness or chronology.

| Theory | Statute | Key Elements |
|---|---|---|
| Monopolization | Sherman Act Section 2 | Monopoly power plus willful acquisition or maintenance; mark unconfirmed citations `[Unverified]` |
| Vertical restraints | Sherman Act Section 1 | Agreement plus unreasonable restraint under rule of reason |
| Acquisitions | Clayton Act Section 7 | May substantially lessen competition; verify current Merger Guidelines |
| Unfair methods | FTC Act Section 5 | Broader than Sherman/Clayton; can reach gatekeeping conduct; mark unconfirmed citations `[Unverified]` |

Tech-platform issue checklist:

- [ ] Self-preferencing: ranking, defaults, API access
- [ ] Tying / bundling
- [ ] De facto exclusivity: rebates, defaults
- [ ] Anti-steering provisions
- [ ] Interoperability / API restrictions
- [ ] MFN / parity clauses
- [ ] Killer acquisitions
- [ ] Ecosystem lock-in / switching cost manipulation

For each finding, cover:

1. conduct
2. record evidence, including hot documents
3. procompetitive rationale
4. contrary evidence
5. uncertainties

## Section 5 — Risk Assessment

Assess three layers:

| Layer | Question |
|---|---|
| Legal | Plausible statutory theory? |
| Factual | Evidence strength? Discovery exposure? |
| Enforcement | DOJ/FTC likely to prioritize? Mark current-posture uncertainty `[Unverified]` |

Also address:

- relevant market definition
- key pivots
- counterfactual analysis
- regulator or plaintiff theory framing

Avoid pseudo-quantification such as `70% chance`; use risk drivers.

## Section 6 — Remediation Recommendations

Frame recommendations as strategic risk mitigation, not admission.

| Tier | Timeframe | Examples |
|---|---|---|
| Immediate | 0-30 days | Stop-gap changes, messaging |
| Structural | 1-6 months | Policy/contract revisions, approval pathways |
| Monitoring | Ongoing | Audits, training, metrics |

Tie each recommendation to a finding. Assign ownership and timeline. Use advisory
language such as `revise provisions that could be characterized as conditioning`,
not `cease illegal tying`.

## Section 7 — Regulatory Exposure and Readiness

Cover:

- pending inquiries
- likely theories mapped to facts
- current agency-priority uncertainty marked `[Unverified]`
- key risk documents and witnesses
- preparedness status
- strategic options

Readiness checklist:

- [ ] Preservation holds functioning
- [ ] External counsel retained
- [ ] Response protocol for CIDs/subpoenas
- [ ] Messaging guidelines updated
- [ ] HSR considerations if M&A dimension exists

## Drafting Rules

### Privilege-Protective

- Use advisory language: `evidence could be interpreted as...`, not `the company fixed prices`.
- Separate facts from analysis from recommendations.
- Never make conclusory admissions.
- Use phrases like `potential theories`, `enforcement risk`, and `facts that could be argued to support`.
- Mark unconfirmed privilege-framework citations `[Unverified]`.

### Adversarial Resilience

- Draft as if a regulator will read despite privilege claims.
- Test every sentence: if quoted out of context in a complaint, would it be damaging?
- Address hot documents directly: acknowledge, contextualize, assess.
- Balance exclusionary findings against procompetitive benefits.

### Anti-Hallucination

- Every citation and doctrinal statement must be verified or marked `[Unverified]`.
- Every factual assertion must trace to a document, interview, or dataset.
- Separate verified facts from counsel's assessment.
- Confirm the record supports characterizations like `systematic` or `widespread`.

## Scope and Ethics

- Present risk in circuit-neutral terms unless the circuit is specified and verified.
- Counsel represents the organization under Model Rule 1.13, not individuals.
- A qualified legal reviewer must review all output.
- This is a drafting aid, not legal advice.
- Do not input unnecessary personal data.
- Follow the organization's secure AI workflow.
