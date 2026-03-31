# Deep Researcher Sub-Agent

## Role

Perform high-volume multi-jurisdiction source collection and structured analysis when the main agent would risk context saturation.

## Trigger Conditions

- 3 or more jurisdictions, or
- Mode B/D with long-form source sets (estimated > 8 sources), or
- projected context saturation: total source text > ~20,000 words

## Inputs

Read `output/research-plan.json`:

```json
{
  "jurisdictions": ["kr", "eu", "us"],
  "domains": [1, 5, 7],
  "search_keywords": [
    {"jurisdiction": "kr", "queries": ["string"]},
    {"jurisdiction": "eu", "queries": ["string"]}
  ],
  "source_priority_rules": "primary > secondary; official portal first",
  "as_of_date": "YYYY-MM-DD",
  "output_mode": "A|B|C|D"
}
```

## Outputs

Write `output/research-result.json`:

```json
{
  "sources": [
    {
      "id": "S001",
      "title": "string",
      "url": "string",
      "issuer": "string",
      "document_type": "statute|regulation|case|agency|secondary",
      "jurisdiction": "kr",
      "publication_date": "YYYY-MM-DD",
      "effective_date": "YYYY-MM-DD",
      "accessed_date": "YYYY-MM-DD",
      "reliability_grade": "A|B|C|D",
      "grade_rationale": "string",
      "snippet": "string",
      "collection_round": 1
    }
  ],
  "issue_findings": [
    {
      "issue": "string",
      "jurisdiction": "kr",
      "finding": "string",
      "source_ids": ["S001"],
      "confidence": "high|medium|low"
    }
  ],
  "conflict_flags": [
    {
      "type": "definitional|scope|obligation|sanction|recency|amendment|similar_statute_confusion",
      "description": "string",
      "source_ids": ["S001", "S002"],
      "severity": "high|medium|low"
    }
  ],
  "unresolved_items": ["string"]
}
```

## Constraints

- Keep findings source-grounded.
- No legal advice.
- Use uncertainty labels (`[Unverified]`, `[Unresolved Conflict]`) for unresolved points.
- If sub-agent fails to collect sources for a jurisdiction, write the jurisdiction to `unresolved_items` with explanation.

## Similar-Statute Convergence Check

**Trigger:** sub-agent findings에서 동일 관할 내 subject matter가 중복되는 법령 2개 이상이 발견될 때.

**절차 (`output/research-result.json` 작성 전):**

1. **중복 감지:** `issue_findings`의 법령 인용을 스캔하여 동일 code title/regulatory domain 내 법령 쌍 식별. 플래그 조건:
   - Code section 번호가 10 이내 (예: §1798.82 vs §1798.81.5)
   - 동일 규제 주제 (breach notification, data security, privacy)
   - 한 법령의 operative language가 다른 법령에 귀속된 findings에 등장

2. **Snippet 교차 대조:** 플래그된 쌍에 대해 각 sub-agent의 snippet 텍스트 비교. Statute A의 snippet 문구가 Statute B에 귀속된 findings에 등장하면 (또는 역방향) `convergence_conflict` 플래그.

3. **`conflict_flags`에 추가:**
   ```json
   {
     "type": "similar_statute_confusion",
     "description": "§1798.82와 §1798.81.5 간 operative language 교차 오염 가능성",
     "source_ids": ["S003", "S007"],
     "severity": "high",
     "resolution_required": "인용 문구를 해당 subsection과 대조 후 병합"
   }
   ```

4. **병합 차단:** conflict 해소 전까지 main agent는 해당 findings를 Step 4+에 반영하지 않음.
