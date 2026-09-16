#!/usr/bin/env python3
"""규정다름 — 서비스 동작 방식 설명 (400자 이내)"""

# 공백 포함 400자 이내로 축소
TEXT = (
    "규정다름은 행정규칙/지침/훈령/예규/요령의 구판과 신판 텍스트를 붙여넣으면 "
    "조문별 대조표와 시행일 D-day를 자동 출력하는 서비스입니다. "
    "입력: 구판/신판 텍스트를 각 영역에 붙여넣고 [대조 실행]을 누릅니다. "
    "샘플 불러오기로 데모 데이터를 바로 입력할 수 있습니다. "
    "처리: admrul-diff 스크립트가 조항 단위 added/modified/deleted를 판정하고 "
    "부칙 시행일을 파싱하여 오늘(KST) 기준 D-day/시행상태를 계산합니다. "
    "모든 계산은 스크립트가 수행하며 LLM은 임의 추정하지 않습니다. "
    "출력: 신/구 조문 대조표(신설/변경/삭제 구분)와 시행 D-day 표가 표시됩니다. "
    "변경된 조문이 없으면 '변경된 조문이 없습니다'가 표시됩니다. "
    "예외: 구판/신판 중 하나라도 비어 있거나 조문 패턴(제N조)이 없으면 오류 메시지가 표시됩니다. "
    "로그인 없이 누구나 바로 사용할 수 있습니다."
)

print(f"공백 포함: {len(TEXT)} 자")
print(f"공백 제외: {len(TEXT.replace(' ', '').replace(chr(10), ''))} 자")
print()
print("=== 내용 ===")
print(TEXT)

# 400자 이내면 저장
if len(TEXT) <= 400:
    with open("/Users/felix/mabc-finals/SERVICE_DESCRIPTION_400CHAR.txt", "w", encoding="utf-8") as f:
        f.write(TEXT)
    print(f"\n저장 완료: {len(TEXT)}자")
else:
    print(f"\n오류: {len(TEXT)}자로 400자 초과")
