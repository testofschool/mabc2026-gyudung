# FRONT_BUILD_SPEC — 규정다름 (강정민)

## 1. Header contract

- **제품**: 규정다름 — 행정규칙 신·구 조문 대조 및 시행 D-day 서비스
- **팀명**: 강정민
- **배포 형태**: 단일 HTML + Vercel 서버리스 API (Python)
- **공개 URL 목표**: Vercel 배포 후 공개 URL (로그인 없이 접속 가능)

## 2. What it is

규정다름은 행정규칙/지침/훈령/예규/요령의 **구판과 신판 텍스트를 붙여넣으면**,  
조항 단위로 변경된 내용(신설/변경/삭제)을 대조표로 보여주고,  
부칙 시행일을 파싱하여 오늘 기준 D-day/시행상태를 함께 출력하는 도구다.

핵심 상호작용: **텍스트 붙여넣기 → '대조 실행' 클릭 → 표 확인**.  
추가 상호작용: 샘플 불러오기 / 지우기 / 에러 확인.

시각적 정체성:
- 깔끔하고 직관적인 행정 도구 느낌
- 색상 구분으로 added/modified/deleted 직관적 파악
- 불필요한 장식 없음 — 정보 전달에 집중

## 3. DOM order declaration

```
body
├── .container (max-width: 900px, 중앙 정렬)
│   ├── header
│   │   ├── h1 "규정다름"
│   │   └── .subtitle "행정규칙/지침의 구판과 신판을 붙여넣으면..."
│   ├── .card (구판 입력)
│   │   ├── label "구판 텍스트 (개정 전)"
│   │   ├── textarea#oldText
│   │   └── .hint
│   ├── .card (신판 입력)
│   │   ├── label "신판 텍스트 (개정 후)"
│   │   ├── textarea#newText
│   │   └── .hint
│   ├── .actions
│   │   ├── button.btn "대조 실행"
│   │   ├── button.btn.secondary "샘플 불러오기"
│   │   └── button.btn.secondary "지우기"
│   ├── #result (동적 결과 영역)
│   │   └── .card.result-card (대조표)
│   │   └── .card.result-card (D-day 표)
│   └── footer
└── script (샘플 데이터, fetch, 렌더링 로직)
```

## 4. Per-section detail

### Header
- h1: "규정다름" — 1.8rem, font-weight: 700
- subtitle: 서비스 설명 한 줄 — color: var(--muted), 0.95rem

### 입력 카드
- label: display:block, font-weight:600, margin-bottom:8px
- textarea: 
  - width:100%, min-height:200px, padding:12px
  - border:1px solid var(--border), border-radius:8px
  - font-family: monospace (SF Mono, Menlo, Consolas)
  - font-size:0.85rem, resize:vertical
  - focus 시 outline:2px solid var(--accent)
- hint: color:var(--muted), font-size:0.82rem

### 액션 버튼
- .btn (기본): background:var(--accent), color:#fff, padding:12px 28px
- .btn.secondary: background:#e5e7eb, color:var(--fg)
- hover: opacity:0.9 / active: translateY(1px)

### 결과 영역
- 대조표 표: width:100%, border-collapse:collapse
- 배지: 
  - added → 초록 (#dcfce7 / #166534)
  - modified → 노랑 (#fef9c3 / #854d0e)
  - deleted → 빨강 (#fee2e2 / #991b1b)
- 에러 박스: background:#fee2e2, border:1px solid #fecaca
- 로딩: italic, color:var(--muted)

## 5. Selected interaction mechanics

- **대조 실행 흐름**:
  1. 구판/신판 모두 비어있는지 검사 → 비어있으면 에러
  2. resultEl.innerHTML = '<p class="loading">대조 중…</p>'
  3. POST /api/admrul-diff (JSON: {old_text, new_text})
  4. response.json() → error면 에러 박스, 정상이면 renderResult()
  5. renderResult(): diff 표 + D-day 표 생성

- **샘플 불러오기**: textarea에 샘플 텍스트 채움 (admrul_sample_old/new 기반)

- **지우기**: 두 textarea와 result 초기화

## 6. Loader/reveal

별도 로딩 스크린 없음. 결과 영역에 "대조 중…" 텍스트가 로딩 표시 역할.

## 7. Fixed parameters

```
--fg: var(--foreground, #1a1a1a)
--muted: var(--muted-foreground, #666)
--accent: var(--accent, #2563eb)
--border: var(--border, #d4d4d4)
--card: var(--card, #fff)
body background: #f8f9fa
container max-width: 900px
card padding: 24px
card border-radius: 12px
card margin-bottom: 20px
textarea min-height: 200px
button padding: 12px 28px
badge-font-size: 0.75rem
badge-padding: 2px 8px
table font-size: 0.88rem
th/td padding: 10px 12px
```

색상 팔레트:
- 배경: #f8f9fa (카드 외부)
- 카드: #fff (또는 var(--card))
- 메인 액션: #2563eb (파랑)
- added: #dcfce7 / #166534
- modified: #fef9c3 / #854d0e  
- deleted: #fee2e2 / #991b1b
- 에러: #fee2e2 / #991b1b / #fecaca

글꼴:
- 본문: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- textarea: "SF Mono", "Menlo", "Consolas", monospace

## 8. Assets

- 이미지/아이콘 없음 — 모두 CSS/텍스트로 구성
- 샘플 텍스트: index.html 내부에 템플릿 리터럴로 내장

---

## 기존 코드 대비 개선 포인트 (proposed — production-level)

1. **반응형**: 기존 코드는 데스크톱 중심. 모바일에서 textarea 높이, 버튼 배치 대응 필요.
2. **접근성**: label-for 연결은 되어 있으나, 포커스 표시, 대비비, aria-live 값 추가 검토.
3. **에러 처리**: 기존 코드 있음. 프록시/API 오류 시 메시지 개선 여지.
4. **로딩 피드백**: 텍스트만 있음. 비동기 요청 중 버튼 비활성화 추가 가능.
5. **empty 상태**: diff 결과가 없을 때 "변경된 조문이 없습니다" 메시지 있음 — 유지.
