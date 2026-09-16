---
name: ordin-gap
description: |
  지자체 조례의 상위 표준규정 준용 배제 및 특례 조항 대조(gap 분석) 전용 스킬.
  복수 지자체(2~9개) 조례 텍스트 파일을 입력받아 상위규정을 자동 특정하고,
  준용 배제 조항을 탐지한 뒤 상위규정과 대조하여 found/not_found Gap 분석을
  순수 표준 raw JSON으로 출력한다.
  상위규정 파일이 함께 첨부되면 그것을 사용하고, 없으면 동봉된
  'upper_sample_standard.txt'를 기본 상위규정으로 자동 fallback한다.
  입력 파일이 아예 없을 경우 동봉된 4개 기본 샘플
  (하늘시·바다군·들녘시·표준규정)을 자동 로드하여 데모 모드로 실행한다.

  자연어 트리거 예시:
  - "이번 조례들 상위규정이 뭔지 찾고 준용 배제 Gap 분석해줘"
  - "ordin-gap 샘플로 한번 돌려봐"
  - "조례 파일들 넣어서 gap 분석표 만들어줘"
  - "demoss 모드 실행해"
---

# ordin-gap 스킬

## 개요

`ordin-gap`은 여러 지자체 조례 텍스트를 받아 다음을 수행한다.

- **상위규정 자동 특정**(3단계 우선순위: ① 준용 조문 제목 인용 ② 준용 본문 내 인용 빈도 ③ 전체 언급 빈도)
- **준용 배제 조항 탐지** 및 상위규정 대조 **Gap 분석**(found / not_found)
- **4종 예외 상황**에 대한 명확한 에러 JSON + 비정상 종료 코드

`scripts/ordin_gap.py`의 실행 결과는 **순수 표준 raw JSON**이며, 모델은 이 JSON을
받아 그대로 사용한다. **모델이 조문 내용을 눈으로 읽고 직접 판정·요약하지 않는다.**

> 이 스킬은 **상위 표준규정 준용 배제·특례 조항 대조(gap 분석) 전용**이다.
> 일반 조문 본문 compare(동일/상이/독자 3상태 비교) 기능은 포함하지 않는다.

---

## 사용 방법

### 기본 실행 (데모 모드)

조례 파일을 지정하지 않으면 동봉된 4개 기본 샘플을 자동 로드한다.

```bash
python .pi/skills/ordin-gap/scripts/ordin_gap.py
```

### 일반 실행 (조례 2개 이상 9개 이하)

```bash
python .pi/skills/ordin-gap/scripts/ordin_gap.py ordinances/a.txt ordinances/b.txt ... [--upper upper.txt] [--names "지자체1" "지자체2" ...]
```

- `--upper`: 상위규정 파일 경로. 미지정 시 `upper_sample_standard.txt` 자동 fallback.
- `--names`: 각 조례 파일에 대응할 지자체명. 조례 파일 개수와 일치해야 한다.
  지정하지 않으면 파일명(확장자 제거)을 지자체명으로 쓴다.

### 동봉 샘플 파일 위치

```
ordin_sample_haneul.txt   # 하늘시 공무원 여비 조례
ordin_sample_bada.txt     # 바다군 공무원 여비 조례
ordin_sample_deulnyeok.txt  # 들녘시 공무원 여비 조례
upper_sample_standard.txt  # 공직자 출장여비 표준규정 (기본 상위규정)
```

---

## 강행 규칙 (모델 필독)

1. **반드시 `scripts/ordin_gap.py`를 실행하여 그 JSON 결과만 사용**한다.
   모델이 조문 내용을 눈으로 읽고 직접 판정·요약하지 않는다.
2. JSON의 `error: true`가 나오면 그대로 사용자에게 에러 내용과 종류(`kind`)를 알린다.
   정상 출력을 에러로 둔갑시키거나 에러를 정상으로 간주하지 않는다.
3. 표 렌더링 시 **셀 안에서 여러 줄 본문을 표기할 때 `<br>` 태그를 절대 쓰지 않는다.**
   슬래시(` / `)나 공백, 쉼표로 연결한다.
4. **사용자가 대화창에 조례 파일(및 상위규정 파일)을 첨부했을 때는,
   반드시 첨부된 파일 경로들을 스크립트 인자로 전달하여 실행한다.**

   ```bash
   # 조례 2개 + 상위규정 1개 첨부 시
   python .pi/skills/ordin-gap/scripts/ordin_gap.py <첨부조례1> <첨부조례2> --upper <첨부상위규정>

   # 조례만 N개 첨부 시 (상위규정 미첨부 → 기본 fallback)
   python .pi/skills/ordin-gap/scripts/ordin_gap.py <첨부조례1> <첨부조례2> ...
   ```

   - 인자가 없을 때만 `assets/` 기본 샘플(데모 모드)로 실행한다.
   - `--upper`를 생략하면 상위규정 파일 미첨부로 간주하며,
     스크립트는 `upper_sample_standard.txt`를 자동 fallback한다.
   - 조례 파일은 **반드시 2개 이상 9개 이하**여야 한다.
     1개이거나 9개 초과이면 스크립트가 `error: true`를 출력하며 비정상 종료한다.

