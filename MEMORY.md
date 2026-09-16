# 프로젝트 메모리 — 규정다름 (강정민 팀, MABC 2026 결선)

## 팀 정보
- 팀명: 강정민
- 참가자: 강정민 (단독)
- 이메일: gangjeongmin23@gmail.com
- 플랫폼: Hermes Agent

## 서비스
- 이름: 규정다름
- URL: https://mabc-finals.vercel.app
- GitHub: https://github.com/testofschool/mabc2026-gyudung
- 핵심: admrul-diff 스크립트 (prelim/admrul-diff/scripts/admrul_diff.py)
- 아키텍처: 단일 HTML + Vercel 서버리스 Python API (POST /api/admrul-diff)

## 대회 마감
- 2026-09-16(수) 23:59 KST
- 제출 양식: research/[MABC 2026] 결선 결과물 제출 양식 2.pdf
- 필수 제출물 8종 (서비스 URL, GitHub, 동작방식 설명, PRD, 포스터, 발표자료, 데모영상, 서비스 소개)

## 금지 사항
- admrul-diff의 diff 판정·시행일/D-day 계산을 LLM이 임의 수행 금지 (스크립트만 사용)
- 외부 주장은 웹검색/웹추출로 1차 소스 확인 후 사용
- 코드에 API 키·토큰 포함 금지 (GitHub Public)
- 연구 byproducts가 submission/ 폴더 오염 금지

## 작업 스타일
- 추상 조언보다 실제 파일·규칙·저장소 상태 기준 순서 선호
- 웹서치 적극 활용 원함
- 대회규칙(제출 항목·파일명·공개 URL 로그인 없이 접속·GitHub Public 등)을 최우선 중시
- 세션 종료는 /session-close로 정리하고 STATE.md 형태 재개 지점 남기는 것 승인

## 주요 파일 위치
- 핵심 스크립트: prelim/admrul-diff/scripts/admrul_diff.py
- 서비스 프론트: service/public/index.html
- 서비스 API: service/api/admrul-diff/index.py
- 제출 양식: research/[MABC 2026] 결선 결과물 제출 양식 2.pdf
- 발표 템플릿: research/[MABC] 발표 PPT Slide Template.pptx.pdf
