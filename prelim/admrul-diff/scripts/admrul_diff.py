#!/usr/bin/env python3
"""
admrul-diff: 행정규칙/지침 신·구 조문 대조 및 시행 D-day 계산기

- 신·구 조문 비교, diff 판정(added/modified/deleted), 부칙 시행일 파싱 및
  오늘 날짜 기준 D-day 계산은 이 스크립트에서만 수행한다.
- LLM 은 이 스크립트가 출력한 JSON 을 받아 표로 렌더링만 해야 하며,
  자체 판정·추정·계산을 절대 수행하지 않는다.
"""

import json
import os
import re
import sys
from datetime import date, datetime, timezone, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# 조문 파싱
# ---------------------------------------------------------------------------

_ARTICLE_RE = re.compile(
    r'제(\d+)조(?:의(\d+))?(?:\(([^)]*)\))?\s*(.*)'
)
"""제N조 / 제N조의M + (제목) + 본문 패턴.
- group(1): 기본 조문 번호 문자열 (예: "4")
- group(2): 가지 번호 문자열 (예: "2"); 없으면 None
- group(3): 괄호 제목 (없으면 None)
- group(4): 괄호 뒤 본문 (없을 수 있음, None 체크 필수)
- 괄호 없는 조문(제1조 이 규정은...) 도 group(3)=None, group(4)=전체 본문으로 잡힌다.
"""


def _assemble_article_number(base: str, branch: Optional[str]) -> str:
    """기본 조문 번호와 가지 번호를 조합하여 '4의2' 형태의 조문 ID를 만든다."""
    if branch:
        return f"{base}의{branch}"
    return base


def parse_articles(text: str) -> dict[str, dict[str, str]]:
    """텍스트에서 제N조(제목) 형태 조문을 파싱하여 {조문ID(str): {title, content}} 로 반환.

    다중 행 조문 처리:
    - '제N조'로 시작하는 줄을 만나면 새 조문으로 시작
    - 그 다음 줄들은 다음 '제N조'나 '부칙'이 나오기 전까지 현재 조문의 본문에 누적
    - 조문 ID는 정수(int)가 아닌 문자열(str)로 저장하여 '제4조의2' 같은 가지조문이 유실되지 않도록 한다.
    """
    articles: dict[str, dict[str, str]] = {}
    current_num: Optional[str] = None
    current_title: Optional[str] = None
    current_lines: list[str] = []

    _ARTICLE_START_RE = re.compile(r'제\d+조(?:의\d+)?(?:\s|\(|$)')

    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_num is not None:
                current_lines.append(stripped)
            continue

        if current_num is None:
            m = _ARTICLE_RE.match(stripped)
            if m:
                current_num = _assemble_article_number(m.group(1), m.group(2))
                current_title = m.group(3) if m.group(3) else ""
                body = m.group(4) or ""
                body = body.strip()
                current_lines = [body] if body else []
            else:
                continue
        else:
            if _ARTICLE_START_RE.match(stripped) or stripped.startswith("부칙"):
                content = "\n".join(current_lines).strip()
                articles[current_num] = {
                    "title": current_title,
                    "content": content,
                }
                m = _ARTICLE_RE.match(stripped)
                if m:
                    current_num = _assemble_article_number(m.group(1), m.group(2))
                    current_title = m.group(3) if m.group(3) else ""
                    body = m.group(4) or ""
                    body = body.strip()
                    current_lines = [body] if body else []
                else:
                    current_num = None
                    current_title = None
                    current_lines = []
            else:
                current_lines.append(stripped)

    if current_num is not None:
        content = "\n".join(current_lines).strip()
        articles[current_num] = {
            "title": current_title,
            "content": content,
        }

    return articles


# ---------------------------------------------------------------------------
# 시행일 파싱
# ---------------------------------------------------------------------------

# 부칙 시행일: '이 지침은/이 규정은/이 훈령은/이 예규는/이 요령은 ... 시행한다.'
# 다양한 행정규칙 주체 표현을 모두 인식
_ENACT_SUBJECTS = [
    "지침",
    "규정",
    "훈령",
    "예규",
    "요령",
]

