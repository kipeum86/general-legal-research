# TODOS

## Phase 2: MCP Integration
**What:** When GDPR-expert and PIPA-expert become MCP servers, add MCP client calls to lookup chain (local cache → MCP → API).
**Why:** Avoids duplicating 2,000+ already-cached articles. Single source of truth per jurisdiction.
**Context:** Design doc at ~/.gstack/projects/kipeum86-general-legal-research/kpsfamily-main-design-20260327-001523.md. Conflict resolution rule: MCP wins over local cache.
**Depends on:** MCP server buildout in GDPR-expert and PIPA-expert (separate projects).

## Phase 2: Contextual Cross-Reference Resolution
**What:** Add state machine parser to resolve '같은 법', '같은 조', '동법' contextual references.
**Why:** Would capture ~60% more cross-references (currently only explicit 제X조 and 「법률명」 patterns are extracted).
**Context:** Requires tracking last-mentioned law name during article text parsing. See eng review outside voice challenge #3.
**Depends on:** Phase 1 cross-ref extraction working and accumulating data.
