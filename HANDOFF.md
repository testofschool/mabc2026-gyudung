# HANDOFF — 규정다름 MABC 2026 결선 제출 (강정민 팀)
- Updated: 2026-09-16
- Session: Solar Pro 4 세션 (2026-09-16)
- Reference files:
  - AGENTS.md (프로젝트 지침)
  - CONTEXT.md (현재 상태·미결 항목)
  - STATE.md (현재 상태)
  - decisions.md (통합 결정 로그 — D-001~D-013)
  - research/[MABC 2026] 결선 결과물 제출 양식 2.pdf (제출 규칙)
  - prelim/admrul-diff/scripts/admrul_diff.py (핵심 로직)
  - service/public/index.html (프론트)
  - service/api/admrul-diff/index.py (API)
  - vercel.json (Vercel 배포 설정)
  - docs/references/evaluation-gap-analysis.md (평가 갭 분석)
  - docs/references/submission-preflight-report.md (제출물 프리플라이트 보고서)

## 1. Current state summary

규정다름 서비스는 Vercel에 배포되어 live 상태. `https://mabc-finals.vercel.app/` HTTP 200(프론트엔드), `/api/admrul-diff` POST 정상 동작(diff + D-day 정확 반환). GitHub Public 확인됨. 제출물 8종 중 6종 완성(PRD·포스터·발표자료·서비스소개·400자 설명·GitHub·URL), 2종 미완료(데모영상 MP4·Google Form 제출). 마감 2026-09-16 23:59 KST.

**데모 영상 녹화는 이번 세션에서 사용자가 직접 수행하기로 함.** Solar Pro 4로는 더 이상 진행하지 않음.

이번 세션에서 통합 결정 로그 `decisions.md`(구 decision.md 대체)와 제출 직전 점검 문서 2종(evaluation-gap-analysis.md, submission-preflight-report.md)을 프로젝트 지식으로 작성함.

## 2. Key context (what the next session must know)

- **서비스 URL**: https://mabc-finals.vercel.app — Vercel 배포됨, 루트 200 + API 동작 확인됨 (이번 세션 curl 검증)
- **GitHub**: https://github.com/testofschool/mabc2026-gyudung — Public (이번 세션 재확인: visibility=public)
- **README 정합 복구**: 프로젝트 구조·시작 방법에 적혀 있던 존재하지 않는 파일(CLAUDE.md, agent.md, orchestration.md, todo.md, progress.md, skill-manifest.md, submission/checklist.md, service/app.py, docs/conventions/)을 실제 repo 구조로 교체 및 커밋·푸시 완료 (e4c32da)
- **미완료 항목**:
  - `강정민_데모영상.mp4` — **사용자가 직접 녹화 예정**. Safari에서 서비스 URL 열기 → 샘플 불러오기 → 대조 실행 → 결과 확인 시나리오. 3분 이내, 100MB 이하. 녹화 후 파일 존재 여부·용량만 확인하면 됨.
  - Google Form 제출 — gangjeongmin23@gmail.com으로 모든 항목 작성 및 파일 업로드 필요. 제출 양식 1(인적사항)·2(URL·GitHub·설명·파일 업로드) 모두 작성 필요.
- **제출 직전 점검 문서(신임)**: `docs/references/evaluation-gap-analysis.md`, `docs/references/submission-preflight-report.md`. 제출 전 자가 점검용. rubric 미확보 상태에서 제출 양식 2 + skill-to-service 프레임워크로 "비어 있을 수 있는 셀"을 식별한 것.
- **STATE.md 주의**: STATE.md는 현재 구버전 정보를 포함할 수 있음(PRD·포스터·발표자료 "미제작" 표기, 서비스 설명 540자 표기 등). 실제는 모두 완성됨. 최신 상태는 이 HANDOFF 및 decisions.md 기준.
- **반복 실패/못 봄 패턴(이 세션 리뷰)**: tesseract 이미 설치(5.5.2)돼 있었는데도 스크린샷 읽기를 위해 더 무거운 접근을 먼저 돌고 tesseract를 뒤로 미룸. vision_analyze 불가 후 OCR을 충분히 먼저 시도하지 않음. rubric 없다고 평가 분석을 먼저 접어두려는 패턴 있었음(이후 제출 양식 2 + skill-to-service 프레임으로 밀고 감).

## 3. Immediate next steps

1. **데모 영상 녹화** (사용자 담당): Safari에서 `https://mabc-finals.vercel.app` 열고 샘플 불러오기 → 대조 실행 → 결과 확인까지 녹화. `강정민_데모영상.mp4`로 저장, 3분 이내·100MB 이하 확인.
2. **Google Form 제출**: gangjeongmin23@gmail.com으로 로그인 → 제출 양식 1(인적사항: 이메일, 팀명 강정민, 팀장 연락처, 플랫폼 Hermes Agent, 플랫폼 계정, 데모데이 참석자) 작성 → 제출 양식 2(서비스 URL `https://mabc-finals.vercel.app`, GitHub URL `https://github.com/testofschool/mabc2026-gyudung`, 동작 방식 설명 SERVICE_DESCRIPTION_400CHAR.txt 내용, PRD·포스터·발표자료·데모영상 파일 업로드) 작성 → 제출.
3. **제출 전 최종 확인**: GitHub Public 여부, 코드에 API 키 없음, 파일명 규칙(팀이_파일명), 용량 제한(PRD·포스터·발표자료 10MB 이하, 데모영상 100MB 이하).
4. **필요 시 제출 직전 점검 문서 재확인**: `docs/references/submission-preflight-report.md` (항목별로 충족/미충족/근거 확인), `docs/references/evaluation-gap-analysis.md` (리스크·권고).
5. **필요 시 더 정밀한 폐쇄망 표현 검토**: "현재 배포 서비스는 인터넷 연결 필요, 단 계산 로직은 스크립트 기반이라 로컬 실행 가능" 수준으로 한계 명시할지 여부. 공간·시간 제약상 선택.

## 4. Decisions and rationale

- **팀명 "강정민"으로 확정** (CONTEXT.md 기준) — see D-001
- **admrul-diff를 MABC 결선 서비스로 유지** (핵심 로직 이미 작동, 새 서비스 구축 시간 없음) — see D-002
- **Vercel 배포 유지** (이미 live, 별도 배포 환경 설정 시간 없음) — see D-003
- **제출물 제작 우선순위**: PRD·발표자료·포스터 → 서비스 소개(양식 내) 순으로 제작 — see D-004
- **서비스 동작 방식 설명 400자 제한 준수** — see D-005
- **포스터 템플릿 미사용 + 운영진 확인 필요 상태 유지** — see D-006
- **데모 영상 제작 방식: screencapture + ffmpeg 합성** — see D-007
- **데모 영상 녹화는 사용자가 직접 수행** — see D-008
- **평가 분석은 rubric 미확보 상태에서 제출 양식 2 + skill-to-service 프레임워크로 수행** — see D-009
- **법.net 과주장 정제 (1차 소스 근거 TRUE)** — see D-010
- **폐쇄망/온프레미스 표현 정밀도 검토 (해석 여지 남김, 정밀 표현 권고)** — see D-011
- **제출 직전 점검 문서 2종 생성** — see D-012
- **reusable asset candidate: tesseract/Playwright 이미 설치된 사실을 프로젝트 지식으로 남김** — see D-013
