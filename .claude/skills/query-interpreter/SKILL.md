---
name: query-interpreter
description: Parse legal research queries into structured parameters, generate clarification prompts when needed, and produce explicit assumptions for missing inputs.
---

# Query Interpreter

Use this skill at Step 1 for every new user query.

## Inputs

- User query text
- Optional explicit user constraints

## Required Output Object

Return a JSON-like structure with:
- `query_summary`
- `jurisdictions` (array)
- `as_of_date` (ISO date)
- `product_or_business_model`
- `target_users`
- `regulatory_domains` (1-10 map)
- `output_mode` (`A|B|C|D|auto`)
- `output_language`
- `assumptions` (array of explicit assumptions)
- `ambiguities` (array)
- `clarification_questions` (array, max 5)

Read `references/parameter-schema.md` before producing output.

## Rules

1. Resolve what you can directly from user text.
2. If key parameters are missing, create assumptions and list them explicitly.
3. Ask clarification questions only when ambiguity is material.
4. Keep clarification to one round by default (max two rounds total).
5. If user says proceed, use assumptions and continue.

## Quality Check

- Jurisdiction and as-of date are present (explicit or assumed).
- Output mode and language are decided (or set to `auto` + assumption).
- No legal conclusion is produced at this step.
