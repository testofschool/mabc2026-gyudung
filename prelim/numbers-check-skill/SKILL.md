---
name: numbers-check-skill
description: >
  초안 텍스트와 원본 텍스트 두 파일을 받아, 초안에 등장한 숫자·날짜·금액·직접인용문을
  전부 추출해 원본과 대조하고 일치/근사/불일치로 판정한 결과를 JSON 으로 출력한다.
  표준 라이브러리만 사용하며 외부 패키지가 필요 없다.
  사용: python scripts/numbers_check.py 원본.txt 초안.txt
---

# numbers-check-skill

초안 속 숫자·날짜·금액·인용문을 원본과 대조하는 검증 스크립트.

## 실행 방법

```bash
python scripts/numbers_check.py 원본.txt 초안.txt
```

- 두 파일은 UTF-8 텍스트.
- 결과는 stdout 에 JSON 한 덩어리로 출력.
- 종료 코드: 0 = 정상, 1 = 처리 오류, 2 = 사용법 오류.

## 판정 기준 요약

| 판정 | 조건 |
|---|---|
| 일치 | 정규화(쉼표 제거·단위 환산·날짜 ISO 변환) 후 값이 동일. 금액 단위 환산(1,000만원=10,000,000원, 3.5억=3억5천만 등)으로 같아져도 일치. '100분의 60'과 '60%'도 비율 환산값으로 동일로 간주해 일치. |
| 근사 | 원본 값을 초안의 소수점 정밀도로 반올림 또는 절사했을 때 초안 값과 정확히 같아지는 경우만 인정. 날짜는 근사 없음. |
| 불일치 | 원본에 없음 / 값이 다름 / 인용문 내용이 다름. |

- 인용문 근사 없음: 공백 정규화 후 원본에 완전히 포함되면 일치, 아니면 불일치.
- 날짜는 연도 포함 절대 날짜만 추출(내일/다음 주 등 상대날짜 제외). 근사 없이 정확 일치만.

## 한계 안내

- 이 스킬의 판정은 스크립트(`scripts/numbers_check.py`)의 JSON 출력이 전부다. 모델을 포함한 그 누구도 손으로 판정을 다시 쓰거나, 결과를 요약하며 바꾸지 않는다.
- '17명', '236건'처럼 명·건·개 등 단위어가 붙은 숫자는 추출 대상이지만, 원본에 같은 type 의 대응 값이 없으면 `missing_in_original`로 나온다. 원본에 전혀 등장하지 않는 값은 '값이 다름(불일치)'이 아니라 '원본에 없음'으로 구분한다.
- '12억 7천만원 → 13억'처럼 반올림·어림 표현한 금액은 근사 판정 대상이 될 수 있지만, 초안의 정밀도와 원본의 구조(복합 표현 등)에 따라 근사가 잡히지 않고 불일치로 나올 수도 있다. 예: 원본 '12억 7천만원'을 초안이 '13억'으로 적으면 억 단위 반올림으로 근사가 될 수 있으나, 초안이 '12억 8천만원'처럼 적으면 근사 조건을 만족하지 못해 불일치가 될 수 있다.
- 요약의 불일치는 '값이 다름' + '원본에 없음'이 함께 집계된 뒤, 행 단위 판정에서 `missing_in_original` 과 `mismatch` 로 나뉘어 표시된다. 숫자 계열에서 원본에 같은 type 엔티티가 아예 없으면 행 판정이 `missing_in_original` 이다.
- 추출 범위 밖의 값은 결과에 아예 등장하지 않는다(제외 항목·작은 숫자·조문번호 등). 그런 값의 개수는 요약의 `excluded` / `excluded_breakdown` 으로만 공개된다.

## 판정 강행 규칙 (반드시 지킬 것)

## JSON 출력 스키마 (성공)

