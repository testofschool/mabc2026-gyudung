# 프로젝트 상태 — 규정다름 (강정민 팀, MABC 2026 결선)

## 현재 상태

- **서비스**: https://mabc-finals.vercel.app — live, 프론트엔드 + API 모두 동작 확인됨 (2026-09-16 curl 검증)
  - 구판/신판 텍스트 입력 → POST /api/admrul-diff → diff 결과 + D-day 반환
  - admrul_diff.py 스크립트가 모든 계산 수행 (LLM 임의 추정 없음)
- **GitHub**: https://github.com/testofschool/mabc2026-gyudung — Public 확인됨
- **제출 양식**: research/[MABC 2026] 결선 결과물 제출 양식 2.pdf — 필수 항목 8종 확인 완료

## 제출물 상태 (2026-09-16 기준)

| # | 항목 | 파일명 | 상태 |
|---|---|---|---|
| 1 | 서비스 공개 URL | — | 완료 (https://mabc-finals.vercel.app) |
| 2 | GitHub URL | — | 완료 (Public) |
| 3 | 서비스 동작 방식 설명 | 양식 내 텍스트 | 완료 (395자, SERVICE_DESCRIPTION_400CHAR.txt) |
| 4 | PRD PDF | 강정민_PRD.pdf | 완료 (57,886 bytes, 5p) |
| 5 | 포스터 PDF | 강정민_포스터.pdf | 완료 (33,064 bytes, 1p) |
| 6 | 발표자료 PDF | 강정민_발표자료.pdf | 완료 (56,973 bytes, 8p) |
| 7 | 데모 영상 MP4 | 강정민_데모영상.mp4 | **사용자 직접 녹화 예정** |
| 8 | 서비스 소개 | 양식 내 텍스트 | 완료 (강정민_서비스소개.txt, 1,417 bytes) |

## 환경

- Vercel CLI 54.6.1, GitHub(testofschool) 로그인
- Python 3.11.15, fpdf2 + reportlab + markdown + pypdf 설치됨
- 나눔스퀘어네오 OTF 폰트 있음 (사용자 라이브러리)
- ffmpeg 있음, screencapture 있음 (화면 캡처 가능)
- Safari: JavaScript from Apple Events 권한 없음 (버튼 클릭 제어에 제한)

## 이번 세션 작업

- README.md 프로젝트 구조·시작 방법 정정: 실제 repo에 존재하지 않는 파일(CLAUDE.md, agent.md, orchestration.md, todo.md, progress.md, skill-manifest.md, submission/checklist.md, service/app.py, docs/conventions/) 제거 + 실제 구조(CONTEXT.md, STATE.md, HANDOFF.md, MEMORY.md, prelim/ 하위 스킬, service/api/admrul-diff/index.py, service/public/index.html, service/uv.lock 등)로 교체
- CLAUDE.md 구조 항목 삭제 커밋 후 푸시 (0d596b4 → e4c32da)
- GitHub 저장소 공개 상태 확인: public 확인 (https://github.com/testofschool/mabc2026-gyudung)
- READMD.md "빠르게 시작하는 법"을 실제 파일(AGENTS.md → project-state/) 기준으로 정정
- /session-close 준비: STATE.md·HANDOFF.md 정합 갱신

## 다음 세션 우선 작업

1. **데모 영상 녹화** (사용자 담당): Safari에서 서비스 URL 열기 → 샘플 불러오기 → 대조 실행 → 결과 확인까지 녹화, `강정민_데모영상.mp4` 저장 (3분 이내, 100MB 이하)
2. **Google Form 제출**: gangjeongmin23@gmail.com으로 로그인 → 제출 양식 1(인적사항) + 제출 양식 2(URL·GitHub·설명·파일 업로드) 작성 → 제출
3. 제출 전 최종 확인: GitHub Public, API 키 없음, 파일명 규칙, 용량 제한