---

## Gap 분석 결과 표 렌더링 규칙

- 상위규정 특정 결과:
  - `name`(상위규정명), `method`(특정 방식: title/body/whole/none),
    `confidence`(high/medium/low/none), `per_ordinance`(조례별 특정 결과).
- Gap 표:
  - `source_article`(해당 지자체 조문), `excluded_article`(배제 대상),
    `status`(`found` / `not_found` / `제외 없음`).
  - `found`인 경우, 원문에 나타난 항 표기(예: 제12조제3항)가 있으면 함께 병기한다.
- 준용 배제 조항이 하나도 없으면 `gap_against_upper`가
  `[{"status": "제외 없음"}]`으로 출력된다.

---

## JSON 출력 스키마 (요약)

정상 출력 예시 구조:

```json
{
  "regulation_identified": {
    "name": "공직자 출장여비 표준규정",
    "method": "title",
    "confidence": "high",
    "per_ordinance": { "...": {...} }
  },
  "gap": {
    "exclusion_clauses": [
      { "municipality": "...", "article": "제7조", "excluded": ["제8조의2","제23조"], "raw": "..." }
    ],
    "gap_against_upper": [
      { "source_article": "...", "excluded_article": "제8조의2", "status": "found" },
      { "source_article": "...", "excluded_article": "제23조", "status": "not_found" },
      { "status": "제외 없음" }
    ]
  },
  "municipalities": ["하늘시","바다군","들녘시"],
  "ordinance_files": ["..."],
  "upper_regulation_file": "upper_sample_standard.txt",
  "upper_articles_count": 16,
  "demo_mode": false,
  "note": null
}
```

---

## 4종 예외 입력 처리 (비정상 종료 코드)

`ordin_gap.py`는 다음 4가지 상황을 감지하면 **표준 에러 JSON을 stdout으로 출력**하고
**0이 아닌 종료 코드로 종료**한다.

| 예외 종류 (`kind`) | 조건 | 예시 메시지 |
|---|---|---|
| `single_file_error` | 조례 파일이 1개뿐 | "조례 파일은 2개 이상 9개 이하를 입력해야 합니다. 현재 1개만 입력되었습니다: …" |
| `too_many_files_error` | 조례 파일이 9개 초과 | "조례 파일은 최대 9개까지 입력 가능합니다. 현재 N개가 입력되었습니다." |
| `file_not_found` | 입력 파일 경로가 존재하지 않음 | "입력 파일 경로를 찾을 수 없습니다: <경로>" |
| `no_article_detected_error` | 조문 형식이 아닌 비규격 텍스트(조문 0건) | "파일 '이름'에서 조문을 하나도 검출하지 못했습니다. 조문 형식이 아닌 비규격 텍스트가 입력된 것으로 보입니다." |

추가로 `--names` 개수 불일치 시 `name_count_mismatch_error`를 낸다.

---

## 검증 방법

1. 스크립트를 인자 없이 실행하여 데모 모드 JSON이 stdout에 출력되는지 확인.
2. 정상 출력 JSON에서 `error` 키가 없는 것과 `regulation_identified`, `gap`,
   `municipalities`가 존재하는지 확인.
3. 4개 예외 상황을 각각 재현하여 `error: true` + 해당 `kind` + 비정상 종료 코드가 나오는지 확인.

---

## 개발 노트 (내부용)

- 조문 추출은 `제N조` 패턴으로 제목을 잘라내며, 정규화 시 공백·괄호 공백을 정리한다.
- 상위규정 특정 3단계: ① 준용 조문 제목 인용 ② 준용 본문 내 인용 빈도 ③ 전체 언급 빈도.
- Gap 분석: 준용 배제 조항 없으면 `gap_against_upper`가 `[{"status": "제외 없음"}]`으로 출력된다.
- 항 포함 배제 대상(예: "제12조제3항") 처리:
  1. 먼저 조 단위('제12조')로 상위규정 존재 여부를 확인한다.
  2. 조가 존재하면 해당 조문 내에서 항 표기(③항 / 제3항 등)를 추출하여 `found`로 처리하고
     원문 항 표기를 병기한다.
  3. 조 자체가 상위규정에 없을 때만 `not_found`로 처리한다.
- 일반 조문 본문 compare(동일/상이/독자 3상태 비교) 로직은 이 스킬에 포함하지 않는다.
