# Reliability Scoring Rubric

## Grade A (Highest)

Official primary source:
- statute/regulation official text
- court decision original text
- regulator original publication

## Grade B (High)

Credible secondary source:
- peer-reviewed publication
- research institute report
- curated case-law DB with links to originals

## Grade C (Medium)

Practitioner or industry material:
- law-firm memo
- policy commentary with potential bias
- self-regulatory body content (default C + tag)

## Grade D (Low)

Low-trust summaries:
- unattributed blog posts
- SEO pages
- wiki-style pages without reliable traceability

Never use D as sole support for conclusions.

## Source Authority Classification

Independent of grade, classify every source as `primary`, `secondary`, or `mixed`:

| Authority | Criteria | Can support key conclusions alone? |
|---|---|---|
| `primary` | Original text issued by the authoritative body (legislature, court, regulator) | Yes (if Grade A or B) |
| `secondary` | Interpretation, commentary, or analysis by third parties | No — must be paired with a primary source |
| `mixed` | Contains both original text and editorial content | Only the primary-text portions may serve as primary authority |

### Source Laundering Indicators

Flag `laundering_risk: true` when a secondary source:
- Paraphrases a statute/regulation without citing the specific article or section number
- Claims "the law requires X" without linking to the actual provision
- Summarizes a court decision without providing the case citation or specific holding
- Presents regulatory requirements as general knowledge without attribution

When flagged, the source **cannot** be cited as primary authority. Either fetch the underlying primary source or cite the secondary source transparently.

## Korean Source Refinements

When grading Korean sources, apply these jurisdiction-specific rules in addition to the general rubric above:

- law.go.kr 현행법 전문 / 연혁 → Grade A
- 대법원·헌재 판례 원문 → Grade A
- 법제처 법령 해석례 → Grade A (공식 유권해석)
- 규제기관 유권해석·심결 → Grade A
- 규제기관 가이드라인·보도자료 → Grade B
- 국회 입법자료 (의안원문, 심사보고서) → Grade B
- 한국법제연구원 보고서 → Grade B
- 비공식 영문 번역본 → Grade B (max), 반드시 한국어 원문 병기
- 대형 로펌 뉴스레터 → Grade C
- 법률 블로그·커뮤니티 → Grade D

See `references/korean-law-reference.md` § 6 for full details.

### Korean Source Authority

- law.go.kr 법령 전문, 대법원/헌재 판례 원문, 법제처 유권해석 → `primary`
- 규제기관 가이드라인, 보도자료, 국회 입법자료 → `primary` (Grade B)
- 한국법제연구원 보고서 → `secondary` (Grade B)
- 로펌 뉴스레터 → `secondary` (Grade C) — 원문 법령 핀포인트 없이 패러프레이즈 시 `laundering_risk: true`
- 법률 블로그/커뮤니티 → `secondary` (Grade D)
