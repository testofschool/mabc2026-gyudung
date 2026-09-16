import sys
import os
import json
from datetime import date, datetime, timezone, timedelta
from typing import Optional
import re

# ---------------------------------------------------------------------------------------
# 조문 파싱
# ---------------------------------------------------------------------------------------

_ARTICLE_RE = re.compile(
    r'제(\d+)조(?:의(\d+))?(?:\(([^)]*)\))?\s*(.*)'
)

def _assemble_article_number(base: str, branch: Optional[str]) -> str:
    if branch:
        return f"{base}의{branch}"
    return base

def parse_articles(text: str) -> dict:
    articles = {}
    current_num = None
    current_title = None
    current_lines = []

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


# ---------------------------------------------------------------------------------------
# 시행일 파싱
# ---------------------------------------------------------------------------------------

_ENACT_SUBJECTS = ["지침", "규정", "훈령", "예규", "요령"]
_ENACT_BIS_PATTERNS = []
for subj in _ENACT_SUBJECTS:
    _ENACT_BIS_PATTERNS.append(
        re.compile(
            rf"이\s*{subj}(?:은|는)\s*(\d{{4}})\s*년\s*(\d{{1,2}})\s*월\s*(\d{{1,2}})\s*일부터\s*시행"
        )
    )

_ENACT_HEADER_RE = re.compile(
    r'\[시행\s+(\d{4})\.?\s*(\d{1,2})\.?\s*(\d{1,2})\.?\s*\]'
)

def parse_enactment_date(text: str) -> Optional[date]:
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


# ---------------------------------------------------------------------------------------
# Diff 판정
# ---------------------------------------------------------------------------------------

def compute_diff(old_articles: dict, new_articles: dict) -> list:
    diff = []
    all_nums = sorted(set(old_articles) | set(new_articles))
    for num in all_nums:
        old = old_articles.get(num)
        new = new_articles.get(num)
        if old and new:
            if old["content"] != new["content"] or old["title"] != new["title"]:
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


# ---------------------------------------------------------------------------------------
# D-day 판정
# ---------------------------------------------------------------------------------------

def _today_kst() -> date:
    tz_kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(tz_kst)
    return now_kst.date()

def d_day_status(enactment: Optional[date], reference: date) -> str:
    if enactment is None:
        return "시행일 미검출"
    delta = (enactment - reference).days
    if delta == 0:
        return "오늘 시행"
    if delta > 0:
        return f"D-{delta}"
    return "시행중"


# ---------------------------------------------------------------------------------------
# 입력 validation
# ---------------------------------------------------------------------------------------

_ARTICLE_START_PATTERN = re.compile(r'제\d+(?:의\d+)?조\b')

def validate(old_text: str, new_text: str):
    if not old_text.strip():
        return False, "구판 입력이 비어 있습니다."
    if not new_text.strip():
        return False, "신판 입력이 비어 있습니다."
    if not _ARTICLE_START_PATTERN.search(old_text):
        return False, "구판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다."
    if not _ARTICLE_START_PATTERN.search(new_text):
        return False, "신판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다."
    return True, ""


# ---------------------------------------------------------------------------------------
# Vercel 핸들러
# ---------------------------------------------------------------------------------------

def handler(request):
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
            },
            'body': '',
        }

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': True, 'message': 'POST 메서드만 지원됩니다.'}, ensure_ascii=False),
        }

    try:
        body = request.get_json()
    except Exception:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': True, 'message': '유효하지 않은 JSON 요청입니다.'}, ensure_ascii=False),
        }

    if not body:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': True, 'message': '요청 본문이 비어 있습니다.'}, ensure_ascii=False),
        }

    old_text = body.get('old_text', '')
    new_text = body.get('new_text', '')

    ok, msg = validate(old_text, new_text)
    if not ok:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': True, 'message': msg}, ensure_ascii=False),
        }

    old_articles = parse_articles(old_text)
    new_articles = parse_articles(new_text)
    old_enact = parse_enactment_date(old_text)
    new_enact = parse_enactment_date(new_text)

    today_kst = _today_kst()
    diff = compute_diff(old_articles, new_articles)

    result = {
        'diff': diff,
        'enactment': {
            'old_date': old_enact.strftime('%Y-%m-%d') if old_enact else None,
            'new_date': new_enact.strftime('%Y-%m-%d') if new_enact else None,
            'reference_date': today_kst.strftime('%Y-%m-%d'),
            'new_d_day_status': d_day_status(new_enact, today_kst),
            'old_d_day_status': d_day_status(old_enact, today_kst),
        },
    }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(result, ensure_ascii=False, indent=2),
    }
