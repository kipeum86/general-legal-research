# Terms of Service Reference Pack

Detailed drafting rules for `.claude/skills/terms-of-service/SKILL.md`. Load this pack only when drafting, tailoring, or quality-checking a Terms of Service agreement.

## Intake Table

Gather before drafting:

| Item | Required | Notes |
|---|---|---|
| Company legal name, address, contact email | Yes | Contracting entity |
| Service name and URL/app identifiers | Yes | Defines "Service" |
| Eligibility/age minimum | Yes | COPPA if under 13 [Unverified] |
| Countries/states served | Yes | Triggers GDPR/CCPA/other |
| Payment terms | If paid | Auto-renew, cancellation, refunds |
| IP assets | Yes | Trademarks, content ownership |
| UGC + moderation approach | If UGC | DMCA workflow |
| APIs/integrations | If any | Third-party terms |

## Clause Selection

| Clause | Include When | Key Points |
|---|---|---|
| Acceptance mechanism | Always | Clickwrap preferred; continued-use fallback |
| Accounts & security | Accounts exist | Credentials, MFA, responsibility |
| Acceptable use | Always | Prohibited conduct list |
| UGC license | UGC exists | Scope, duration, takedown |
| IP ownership | Always | Service IP, limited license |
| Payments | Paid tiers | Billing, taxes, refunds |
| Termination | Always | For cause/at will, effects |
| Disclaimers | Always | AS IS / AS AVAILABLE |
| Liability cap | Always | Cap amount, exclusions, carve-outs |
| Indemnity | B2B or UGC | IP claims, violations |
| Dispute resolution | Always | Governing law, venue/arbitration |

## Drafting Sequence

1. Definitions & acceptance - clickwrap, versioning, and effective date.
2. Eligibility & authority - age, entity authority, and lawful use.
3. Account rules - registration, security, and accuracy.
4. Acceptable use - law compliance and prohibited conduct.
5. UGC & IP - ownership, license grant, feedback assignment, and takedown.
6. Third-party services - links, integrations, no endorsement, and third-party terms.
7. Payment terms - billing, taxes, renewals, cancellation, refunds, and chargebacks if applicable.
8. Termination & suspension - rights, effects, and survival.
9. Disclaimers & limitation of liability.
10. Indemnification if applicable.
11. Dispute resolution - law, venue, arbitration, carve-outs, and mandatory consumer rights.
12. Boilerplate - severability, assignment, notices, force majeure, entire agreement, and interpretation.

## Prohibited Conduct

Always include prohibitions on:

- Illegal activity, fraud, and misrepresentation.
- Malware, phishing, and security bypass.
- Unauthorized access, scraping, harvesting, and rate-limit evasion.
- IP infringement or circumvention of technical protections.
- Harassment, hate, abusive conduct, or threats.
- Interference with service availability or integrity.

## Dispute Resolution Selection

| Option | Use When | Notes |
|---|---|---|
| Arbitration + class waiver | B2B or low-risk consumer | Include small-claims carve-out |
| Court litigation | High consumer scrutiny | Specify venue + jury waiver |
| EU consumer carve-out | Serving EU | Mandatory local rights preserved |

## Sample Clauses

### UGC License

Edit scope as needed.

```text
User Content License. You retain ownership of Your Content. You grant Company a worldwide, non-exclusive, royalty-free, sublicensable, transferable license to host, store, use, display, reproduce, modify for technical purposes, distribute, and create derivative works of Your Content solely to operate, improve, and promote the Service. License ends upon deletion except for content already shared or cached in ordinary operation.
```

### Liability and Warranty

Edit cap and carve-outs as needed.

```text
Disclaimer. THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS, AND NON-INFRINGEMENT, TO THE MAXIMUM EXTENT PERMITTED BY LAW.

Limitation. TO THE MAXIMUM EXTENT PERMITTED BY LAW, COMPANY SHALL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR LOSS OF DATA, PROFITS, OR REVENUE. TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNTS PAID BY YOU TO COMPANY IN THE 12 MONTHS BEFORE THE CLAIM (OR $100 IF NONE). EXCEPTIONS: LIABILITY FOR DEATH/PERSONAL INJURY, FRAUD, OR WILLFUL MISCONDUCT WHERE PROHIBITED.
```

## Privacy and Data Hooks

- Incorporate Privacy Policy by reference.
- Specify data processing roles such as controller/processor where relevant.
- Reference security measures at a high level only; do not promise beyond actual controls.
- Address cross-border transfers if applicable, including EU SCCs [Unverified].

## Final QC Checklist

- [ ] Definitions are consistent and capitalization is standardized.
- [ ] Effective date and version history are included.
- [ ] Notice method and update mechanism are defined.
- [ ] Survival clauses are listed.
- [ ] Hyperlinks to all incorporated policies work.

## Pitfalls

- Browsewrap is weak. Prefer clickwrap acceptance; browsewrap risks unenforceability.
- EU/UK users require GDPR-consistent rights hooks and consumer protections; avoid overbroad waivers. [Unverified]
- California residents may require CCPA/CPRA notice hooks and no-sale/share language. [Unverified]
- UGC services need DMCA agent designation and takedown procedure. [Unverified]
- Unconscionability risk rises with unreasonable liability caps or consumer waivers.
- Regulated industries such as health, finance, and telecom require additional statutory modules.
