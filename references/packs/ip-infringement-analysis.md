# IP Infringement Analysis Reference Pack

This pack contains detailed IP infringement memo frameworks for
`.claude/skills/ip-infringement-analysis/SKILL.md`.

## Quick Start

1. Identify the IP rights at issue.
2. Characterize the accused activity.
3. Apply the type-specific framework: Patent, Trademark, Copyright, or Trade Secret.
4. Assess defenses and vulnerabilities.
5. Evaluate available remedies.
6. State overall assessment with confidence level.

Analyze each IP type separately when multiple rights are at issue.

## Step 1 — IP Rights Identification

| Field | Detail |
|---|---|
| IP Type | Patent / Trademark / Copyright / Trade Secret |
| Registration/Application No. | |
| Filing/Priority Date | |
| Owner/Claimant | |
| Key Claims/Mark/Work Description | |
| Status | Active / Expired / Pending |

## Step 2 — Accused Activity

| Field | Detail |
|---|---|
| Accused party | |
| Product/service/activity | |
| Date of first use | |
| Geographic scope | |
| Commercial context | |

## Step 3 — Type-Specific Analysis

### Patent Infringement

1. Claim construction: construe disputed terms under controlling law; mark unconfirmed authority `[Unverified]`.
2. Literal infringement: apply the all-elements rule through limitation-by-limitation comparison.
3. Doctrine of equivalents: apply function-way-result or insubstantial differences; check prosecution history estoppel.
4. Means-plus-function: identify Section 112(f) limitations and corresponding structure.
5. Indirect infringement: analyze inducement and contributory theories separately.
6. Validity challenges: anticipation, obviousness, enablement, and written description.

Claim chart:

| Claim Element | Accused Feature | Literal? | DOE? | Notes |
|---|---|---|---|---|
| [Limitation 1] | | Y/N | Y/N | |
| [Limitation 2] | | Y/N | Y/N | |

A single missing limitation defeats literal infringement on that claim.

### Trademark Infringement

Identify the controlling circuit's likelihood-of-confusion test, such as Polaroid,
Sleekcraft, or Lapp, and apply the factors.

| Factor | Analysis | Weight |
|---|---|---|
| Similarity of marks: sight, sound, meaning, commercial impression | | |
| Relatedness of goods/services | | |
| Strength of senior mark: inherent plus acquired distinctiveness | | |
| Evidence of actual confusion | | |
| Defendant's intent | | |
| Consumer sophistication | | |
| Channels of trade / marketing convergence | | |
| Likelihood of expansion into related markets | | |

If the mark is famous, assess dilution by blurring or tarnishment. Evaluate
descriptive fair use, nominative fair use, and First Amendment defenses where
applicable.

### Copyright Infringement

1. Ownership: valid registration and chain of title.
2. Access: direct or circumstantial evidence.
3. Substantial similarity: objective/extrinsic analysis plus ordinary-observer or intrinsic analysis as applicable.
4. Idea/expression filtration: exclude ideas, facts, scenes a faire, merger doctrine, and other unprotectable elements.
5. De minimis: assess whether copying falls below the actionable threshold.

Fair use:

| Factor | Analysis | Favors |
|---|---|---|
| Purpose and character, including transformativeness | | P / D |
| Nature of copyrighted work | | P / D |
| Amount and substantiality used | | P / D |
| Market effect | | P / D |

### Trade Secret Misappropriation

1. Identification: describe each alleged trade secret with specificity.
2. Qualification: independent economic value from secrecy plus reasonable secrecy measures.
3. Misappropriation method: improper means or breach of confidentiality obligation.
4. Inevitable disclosure: apply only in jurisdictions recognizing the doctrine.
5. Restrictive covenants: analyze NDA/non-compete scope, enforceability, and temporal/geographic limits.

## Step 4 — Defenses and Vulnerabilities

| Defense | Applicability | Risk Level |
|---|---|---|
| Statute of limitations / laches | | High/Med/Low |
| Estoppel: prosecution, equitable, licensee | | |
| Exhaustion / first sale | | |
| Independent creation / reverse engineering | | |
| Invalidity / unenforceability | | |
| Fair use / nominative use | | |
| Unclean hands | | |

## Step 5 — Remedies Assessment

| Remedy | Availability | Estimated Range |
|---|---|---|
| Lost profits | | |
| Reasonable royalty | | |
| Disgorgement of profits | | |
| Statutory damages | | |
| Enhanced/treble damages for willfulness | | |
| Attorneys' fees / exceptional case | | |
| Preliminary injunction | | |
| Permanent injunction | | |

All damages estimates are preliminary and must be validated with economic expert
analysis.

## Step 6 — Overall Assessment

| Item | Assessment |
|---|---|
| Infringement likelihood | Strong / Moderate / Weak |
| Strongest arguments for infringement | |
| Greatest vulnerabilities | |
| Recommended course of action | Litigate / Settle / License / Monitor |
| Settlement valuation range | |

Do not state ultimate legal conclusions without a confidence level and uncertainty
qualifications.

## Troubleshooting

| Issue | Resolution |
|---|---|
| Uncertain claim construction | Flag ambiguous terms; present competing constructions with likelihood assessment |
| Circuit split on likelihood-of-confusion factors | Identify controlling circuit; note split if forum selection matters |
| Mixed literal/DOE results across claims | Analyze each claim independently; one infringed claim can suffice |
| Incomplete accused instrumentality info | Note gaps; qualify as preliminary; request missing specs before finalizing |
| Foreign IP rights implicated | Flag Paris Convention, Berne Convention, or TRIPS issues; analyze domestic and foreign rights separately |

## Guidelines

- Cite controlling authority from the relevant jurisdiction.
- Flag persuasive-only authority from other circuits.
- Use `[Unverified]` for any citation not confirmed against source documents.
- Flag privilege, work-product, and ethical issues, including conflicts.
- Output is draft work product and must note that it does not constitute legal advice.
