# Korean Law Reference (한국법 조사 참조 가이드)

이 문서는 한국법이 포함된 조사에서 Steps 2–6에 걸쳐 참조하는 한국법 전용 가이드입니다.

---

## 1. 법원(法源) 체계 — Legal Source Hierarchy

한국법의 효력 서열. 상위 규범에 위반되는 하위 규범은 무효입니다.

| 단계 | 유형 | 제정 주체 | 성격 | 예시 |
|------|------|----------|------|------|
| 1 | **헌법** (Constitution) | 국민투표 | 최상위 규범 | 대한민국 헌법 |
| 2 | **법률** (Act/Statute) | 국회 (National Assembly) | 일반적·추상적 규범 | 개인정보 보호법, 상법, 민법 |
| 3 | **대통령령 (시행령)** (Presidential Decree / Enforcement Decree) | 대통령 | 법률의 위임 사항 구체화 | 개인정보 보호법 시행령 |
| 4 | **총리령·부령 (시행규칙)** (Ministerial Regulation / Enforcement Rules) | 국무총리 또는 소관 부처 장관 | 시행령의 세부 절차·양식 규정 | 개인정보 보호법 시행규칙 |
| 5 | **행정규칙** (Administrative Rules) | 행정기관 | 내부 지침, 대외적 구속력 제한적 | 고시(Notice), 훈령(Directive), 예규(Regulation), 지침(Guideline) |

### 연구 시 체크포인트

- **위임 여부 확인**: 법률 조항이 "대통령령으로 정한다", "~에서 정하는 바에 따라"로 끝나면, 해당 시행령·시행규칙까지 반드시 확인.
- **하위법령 미제정**: 법률에 위임 규정이 있으나 시행령이 아직 제정되지 않은 경우, 해당 조항은 사실상 시행 불가 → `[Unverified — 하위법령 미제정]` 태그 사용.
- **고시·훈령의 대외적 효력**: 원칙적으로 행정기관 내부 규범이나, 법률이 명시적으로 "고시로 정한다"고 위임한 경우(위임고시)에는 대외적 구속력 인정. 구별 필요.
- **자기완결 조항 vs 위임 조항**: "~한다"로 종결되면 자기완결적, "~대통령령으로 정한다"면 위임 조항.

---

## 2. 부칙(附則) 체크리스트 — Supplementary Provisions

법률의 부칙(supplementary/transitional provisions)에 핵심 실무 정보가 집중됩니다.

| 항목 | 확인 사항 | 왜 중요한가 |
|------|----------|------------|
| **시행일 (발효일)** | 부칙 제1조 — "이 법은 공포 후 X개월이 경과한 날부터 시행한다" | 법률이 공포되었더라도 시행 전이면 현행법 아님 |
| **경과규정** | 부칙 제2조~ — "이 법 시행 전에 ~한 경우에는 종전의 규정에 따른다" | 기존 계약·처분·인허가에 구법 적용 여부 결정 |
| **적용례** | "이 법 시행 후 최초로 ~하는 경우부터 적용한다" | 소급적용 여부 판단 |
| **한시법 (시한법)** | 부칙에 유효기간 명시 — "이 법은 ~까지 효력을 가진다" | 자동 실효 여부 확인 |
| **다른 법률의 개정** | 부칙으로 타 법률 조항을 함께 개정 | 해당 법률만 보면 놓치는 변경 사항 |

### 연구 규칙

- 법률 본문만 읽지 말 것 — **반드시 부칙까지 확인**.
- law.go.kr에서 "연혁" 탭을 통해 개정 이력과 부칙 전문 확인 가능.
- 시행일이 미래인 경우: 본문에 `(시행 예정: YYYY-MM-DD)` 명기.

---

## 3. 판례 검색 가이드 — Case Law Navigation

### 3.1 법원 체계

