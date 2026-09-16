#!/usr/bin/env python3
"""규정다름 — 서비스 동작 방식 설명 (400자 이내) - 강정민 팀 MABC 2026 결선"""

TEXT = (
    "행정규칙/지침 구판·신판 텍스트를 붙여넣으면 조문별 대조표와 시행일 D-day를 자동 출력하는 서비스입니다. "
    "입력: 구판·신판 텍스트를 붙여넣고 '대조 실행' 클릭. "
    "처리: admrul-diff 스크립트가 조항 단위 diff(added/modified/deleted) 판정, 부칙 시행일을 파싱해 오늘(KST) 기준 D-day/시행상태를 계산. "
    "계산은 스크립트만 수행, LLM 임의 추정 없음. "
    "출력: 신·구 조문 대조표(신설/변경/삭제)와 시행 D-day 표 표시. "
    "샘플: '샘플 불러오기'로 구판(2026.3.1. 시행)·신판(2026.9.15. 시행) 텍스트를 바로 입력 가능. "
    "예외: 구판/신판 중 하나라도 비었거나 조문 패턴(제N조)이 없으면 오류 표시. "
    "로그인 없이 누구나 바로 사용할 수 있음."
)

print(f"공백 포함: {len(TEXT)} 자")
print()
print("=== 내용 ===")
print(TEXT)

with open("/Users/felix/mabc-finals/SERVICE_DESCRIPTION.txt", "w", encoding="utf-8") as f:
    f.write(TEXT)
print(f"\n저장 완료: {len(TEXT)} 자")
