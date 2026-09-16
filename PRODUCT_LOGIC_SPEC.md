# PRODUCT_LOGIC_SPEC — 규정다름 (강정민)

Status: READY  
Upstream decision: admrul-diff 스크립트 (prelim/admrul-diff/scripts/admrul_diff.py)  
Target runtime: web (Vercel 서버리스 + 정적 HTML)

## 1. Product truth

규정다름은 행정규칙/지침/훈령/예규/요령 등 조문 단위로 바뀌는 문서의 **구판과 신판 텍스트**를 입력받아,  
① 조항 단위 diff(added/modified/deleted) 대조표,  
② 부칙 시행일 파싱 → 오늘(KST) 기준 D-day/시행상태를 자동으로 출력하는 단일 페이지 서비스다.

핵심 약속:
- **계산은 스크립트가 수행**한다. LLM은 임의 판정·추정·계산을 하지 않는다.
- 입력은 **텍스트 붙여넣기** (파일 업로드 아님).
- 출력은 **두 개의 표**: 신·구 조문 대조표 / 시행 D-day.

## 2. Primary loop and invariants

```
입력(구판 텍스트 + 신판 텍스트) → POST /api/admrul-diff → 
스크립트 diff + 시행일 파싱 → JSON → 표 렌더링
```

이벤트:
- `runDiff()`: 구판/신판 텍스트가 모두 비어있지 않으면 POST 요청.
- `loadSample()`: 구판/신판 샘플 텍스트 채움.
- `clearAll()`: 입력·결과 초기화.

상태:
- **idle**: 입력 대기.
- **loading**: 요청 중, 결과 영역에 "대조 중…" 표시.
- **result**: 대조표 + D-day 표 표시.
- **error**: 에러 메시지 표시 (빨간 박스).

불변식:
- 구판/신판 중 하나라도 비어있으면 실행 불가 (클라이언트 사전 검증 + 서버 검증).
- 조문 패턴(제N조)이 양쪽 모두 있어야 함.
- diff 결과는 added/modified/deleted만 사용.
- D-day 상태는 "D-n"/"오늘 시행"/"시행중"/"시행일 미검출"만 사용.

## 3. State, event, data, and effect explanation

### 데이터
- 구판 텍스트 (string, 최대 약 50KB)
- 신판 텍스트 (string, 최대 약 50KB)
- diff 결과 (JSON 배열)
- enactment 결과 (JSON 객체)

### 효과 (effects)
- `fetch('/api/admrul-diff', {method: POST, body: JSON})`
  - 성공: JSON 파싱 → renderResult()
  - 실패: 에러 박스 표시
  - 네트워크 오류: 에러 박스 표시

### 예외 처리
- 구판/신판 중 하나 빈 경우: "구판과 신판 텍스트를 모두 입력해주세요."
- 조문 패턴 없음: "행정규칙/지침 형식이 아닌 것으로 보입니다."
- 서버 에러(500 등): "요청 중 오류가 발생했습니다: [메시지]"

### 백/되돌리기
- 브라우저 뒤로가기: 별도 상태 저장 없음 (단일 페이지, 입력 히스토리 없음).
- 페이지 새로고침: 입력값 유지 안 됨 (의도적 — 세션 저장 미구현).

## 4. Motion and runtime rationale

의미 있는 모션 없음 — 정보 집약형 도구이므로 애니메이션보다 빠른 응답 우선.
로딩 표시는 텍스트("대조 중…")만 사용.

## 5. Canonical contract

이 서비스는 단일 HTML + 서버리스 API 구조이므로, 별도 JSON 계약 없이  
`service/public/index.html`과 `service/api/admrul-diff/index.py`가 정본이다.

## 6. Open decisions and handoff

- **미결정**: 파일 업로드 지원 여부 (현재 붙여넣기만). 향후 추가 가능.
- **미결정**: 다크 모드 (현재 라이트 전용, CSS 변수만 정의됨).
- **미결정**: 결과 저장/공유 기능 (현재 없음).
- **Handoff to front-build-spec**: UI/UX 상수는 index.html의 CSS가 정본. 개선 시 여기 반영.
- **Handoff to visual-production**: 실제 화면 마감은 index.html 렌더 결과가 정본.

본 명세는 admrul-diff 스크립트 로직을 그대로 웹 서비스로 감싼 구조이므로,  
별도 비즈니스 로직 추가 없이 **스크립트 → API → UI** 파이프라인이 완전성을 가진다.