| 법원 | 역할 | 판례 검색처 |
|------|------|-----------|
| **대법원** (Supreme Court) | 최종심, 법률해석 통일 | supremecourt.go.kr → 종합법률정보 |
| **헌법재판소** (Constitutional Court) | 위헌법률심판, 헌법소원 | ccourt.go.kr |
| **고등법원** (High Court) | 항소심 | 종합법률정보 (선별적 게재) |
| **지방법원** (District Court) | 제1심 | 종합법률정보 (선별적 게재) |
| **특허법원** | 특허·상표·디자인 항소심 | 종합법률정보 |
| **행정법원** | 행정소송 제1심 | 종합법률정보 |
| **가정법원** | 가사·소년 사건 | 종합법률정보 (선별적 게재) |

### 3.2 판례번호 구조

```
대법원 2020다12345 판결
 ↑      ↑    ↑     ↑
법원명  연도  사건종류+번호  재판유형
```

**사건종류 코드:**
- `다` — 민사 상고 (civil cassation)
- `두` — 민사 항고 (civil appeal of ruling)
- `도` — 형사 상고 (criminal cassation)
- `누` — 행정 상고 (administrative cassation)
- `허` — 특허 상고 (patent cassation)
- `헌가` — 위헌법률심판 (constitutional review of statute)
- `헌마` — 헌법소원 (constitutional complaint)
- `헌바` — 위헌심판제청 (constitutional referral)

### 3.3 판례 선례 가치

| 구분 | 구속력 | 설명 |
|------|--------|------|
| **대법원 전원합의체 판결** | 사실상 구속력 (de facto binding) | 판례 변경 시 전원합의체 필요 |
| **대법원 소부 판결** | 높은 참고적 효력 | 하급심 통상 따름 |
| **헌법재판소 위헌결정** | 법적 구속력 (legally binding) | 해당 법률 조항 효력 상실 |
| **헌법재판소 헌법불합치결정** | 입법개선 의무 | 개정 시한까지 잠정 적용 |
| **하급심 판결** | 참고적 효력 | 확정 전 판결은 인용 시 주의 |

### 3.4 검색 전략

1. **law.go.kr 법령 내 "판례" 탭** — 해당 조항 관련 판례 직접 링크
2. **supremecourt.go.kr "종합법률정보"** — 판례번호·키워드 검색
3. **ccourt.go.kr** — 헌법재판소 결정문 전문 검색
4. 판례 원문에서 인용된 선행 판례를 역추적하여 판례 계보 파악

---

## 4. 주요 규제기관 매핑 — Regulator Authority Map

| 규제기관 | 영문명 | 소관 주요 법률 | 포털 |
|---------|--------|-------------|------|
| **개인정보보호위원회** | PIPC | 개인정보 보호법, 신용정보법 | pipc.go.kr |
| **공정거래위원회** | KFTC | 공정거래법, 하도급법, 표시광고법 | ftc.go.kr |
| **금융위원회 / 금융감독원** | FSC / FSS | 자본시장법, 은행법, 보험업법 | fsc.go.kr, fss.or.kr |
| **방송통신위원회** | KCC | 전기통신사업법, 방송법 | kcc.go.kr |
| **과학기술정보통신부** | MSIT | 정보통신망법, 클라우드컴퓨팅법 | msit.go.kr |
| **고용노동부** | MOEL | 근로기준법, 산업안전보건법 | moel.go.kr |
| **법무부** | MOJ | 민법, 형법, 국적법 | moj.go.kr |
| **법제처** | MOLEG | 법령 해석, 입법예고 관리 | moleg.go.kr |
| **국토교통부** | MOLIT | 건축법, 주택법, 국토계획법 | molit.go.kr |
| **환경부** | ME | 환경영향평가법, 대기환경보전법 | me.go.kr |
| **식품의약품안전처** | MFDS | 식품위생법, 약사법 | mfds.go.kr |
| **특허청** | KIPO | 특허법, 상표법, 디자인보호법 | kipo.go.kr |
| **관세청** | KCS | 관세법, 대외무역법 | customs.go.kr |
| **국세청** | NTS | 소득세법, 법인세법, 부가가치세법 | nts.go.kr |

