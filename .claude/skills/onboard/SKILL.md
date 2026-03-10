---
name: onboard
description: 최초 1회 인터뷰를 통해 user-config.json을 생성하고 knowledge/ 및 library/ 디렉토리를 초기화한다.
---

# Onboard

사용 시점:
- **자동**: `user-config.json`이 없을 때 Step 0이 자동으로 호출
- **수동**: 사용자가 `/onboard`를 직접 실행해 설정을 재설정할 때

## Purpose

사용자의 practice area, jurisdiction, 출력 설정을 수집해 `user-config.json`을 생성하고,
에이전트 KB(`knowledge/`)와 변호사 자료 라이브러리(`library/`) 디렉토리를 초기화한다.

---

## Procedure

### A. 기존 설정 확인

1. `user-config.json` 존재 여부 확인 (Read 시도).
2. **존재하면**: 현재 설정의 주요 항목을 요약 출력한 후 "설정을 재구성할까요?" 확인.
   - 사용자가 거부하면 즉시 종료 (기존 설정 유지).
   - 사용자가 동의하면 B단계로 진행.
3. **없으면**: 바로 B단계로.

### B. 시작 방식 선택

사용자에게 두 가지 옵션을 제시한다:

```
설정 방식을 선택해주세요:

[1] 템플릿 선택  — 6개 starter 중 하나를 골라 즉시 생성
[2] 직접 설정    — 인터뷰 (7문항)를 통해 맞춤 설정 생성
```

**템플릿 목록 (옵션 1 선택 시 제시):**

| # | 템플릿 | 대상 |
|---|--------|------|
| 1 | 한국 법령 일반 | 국내 법령·규정 리서치 전반 |
| 2 | 한국 스타트업·VC·IT | 창업, VC 투자, IT 법무 |
| 3 | 한국 IP 소송 | 특허, 상표, 저작권 분쟁 |
| 4 | 한국 고용·노동 | 근로기준법, 노사관계 |
| 5 | 미국 기업·M&A | 미국 델라웨어 법인, 딜 구조 |
| 6 | EU 개인정보보호 | GDPR, ePrivacy, 감독당국 |

템플릿 선택 시 → `.claude/skills/onboard/templates/{template-filename}.json` 읽어 `user-config.json` 생성 후 D단계로.

### C. 인터뷰 7문항 (옵션 2 선택 시)

아래 7문항을 순서대로 물어본다. 응답 누락 시 기본값을 적용하고 명시한다.

1. **이름 / 직함 / 사무소명**
   - 예: "홍길동 / Senior Associate / 법무법인 OO"
   - 기본값: "Attorney / Associate / [사무소 미지정]"

2. **주요 업무 분야**
   - 선택지: `corporate` / `IP` / `employment` / `regulatory` / `criminal` / `tax` / `other`
   - 기본값: `corporate`

3. **주요 산업 섹터** (복수 가능)
   - 예: fintech, pharma, gaming, real estate, SaaS, healthcare, energy ...
   - 기본값: 미지정 (skip 가능)

4. **Primary jurisdiction(s)**
   - 예: KR, US, EU, SG, JP, CN, UK ...
   - 기본값: KR

5. **기본 출력 언어 & 파일 포맷**
   - 언어: `ko` / `en` / `ko+en`
   - 포맷: `docx` / `pdf` / `md`
   - 기본값: ko, docx

6. **리서치 기본 깊이**
   - `Quick` (단일 이슈, 빠른 답변) / `Full` (8단계 전체)
   - 기본값: Full

7. **특수 참조 소스** (선택, skip 가능)
   - 자주 쓰는 데이터베이스, 내부 포털 등
   - 기본값: 없음

### D. user-config.json 생성

인터뷰 응답 또는 선택한 템플릿 데이터를 바탕으로 아래 스키마로 `user-config.json`을 프로젝트 루트에 작성한다.