```json
{
  "status": "ok",
  "files": {"original": "원본.txt", "draft": "초안.txt"},
  "summary": {
    "draft_total": 42,
    "excluded": 5,
    "by_type": {
      "date": {"draft": 3, "match": 2, "approx": 0, "mismatch": 1},
      "money": {"draft": 10, "match": 7, "approx": 1, "mismatch": 2},
      "number": {"draft": 8, "match": 6, "approx": 0, "mismatch": 2},
      "percent": {"draft": 5, "match": 4, "approx": 0, "mismatch": 1},
      "quote": {"draft": 4, "match": 3, "approx": 0, "mismatch": 1}
    },
    "excluded_breakdown": {
      "article_number": 2,
      "denominator": 1,
      "small_standalone": 2
    }
  },
  "rows": [
    {
      "type": "money",
      "draft_value": "1,000만원",
      "draft_line": 4,
      "draft_raw": "1,000만원",
      "normalized": 10000000.0,
      "verdict": "match",
      "original_value": "10,000,000원",
      "original_line": 2,
      "original_raw": "10,000,000원",
      "original_normalized": 10000000.0
    }
  ]
}
```

- `type`: `date`, `money`, `number`, `percent`, `quote` 중 하나.
- `verdict`: `match` | `approx` | `mismatch` | `missing_in_original`.
- `missing_in_original`: 원본에 같은 type 의 대응 값이 아예 없는 경우. 이 경우 `original_value` 등은 `null`이다.
- `rows`는 초안 엔티티 순서대로 출력. 원본에 대응되는 값이 없으면 `original_value` 등이 `null`.
- `normalized`: money 는 원 단위(float), percent 는 비율(0~1), number 는 float, date 는 ISO 문자열, quote 는 공백 정규화 문자열.

## 제외 항목 (요약에 공개)

- `article_number`: "제N조" 형태 조문번호.
- `denominator`: "100분의 N"에서 N 앞의 100 (분모).
- `small_standalone`: 포함 기준(100 이상·소수점·천단위콤마·단위어) 미달인 한두 자리 단독 숫자.

## 포함 기준 (의미 있는 수치만 추출)

- 100 이상이거나, 소수점·천단위 콤마가 있거나, 억·만 같은 단위어나 원·%·명 같은 단위가 붙은 것.
- "제5조" 같은 조문번호, "100분의 60"의 분모 100, 한두 자리 맨숫자는 제외하고 그 개수를 결과에 공개.

## 단위 환산 규칙

- 1억 = 100,000,000원, 1만 = 10,000원.
- "3.5억" → 350,000,000원.
- "3억 5천만원" → 3×1e8 + 5000×1e4 = 350,000,000원 → "3.5억"과 일치.
- "1,000만원" = 10,000,000원 → "10,000,000원"과 일치.
- "100분의 60" → 0.6 (비율), "60%" → 0.6 → 일치.

## 근사 판정 상세

- 원본 값을 초안의 정밀도로 반올림하거나 절사했을 때 초안 값과 정확히 같아지는 경우만 근사로 인정.
- 예: 원본 "3.456억", 초안 "3.5억" → 3.456을 소수점 1자리로 반올림(3.5) 또는 절사(3.4) → 반올림 시 일치하므로 근사.
- 날짜는 근사 없이 정확 일치만.

## 인용문 판정

- 공백 정규화 후 초안 인용문이 원본 인용문에 완전히 포함되면 일치.
- 그 외(불포함, 내용 다름 등)는 불일치. 근사 없음.

## 참고

- 스크립트 위치: `scripts/numbers_check.py`.
- Python 3 표준 라이브러리만 사용 (`re`, `json`, `sys`, `os`, `math`).
- **판정은 스크립트 JSON 출력이 전부고, 절대 네가 손으로 판정을 다시 하지 마라.** 반드시 `python scripts/numbers_check.py 원본.txt 초안.txt` 를 실행해 그 결과만 표로 옮겨야 하며, 결과를 요약하거나 임의의 판정으로 바꾸면 안 된다.