# 각 주체별 패턴: "이 <주체>은/는 YYYY년 M월 D일부터 시행"
# 은/는 선택: '지침은', '규정은', '훈령은', '요령은' (모음 뒤 '는') / '예규는' 등
# 한국어 조사: 받침 있으면 '은', 없으면 '는'. 통일적으로 '(은|는)'으로 처리.
_ENACT_BIS_PATTERNS = []
for subj in _ENACT_SUBJECTS:
    _ENACT_BIS_PATTERNS.append(
        re.compile(
            rf"이\s*{subj}(?:은|는)\s*(\d{{4}})\s*년\s*(\d{{1,2}})\s*월\s*(\d{{1,2}})\s*일부터\s*시행"
        )
    )

# 헤더: "[시행 YYYY. M. D.]"
_ENACT_HEADER_RE = re.compile(
    r'\[시행\s+(\d{4})\.?\s*(\d{1,2})\.?\s*(\d{1,2})\.?\s*\]'
)


def parse_enactment_date(text: str) -> Optional[date]:
    """부칙 또는 헤더에서 시행일자를 추출한다. 없으면 None."""
    for line in text.splitlines():
        for pat in _ENACT_BIS_PATTERNS:
            m = pat.search(line)
            if m:
                y, mth, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                return date(y, mth, d)
        m = _ENACT_HEADER_RE.search(line)
        if m:
            y, mth, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return date(y, mth, d)
    return None


# ---------------------------------------------------------------------------
# Diff 판정
# ---------------------------------------------------------------------------

def compute_diff(
    old_articles: dict[str, dict[str, str]],
    new_articles: dict[str, dict[str, str]],
) -> list[dict]:
    """구·신 조문을 비교하여 diff 목록을 반환한다.

    - 조문 ID는 문자열(str)로 비교한다 (가지조문 '4의2' 등 보존).
    - 양쪽 존재 & 내용/제목 상이 → modified
    - 구판에만 존재 → deleted
    - 신판에만 존재 → added
    - 양쪽 존재 & 내용/제목 동일 → diff 에서 제외 (변경 없음)
    """
    diff: list[dict] = []
    all_nums = sorted(set(old_articles) | set(new_articles))
    for num in all_nums:
        old = old_articles.get(num)
        new = new_articles.get(num)
        if old and new:
            if old["content"] != new["content"] or old["title"] != new["title"]:
                # 제목이 비어 있으면 조문 ID 자체를 제목으로 사용
                title = new["title"] or f"제{num}조"
                diff.append({
                    "article_number": num,
                    "article_title": title,
                    "judgment": "modified",
                    "old_content": old["content"],
                    "new_content": new["content"],
                })
        elif old and not new:
            title = old["title"] or f"제{num}조"
            diff.append({
                "article_number": num,
                "article_title": title,
                "judgment": "deleted",
                "old_content": old["content"],
                "new_content": "",
            })
        elif new and not old:
            title = new["title"] or f"제{num}조"
            diff.append({
                "article_number": num,
                "article_title": title,
                "judgment": "added",
                "old_content": "",
                "new_content": new["content"],
            })
    return diff


# ---------------------------------------------------------------------------
# D-day 판정 (KST 기준, 3상태 + 미검출)
# ---------------------------------------------------------------------------

def _today_kst() -> date:
    """현재 시각을 한국 표준시(KST, UTC+9) 기준으로 변환하여 오늘 날짜를 반환한다.

    샌드박스 환경 시계가 UTC 로 동작하여 날짜가 하루 밀리는 것을 방지한다.
    """
    tz_kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(tz_kst)
    return now_kst.date()


def d_day_status(enactment: Optional[date], reference: date) -> str:
    """시행일자와 기준일자(KST 오늘)를 비교하여 D-day 상태를 반환한다.

    - 시행일이 오늘 이후(미래): "D-n"  (n = 남은 일수, 수식 기호 없는 일반 텍스트)
    - 시행일이 오늘: "오늘 시행"
    - 시행일이 오늘 이전(과거): "시행중"
    - 시행일이 None: "시행일 미검출"
    """
    if enactment is None:
        return "시행일 미검출"
    delta = (enactment - reference).days
    if delta == 0:
        return "오늘 시행"
    if delta > 0:
        return f"D-{delta}"
    return "시행중"


