# Parameter Schema (Step 1 Output)

```json
{
  "query_summary": "string",
  "jurisdictions": [
    {
      "code": "kr|us|eu|uk|jp|de|...",
      "name": "string",
      "level": "national|federal|state|supranational|mixed"
    }
  ],
  "as_of_date": "YYYY-MM-DD",
  "product_or_business_model": "string",
  "target_users": "string",
  "regulatory_domains": [
    {
      "id": 1,
      "name": "Gambling & chance mechanics",
      "selected": true,
      "reason": "string"
    }
  ],
  "output_mode": "A|B|C|D|auto",
  "output_language": "en|ko|ja|...",
  "assumptions": ["string"],
  "ambiguities": ["string"],
  "clarification_questions": ["string"]
}
```

Mandatory minimum fields:
- `jurisdictions` (non-empty with assumption allowed)
- `as_of_date` (explicit or assumed to current date)
- `output_language` (default to user input language)
