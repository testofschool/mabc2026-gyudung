# 새 세션 진입 프롬프트 — 규정다름 (MABC 2026 결선)

> 이 텍스트를 새 Solar Pro 4 세션 시작 시 그대로 복붙한다.

---

우리는 MABC 2026 결선 제출물을 만들고 있고, 마감은 **2026-09-16(수) 23:59**다.  
중심 서비스는 admrul-diff 기반 **규정다름**이다.

이 세션은 **Solar Pro 4만 사용**한다. Claude/Codex/Gemini/Cursor/Copilot 등 다른 LLM·에이전트 관련 파일이나 흔적은 만들지 않는다.

새 세션이면 먼저 아래 프로젝트 상태 폴더만 읽는다. repo 전체를 처음부터 스캔하지 않는다.

## 먼저 읽을 파일 (순서 고정)

1. `/Users/felix/mabc-finals/project-state/README.md`
2. `/Users/felix/mabc-finals/project-state/MEMORY.md`
3. `/Users/felix/mabc-finals/project-state/STATE.md`
4. `/Users/felix/mabc-finals/project-state/HANDOFF.md`

 그다음 아래 핵심 파일도 필요한 만큼만 본다.

5. `/Users/felix/mabc-finals/AGENTS.md`
6. `/Users/felix/mabc-finals/CONTEXT.md`
7. `/Users/felix/mabc-finals/models.md`
8. `/Users/felix/mabc-finals/STATE.md` (현재 todo·작업 상태)

## 작업 시작 전 확인할 것

- 현재 활성 todo는 무엇인가
- 직전 세션에서 끝난 것과 안 끝난 것
- 이번 세션에 뭘 할지 사용자 확인이 필요한가

## 반드시 지킬 것

- admrul-diff의 diff 판정·시행일/D-day 계산은 **스크립트(`scripts/admrul_diff.py`)로만** 수행한다. LLM이 임의로 계산·추정하면 안 된다.
- 외부 주장(경쟁자·시장·정책 동향 등)은 웹검색/웹추출로 1차 소스를 확인한 뒤에만 쓴다.
- 제출 양식 2 PDF의 필수 항목·파일명 규칙·용량·형식을 반드시 지킨다.
- 코드에는 API 키·토큰을 넣지 않는다 (GitHub Public 제출 조건).
- 연구 byproducts가 `submission/` 폴더를 오염시키지 않게 한다.

## 이번 세션 목표

사용자가 별도로 요청하지 않았으면, STATE.md와 HANDOFF.md에 적힌 다음 액션부터 이어서 진행한다.