# ---------------------------------------------------------------------------
# 입력 validation
# ---------------------------------------------------------------------------

_ARTICLE_START_PATTERN = re.compile(r'제\d+(?:의\d+)?조\b')


def validate(old_text: str, new_text: str) -> tuple[bool, str]:
    """입력이 행정규칙/지침으로 보이는지 검사한다.

    가지조문(제N조의M) 및 괄호 없는 조문(제N조 본문...) 패턴도 유효로 인식한다.
    """
    if not old_text.strip():
        return False, "구판 입력이 비어 있습니다."
    if not new_text.strip():
        return False, "신판 입력이 비어 있습니다."
    if not _ARTICLE_START_PATTERN.search(old_text):
        return False, "구판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다."
    if not _ARTICLE_START_PATTERN.search(new_text):
        return False, "신판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다."
    return True, ""


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

_SAMPLE_NAMES = {  # 샘플 파일명 상수
    "old": "admrul_sample_old.txt",
    "new": "admrul_sample_new.txt",
}


def _find_sample(filename: str) -> Optional[str]:
    """샘플 파일을 스킬 패키지 내 samples/ 에서 찾고, 없으면 작업디렉토리에서 찾는다."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    candidates = [
        os.path.join(skill_dir, "samples", filename),
        os.path.join(os.getcwd(), filename),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def main() -> None:
    # --- 입력 결정 -----------------------------------------------------------
    if len(sys.argv) == 1:
        # 데모 모드: 샘플 내장 파일 사용
        old_path = _find_sample(_SAMPLE_NAMES["old"])
        new_path = _find_sample(_SAMPLE_NAMES["new"])
        if old_path is None or new_path is None:
            print(json.dumps({
                "error": True,
                "message": "데모 샘플 파일을 찾을 수 없습니다. (samples/ 또는 작업디렉토리에 admrul_sample_old.txt / admrul_sample_new.txt 필요)",
            }, ensure_ascii=False, indent=2))
            sys.exit(2)
        try:
            with open(old_path, "r", encoding="utf-8") as f:
                old_text = f.read()
            with open(new_path, "r", encoding="utf-8") as f:
                new_text = f.read()
        except FileNotFoundError as e:
            print(json.dumps({
                "error": True,
                "message": f"샘플 파일 읽기 실패: {e}",
            }, ensure_ascii=False, indent=2))
            sys.exit(2)

    elif len(sys.argv) == 3:
        old_path, new_path = sys.argv[1], sys.argv[2]
        try:
            with open(old_path, "r", encoding="utf-8") as f:
                old_text = f.read()
            with open(new_path, "r", encoding="utf-8") as f:
                new_text = f.read()
        except FileNotFoundError as e:
            print(json.dumps({
                "error": True,
                "message": f"파일을 찾을 수 없습니다: {e}",
            }, ensure_ascii=False, indent=2))
            sys.exit(2)

    else:
        print(json.dumps({
            "error": True,
            "message": "사용법: python admrul_diff.py [구판파일] [신판파일]  (파일 미지정 시 데모 모드)",
        }, ensure_ascii=False, indent=2))
        sys.exit(2)

    # --- validation ----------------------------------------------------------
    ok, msg = validate(old_text, new_text)
    if not ok:
        print(json.dumps({
            "error": True,
            "message": msg,
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # --- 파싱 ---------------------------------------------------------------
    old_articles = parse_articles(old_text)
    new_articles = parse_articles(new_text)
    old_enact = parse_enactment_date(old_text)
    new_enact = parse_enactment_date(new_text)

    # --- 계산 ---------------------------------------------------------------
    today_kst = _today_kst()
    diff = compute_diff(old_articles, new_articles)

    result = {
        "diff": diff,
        "enactment": {
            "old_date": old_enact.strftime("%Y-%m-%d") if old_enact else None,
            "new_date": new_enact.strftime("%Y-%m-%d") if new_enact else None,
            "reference_date": today_kst.strftime("%Y-%m-%d"),
            "new_d_day_status": d_day_status(new_enact, today_kst),
            "old_d_day_status": d_day_status(old_enact, today_kst),
        },
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
