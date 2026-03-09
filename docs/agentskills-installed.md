# AgentSkills Installed Set

Installed date: 2026-03-05
Source repository: `CaseMark/skills` (`skills/legal/*`)
Source site: `https://agentskills.legal`

Installed skills:
- `legal-research`
- `legal-research-summary`
- `regulatory-summary`
- `compliance-summaries`
- `gambling-law-summary`
- `privacy-law-updates`
- `antitrust-investigation-summary`
- `ip-infringement-analysis`
- `terms-of-service`
- `api-acceptable-use-policy`
- `client-memo`
- `judgment-summary`
- `case-briefs`
- `cyber-law-compliance-summary`

Install command used:

```powershell
python "C:/Users/kplee/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" `
  --repo CaseMark/skills `
  --path `
  skills/legal/legal-research `
  skills/legal/legal-research-summary `
  skills/legal/regulatory-summary `
  skills/legal/compliance-summaries `
  skills/legal/gambling-law-summary `
  skills/legal/privacy-law-updates `
  skills/legal/antitrust-investigation-summary `
  skills/legal/ip-infringement-analysis `
  skills/legal/terms-of-service `
  skills/legal/api-acceptable-use-policy `
  skills/legal/client-memo `
  skills/legal/judgment-summary `
  skills/legal/case-briefs `
  skills/legal/cyber-law-compliance-summary `
  --dest "general-legal-research/.claude/skills"
```
