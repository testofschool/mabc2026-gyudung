# MABC 2026 결선 — 규정다름 ( AdmRul-Diff 기반 서비스 )

행정규칙/지침/훈령 등 조문 단위로 바뀌는 문서를 **구판·신판 텍스트만 넣으면 조항별 대조표 + 시행일/D-day까지 자동 출력**하는 서비스다.

- 핵심 로직: `skills/admrul-diff/SKILL.md` (실제 실행은 `scripts/admrul_diff.py`)
- 제출 마감: **2026-09-16(수) 23:59**
- 제출 양식 근거: `research/[MABC 2026] 결선 결과물 제출 양식 2.pdf`

## 뭘 하는 프로젝트인가

- 대상 사용자: 행정규칙/지침을 자주 다루는 실무 담당자, 정책·연구자, 공공기관 종사자
- 해결하고 싶은 불편: 개정 전후 조문을 사람이 눈으로 일일이 대조 + 시행일/D-day를 따로 확인해야 하는 작업
- 우리가 주는 것: 구판/신판 텍스트 입력 → added/modified/deleted 대조표 + 시행일/D-day/시행상태 출력

## 프로젝트 구조 한눈에

```
mabc-finals/
├── AGENTS.md              # 루트 에이전트 지침 (항상 로드)
├── CLAUDE.md              # Claude Code용 — 첫 줄: @AGENTS.md
├── agent.md               # 범용 에이전트 지침 (플랫폼 독립)
├── orchestration.md       # 작업 흐름·역할·서브에이전트 라우팅
├── skill-manifest.md      # 프로젝트 스킬 카탈로그
├── todo.md                # 활성 작업 항목
├── decision.md            # 결정 로그 (ADR 스타일)
├── progress.md            # 세션별 작업 로그
├── skills/                # 프로젝트 정의 스킬
│   └── admrul-diff/       # → prelim/admrul-diff로 심볼릭 링크 예정
├── .agents/               # 에이전트 런타임 설정
│   ├── orchestration.md   # 오케스트레이션 맵
│   ├── skills/
│   ├── memories/
│   └── tasks/
├── docs/
│   ├── references/        # 장문 참조 문서
│   └── conventions/
│       └── SKILL_conventions.md
├── submission/            # 제출물
│   ├── PRD/
│   ├── poster/
│   ├── presentation/
│   ├── demo-video/
│   └── checklist.md
├── scripts/               # 결정론적 검증 스크립트
├── service/               # 서비스 코드
│   ├── app.py
│   └── requirements.txt
├── prelim/                # 기확보 스킬 (admirl-diff 등)
└── research/              # 연구용 (제출물 오염 방지)
```

## 빠르게 시작하는 법

1. 새 세션 진입 시 `CONTEXT.md` → `agent.md` → `orchestration.md` 순서로 읽는다.
2. MABC 마감 관련 작업은 `todo.md` 상단 항목부터 처리한다.
3. admirl-diff 실행이 필요하면 `skills/admrul-diff/SKILL.md`를 따르고, 계산은 반드시 `scripts/admrul_diff.py`로만 수행한다.
4. 외부 주장(경쟁자·시장·정책 동향)은 웹검색/웹추출로 1차 소스 확인 후 쓴다.

## 규칙 요약

- **대회규칙이 최상위.** 제출 양식 2 PDF의 필수 항목·파일명 규칙·용량·형식을 반드시 지킨다.
- **admirl-diff 계산은 스크립트에서만.** LLM이 임의 추정·재구성하면 안 된다.
- **admirl-diff의 판정(added/modified/deleted), 시행일/D-day는 스크립트가 낸 결과만 최종.**
- **PDF·포스터·발표자료·데모영상은 제출용 폴더에만.** 연구 byproducts가 제출물 폴더를 오염시키면 안 된다.
- **API 키·토큰이 코드에 들어가면 안 된다.** GitHub Public 제출 조건.