```json
{
  "version": "1.0",
  "created": "<오늘 날짜 ISO>",
  "persona": {
    "name": "<이름>",
    "title": "<직함>",
    "firm": "<사무소명>",
    "bar_admissions": ["<jurisdiction>"],
    "specialization": "<practice area 요약>"
  },
  "practice": {
    "primary_area": "<primary_area>",
    "sub_areas": [],
    "industry_sectors": [],
    "typical_matters": []
  },
  "jurisdictions": {
    "primary": ["<KR|US|EU|...>"],
    "secondary": []
  },
  "research_defaults": {
    "mode": "D",
    "output_format": "<docx|pdf|md>",
    "output_language": "<ko|en>",
    "quick_mode_threshold": "single-<primary_jurisdiction>-statute"
  },
  "kb": {
    "index_path": "knowledge/_index.md"
  },
  "library": {
    "index_path": "library/_index.md"
  }
}
```

### E. 디렉토리 초기화

#### `knowledge/` (에이전트 자동 관리)

```
knowledge/
  _index.md       ← 에이전트가 리서치 결과를 기록하는 인덱스
  statutes/
  cases/
  templates/
  precedents/
```

`knowledge/_index.md` 초기 내용:

```markdown
# Knowledge Base Index

에이전트가 리서치 완료 후 검증된 결과를 여기에 기록합니다.
직접 편집하지 마세요 — 에이전트가 자동으로 관리합니다.

| 파일 | 주제 | 날짜 | 관할 |
|------|------|------|------|
```

#### `library/` (변호사 직접 관리)

```
library/
  _index.md       ← 변호사가 직접 업데이트하는 자료 인덱스
  opinions/       ← 법률 의견서 (자사 + 외부 로펌)
  cases/          ← 판례 원문
  papers/         ← 논문, 아티클, 주석서
  regulations/    ← 규정집, 가이드라인, 유권해석
  misc/
```

`library/_index.md` 초기 내용:

```markdown
# Attorney Library Index

이 폴더에 보유 자료를 추가하고, 아래 표에 직접 기록해주세요.
에이전트는 리서치 시 이 인덱스를 먼저 확인하고 해당 파일을 Grade A 소스로 참조합니다.

| 파일 경로 | 제목 | 유형 | 관할 | 날짜 | 비고 |
|-----------|------|------|------|------|------|
```

### F. 완료 메시지 출력

설정 요약을 출력한 후 아래 안내를 포함한다:

```
✓ 설정 완료: {name} @ {firm}
✓ 주요 관할: {primary jurisdictions}
✓ knowledge/ 및 library/ 디렉토리 생성 완료

💡 library/ 폴더에 보유 자료(의견서, 판례, 논문 등)를 추가하면
   리서치 시 에이전트가 자동으로 Grade A 소스로 참조합니다.
   추가 후 library/_index.md 표를 직접 업데이트해주세요.

이제 리서치 질문을 입력하면 바로 시작됩니다.
```

---

## Failure Handling

- 응답 누락 항목: 기본값 적용 후 "[기본값 적용: ...]"으로 명시
- 파일 쓰기 실패: 경로 및 권한 확인 후 재시도 1회; 실패 지속 시 사용자에게 수동 생성 안내
- 디렉토리 이미 존재: 덮어쓰지 않고 `_index.md`만 없으면 생성

---

## Outputs

- `user-config.json` (프로젝트 루트, gitignored)
- `knowledge/` 디렉토리 + `_index.md`
- `library/` 디렉토리 + `_index.md` + 하위 폴더 (비어있는 상태)

---

## Quality Check

- [ ] `user-config.json` 생성 확인
- [ ] `persona.name`, `jurisdictions.primary`, `research_defaults.output_language` 모두 채워짐
- [ ] `knowledge/_index.md` 생성 확인
- [ ] `library/_index.md` 생성 확인
- [ ] 완료 메시지 출력됨
