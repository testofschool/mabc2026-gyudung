# 에이전트 지침 — 규정다름 (MABC 2026 결선)

> 이 파일은 프로젝트에 참여하는 모든 코딩 에이전트에게 항상 전달되는 지침이다.
> 세부 워크플로는 orchestration.md, 스킬은 skills/, 참조 문서는 docs/references/를 본다.

## 한 줄 요약

행정규칙/지침/훈령 등 조문 단위로 바뀌는 문서를 **구판·신판 텍스트만 넣으면 조항별 대조표 + 시행일/D-day까지 자동 출력**하는 서비스를 MABC 2026 결선에 제출한다. 마감: **2026-09-16(수) 23:59**.

## 이 프로젝트의 중심 스킬

- `skills/admrul-diff/SKILL.md` — 행정규칙 신·구 조문 대조 스킬 (실제 계산은 `scripts/admrul_diff.py`에서 수행)
- 계산·판정은 반드시 스크립트로만 수행한다. LLM이 임의 추정하면 안 된다.

## 새 세션 진입 순서

1. `CONTEXT.md` 읽기 — 현재 상태·미결 항목·파일 위치
2. `agent.md` 읽기 — 프로젝트 전반의 에이전트 원칙
3. `orchestration.md` 읽기 — 작업 흐름·역할·서브에이전트 라우팅
4. `todo.md` 확인 — 활성 작업 항목
5. `decision.md` 확인 — 이미 내려진 결정

## 제출물 (필수)

대회 제출 양식 2 PDF 기준:

1. 서비스 공개 URL (로그인 없이, 심사 시점 접속 가능)
2. GitHub 레포지토리 URL (Public, API 키·토큰 코드 포함 금지)
3. 서비스 동작 방식 설명 (400자 이내, 입력→처리→출력)
4. PRD PDF (`팀명_PRD.pdf`, 10MB 이하)
5. 포스터 PDF (`팀명_포스터.pdf`, A1 세로 1장, 템플릿 사용, 글꼴 아웃라인/임베딩)
6. 발표자료 PDF (`팀명_발표자료.pdf`, 10MB 이하)
7. 데모 영상 MP4 (`팀명_데모영상.mp4`, 3분 이내 실제 동작 화면, 100MB 이하)
8. 본 양식의 서비스 소개 작성

하나라도 누락 시 정상 접수·심사 대상에서 제외될 수 있다.

## 금지

- admirl-diff의 diff 판정·시행일/D-day를 LLM이 임의 계산·추정하지 않는다.
- 외부 주장(경쟁자·시장·정책 동향)을 확인 없이 확정 사실로 쓰지 않는다.
- 연구 byproducts가 `submission/`을 오염시키지 않는다.
- 코드에 API 키·토큰을 포함하지 않는다 (GitHub Public 조건).

## 참조

- 대회 제출 양식: `research/[MABC 2026] 결선 결과물 제출 양식.pdf`, `research/[MABC 2026] 결선 결과물 제출 양식 2.pdf`
- 발표 템플릿: `research/[MABC] 발표 PPT Slide Template.pptx.pdf`
- 컨텍스트: `CONTEXT.md`
- 오케스트레이션: `orchestration.md`
- 스킬 카탈로그: `skill-manifest.md`