### 연구 시 활용법

- 소관 규제기관의 **유권해석** (행정해석)은 Grade A 취급 — 법적 구속력은 없으나 실무상 규제기관이 따르는 해석.
- 규제기관 **보도자료·가이드라인**은 Grade B — 공식이나 법적 구속력 제한적.
- 규제기관이 불분명한 경우, law.go.kr에서 해당 법률의 "소관부처" 항목 확인.

---

## 5. 법제처 자원 활용 — MOLEG Resources

| 자원 | URL/경로 | 용도 |
|------|----------|------|
| **법령 해석례** | moleg.go.kr → 법령해석 | 공식 유권해석. 행정기관 간 법령 해석 분쟁 조정 |
| **입법예고** | moleg.go.kr → 입법예고 | 제·개정 예정 법령 사전 공개. 시행 전 변경사항 추적 |
| **국회 의안정보** | likms.assembly.go.kr | 국회 계류 중 법안 (발의·심사·의결 상태) |
| **법제처 법령정비** | moleg.go.kr | 장기 미정비 법령, 정비 예정 법령 목록 |

### 연구 규칙

- 개정법 분석 시: 현행법 + 입법예고 중인 개정안 병행 확인.
- "입법동향" 관련 질의: 국회 의안정보시스템에서 관련 법안 검색.
- 법제처 해석례는 `[A#]` (행정문서) 코드로 인용.

---

## 6. 한국법 소스 등급 세분화 — Korean Source Grading

일반 scoring-rubric에 추가하여 한국 소스에 적용하는 세분화 기준:

| 소스 유형 | 등급 | 비고 |
|----------|------|------|
| law.go.kr 현행 법령 전문 | **A** | 최우선 참조 |
| law.go.kr 연혁·개정이력 | **A** | 부칙·경과규정 포함 |
| 대법원 판례 원문 (supremecourt.go.kr) | **A** | |
| 헌법재판소 결정문 (ccourt.go.kr) | **A** | |
| 법제처 법령 해석례 | **A** | 공식 유권해석 |
| 규제기관 유권해석·심결 (공정위 의결, 금융위 질의회신 등) | **A** | |
| 규제기관 가이드라인·보도자료 | **B** | 공식이나 구속력 제한 |
| 국회 입법자료 (의안원문, 심사보고서) | **B** | 입법 취지 해석에 유용, 법적 구속력 없음 |
| 한국법제연구원 (KLRI) 연구보고서 | **B** | 정부출연 연구기관 |
| 비공식 영문 번역본 | **B (max)** | 반드시 한국어 원문 병기 |
| 법률신문·변호사신문 기사 | **B–C** | 뉴스 보도, 분석 기사 구분 필요 |
| 대형 로펌 뉴스레터 (김앤장, 광장 등) | **C** | 실무적이나 편향 가능성 |
| 법률 블로그·커뮤니티 | **D** | 단독 근거 불가 |

---

## 7. 한국법 충돌 유형 — Korean-Specific Conflict Rules

일반 conflict-detector 규칙에 추가:

### 7.1 법률 vs 시행령 충돌 (위임한계 초과)

- **문제**: 시행령이 모법(법률)의 위임 범위를 초과하여 규정.
- **판단 기준**: 대법원 판례 — "위임의 범위를 벗어난 것인지는 당해 법률 규정의 입법 취지와 체계적 관련성 등을 고려하여 판단" (대법원 2008두167 등).
- **처리**: `[Unresolved Conflict — 위임한계 초과 의심]` 태그 + 시행령 해당 조항과 모법 위임 조항 병기.

### 7.2 법률 vs 지방조례 충돌

- **원칙**: 지방자치법 제28조 — 조례는 법령의 범위 안에서 제정.
- **예외**: 주민 권리 제한·의무 부과 사항은 법률의 위임이 있어야 조례로 규정 가능.
- **처리**: 조례가 법률보다 엄격한 경우, 적법한 위임 범위 내인지 확인.

