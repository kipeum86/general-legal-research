# Glossary Entry Schema

```json
{
  "term": "string",
  "original_language_term": "string",
  "standard_translation": "string",
  "synonyms": ["string"],
  "jurisdiction_code": "kr|us|eu|...",
  "jurisdiction_level": "national|federal|state|supranational",
  "definition": "string",
  "practical_meaning_for_context": "string",
  "mistranslation_risks": ["string"],
  "sources": [
    {
      "citation_code": "[P1]",
      "pinpoint": "Article 3(2)",
      "url": "https://..."
    }
  ],
  "last_verified_date": "YYYY-MM-DD",
  "version": "v1",
  "status": "confirmed|provisional"
}
```

Note: `practical_meaning_for_context` should describe the term's practical significance in the context of the current research matter (e.g., compliance implications, definitional scope in the relevant industry or transaction type).