### 7.3 구법 vs 신법 충돌 (경과규정)

- **원칙**: 신법 우선 (lex posterior). 다만 부칙 경과규정에 따라 구법 적용 존속 가능.
- **처리**: 부칙 경과규정을 반드시 확인. 경과규정 유무에 따라 결론이 반대가 될 수 있음.
- **태그**: `[Unresolved Conflict — 구법/신법 경과규정 확인 필요]`

### 7.4 일반법 vs 특별법 충돌

- **원칙**: 특별법 우선 (lex specialis). 예: 민법(일반법) vs 상법(상사 특별법), 개인정보 보호법(일반법) vs 신용정보법(금융 특별법).
- **처리**: 특별법 적용 범위를 먼저 확정하고, 범위 밖은 일반법 적용.

---

## 8. 핵심 용어 시드 — Korean Legal Terminology Seeds

아래 용어는 한국법 조사 시 빈번하게 등장하며, 오역 위험이 높은 핵심 용어입니다.

| 한국어 | 영문 표준 번역 | 오역 위험 | 비고 |
|--------|-------------|----------|------|
| 법률 | Act / Statute | "Law"로 번역 시 법원(法源) 전체와 혼동 | 국회 제정 법률만 지칭 |
| 시행령 | Enforcement Decree / Presidential Decree | "Regulation"으로 번역 시 시행규칙과 혼동 | 대통령 제정 |
| 시행규칙 | Enforcement Rules / Ministerial Regulation | | 장관 제정 |
| 고시 | Public Notice / Official Notice | "Notification"과 혼동 | 위임고시는 구속력 있음 |
| 판결 | Judgment / Decision | "Verdict"는 배심 평결에 한정 (한국 해당 없음) | |
| 결정 | Ruling / Order | 판결과 구별 — 비송사건, 부수적 신청 등 | |
| 의뢰인 | Client (legal advice context) | "당사자"(party to litigation)와 혼동 주의 | |
| 당사자 | Party (to a case/transaction) | | 소송·계약의 당사자 |
| 법률자문 | Legal consultation/advice | "경영자문"(business consulting)과 혼동 시 비밀유지특권 판단 영향 | |
| 소송 | Litigation / Lawsuit | "수사"(investigation), "조사"(inquiry)와 구별 | 민사·행정 |
| 수사 | Criminal investigation | | 검찰·경찰 |
| 행정조사 | Administrative inquiry/inspection | | 규제기관 |
| 과태료 | Administrative fine (non-criminal) | "벌금"(criminal fine)과 혼동 주의 | 전과 기록 없음 |
| 벌금 | Criminal fine | | 전과 기록 발생 |
| 과징금 | Surcharge / Penalty surcharge | "과태료"와 구별 — 부당이득 환수 성격 | 공정거래법, 개인정보보호법 등 |
| 법인 | Juridical person / Corporation | "개인"(natural person)과 구별 | |
| 가명정보 | Pseudonymized data | GDPR "pseudonymisation"과 유사하나 처리 요건 상이 | 개인정보 보호법 제28조의2 |
| 개인정보처리자 | Personal information controller | GDPR "controller"에 대응 | |
| 정보주체 | Data subject | GDPR "data subject"에 대응 | |

---

## 9. Open Law API (열린법령 API) 활용 가이드

### 9.1 개요

**Step 3 한국법 소스 수집의 1순위 도구.** law.go.kr DRF API를 통해 구조화된 법령·판례·해석례 데이터를 온디맨드로 조회합니다.

- **CLI 래퍼:** `scripts/open_law_api.py`
- **인증:** `OPEN_LAW_OC` 환경변수 (`.env` 파일에 설정)
- **외부 의존성 없음** — Python 표준 라이브러리만 사용

### 9.2 핵심 엔드포인트

| 서브커맨드 | API target | Base URL | 용도 |
|-----------|-----------|----------|------|
| `search-law` | `law` | `lawSearch.do` | 법령 키워드 검색 → ID/MST 확보 |
| `get-law` | `law` | `lawService.do` | 법령 전문 조회 (조문·항·호·목·부칙) |
| `get-article` | `lawjosub` | `lawService.do` | 특정 조문만 정밀 조회 |
| `search-cases` | `prec` | `lawSearch.do` | 판례 키워드 검색 |
| `get-case` | `prec` | `lawService.do` | 판례 전문 (판시사항·요지·참조조문) |
| `search-interpretations` | `expc` | `lawSearch.do` | 법령해석례 검색 |

### 9.3 표준 연구 순서 (API 우선)

1. **`search-law "법률명"`** → 법령 ID 확보
2. **`get-law --id {ID}`** → 전문 조회 (조문 구조화 + 부칙 포함)
3. **`get-article --id {ID} --article {N}`** → 특정 조문만 조회 (토큰 절약)
4. **`search-law "시행령명"`** → 하위법령(시행령·시행규칙) 검색 및 조회
5. **`search-cases "키워드"`** → 관련 판례 검색
6. **`get-case --id {ID}`** → 판례 전문 조회
7. **`search-interpretations "키워드"`** → 법제처 해석례 확인
8. 영문 번역 필요 시 elaw.klri.re.kr 참조 (Grade B max)

### 9.4 사용 예시

```bash
# 법령 검색
python3 scripts/open_law_api.py search-law "개인정보 보호법"

# 법령 전문 조회 (ID로)
python3 scripts/open_law_api.py get-law --id 001823

# 특정 조문만 조회 (제17조)
python3 scripts/open_law_api.py get-article --id 001823 --article 17

# 판례 검색 (전문 검색 모드)
python3 scripts/open_law_api.py search-cases "개인정보 유출" --fulltext

# 판례 전문 조회
python3 scripts/open_law_api.py get-case --id 228541

# 법령해석례 검색
python3 scripts/open_law_api.py search-interpretations "자동차"

# 페이지네이션
python3 scripts/open_law_api.py search-law "보호법" --display 50 --page 2
```

### 9.5 API Fallback 규칙

1. Open Law API 호출 → 정상 응답 시 그대로 사용 (Grade A 소스)
2. API 실패(HTTP 에러, 타임아웃, 빈 결과) → Tavily/Brave 검색으로 fallback
3. 검색도 실패 → `references/legal-source-urls.md`의 큐레이팅된 URL로 직접 fetch

### 9.6 기존 웹 검색과의 차이

| 항목 | 기존 (WebFetch) | Open Law API |
|------|----------------|-------------|
| 데이터 형태 | HTML 파싱 필요 | 구조화된 XML (조문별 분리) |
| 정확도 | 페이지 레이아웃 의존 | 필드 단위 정확 |
| 부칙 접근 | 별도 탭 확인 필요 | 응답에 포함 |
| 토큰 효율 | 전체 페이지 텍스트 | 필요 조문만 조회 가능 |
| 안정성 | 웹 레이아웃 변경 시 깨짐 | 공식 API, 안정적 |

## 10. law.go.kr 웹 직접 검색 (API Fallback용)

API가 실패할 경우 아래 웹 검색 방식을 사용합니다:

### URL 패턴

- 법령 본문: `https://www.law.go.kr/법령/개인정보보호법`
- 영문 법령 (비공식): `https://elaw.klri.re.kr/` (한국법제연구원 영문법령정보)

### 웹 검색 방법

1. **법령명 검색**: 정확한 법률명 입력 → 현행 법령 전문 확인
2. **조문별 검색**: 법령명 + 조문번호 → 해당 조항만 확인
3. **연혁 탭**: 개정 이력, 각 버전별 부칙 확인
4. **하위법령 탭**: 해당 법률의 시행령·시행규칙·관련 고시 일괄 확인
5. **판례 탭**: 해당 법률 조항에 대한 관련 판례 링크
6. **법령체계도**: 상위법-하위법 관계도 시각화
