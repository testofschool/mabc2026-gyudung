import json
import re
import traceback
from datetime import date, datetime, timezone, timedelta
from typing import Optional, Dict, List, Any, Tuple
from urllib.parse import parse_qs

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

    for line in text.splitlines():
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
                body = (m.group(4) or "").strip()
                current_lines = [body] if body else []
        else:
            if _ARTICLE_START_RE.match(stripped) or stripped.startswith("부칙"):
                content = "\n".join(current_lines).strip()
                articles[current_num] = {"title": current_title, "content": content}
                m = _ARTICLE_RE.match(stripped)
                if m:
                    current_num = _assemble_article_number(m.group(1), m.group(2))
                    current_title = m.group(3) if m.group(3) else ""
                    body = (m.group(4) or "").strip()
                    current_lines = [body] if body else []
                else:
                    current_num = None
                    current_title = None
                    current_lines = []
            else:
                current_lines.append(stripped)

    if current_num is not None:
        content = "\n".join(current_lines).strip()
        articles[current_num] = {"title": current_title, "content": content}

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
# D-day 판정 (KST)
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
# 파일 텍스트 추출 (Vercel Python 런타임에서 동작 가능한 범위)
# ---------------------------------------------------------------------------------------

def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    지원 형식:
      - .txt              → 그대로 디코딩
      - .csv              → pandas로 읽고 모든 셀을 이어붙임 (한글 인코딩 대응)
      - .xlsx / .xls     → openpyxl/pandas로 시트를 읽고 이어붙임
      - .docx            → python-docx로 문단 텍스트 추출
      - .hwp              → 현재 미지원 (별도 라이브러리 필요). 오류 반환.
    """
    low = filename.lower()

    # --- .txt ---
    if low.endswith('.txt'):
        try:
            return file_bytes.decode('utf-8'), None
        except UnicodeDecodeError:
            try:
                return file_bytes.decode('cp949'), None
            except Exception as e:
                return None, f"텍스트 파일 디코딩 실패: {e}"

    # --- .csv ---
    if low.endswith('.csv'):
        try:
            import pandas as pd
            # 한글 CSV는 보통 cp949 / euc-kr. 여러 인코딩 시도.
            for enc in ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']:
                try:
                    df = pd.read_csv(filename.encode('utf-8') if isinstance(filename, str) else b'',  # placeholder
                                     encoding=enc)
                    break
                except Exception:
                    continue
            else:
                # 파일 객체로부터 직접 읽어야 함 — 아래서 BytesIO로 처리
                pass
            # 실제 구현: BytesIO로 감싸서 읽음
            from io import BytesIO
            bio = BytesIO(file_bytes)
            texts = []
            for enc in ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']:
                try:
                    bio.seek(0)
                    df = pd.read_csv(bio, encoding=enc, dtype=str, header=None)
                    texts.append(df.fillna('').astype(str).values.flatten().tolist())
                    break
                except Exception:
                    continue
            if not texts:
                return None, "CSV 파일 읽기에 실패했습니다. 인코딩을 확인할 수 없습니다."
            flat = [str(x) for x in texts[0]]
            return "\n".join(flat), None
        except Exception as e:
            return None, f"CSV 처리 중 오류: {e}"

    # --- .xlsx / .xls ---
    if low.endswith(('.xlsx', '.xls')):
        try:
            from io import BytesIO
            bio = BytesIO(file_bytes)
            import pandas as pd
            dfs = pd.read_excel(bio, dtype=str, header=None, sheet_name=None)
            parts = []
            for sheet_name, df in dfs.items():
                parts.append(f"[시트: {sheet_name}]")
                flat = df.fillna('').astype(str).values.flatten().tolist()
                parts.extend(str(x) for x in flat)
            return "\n".join(parts), None
        except Exception as e:
            return None, f"엑셀 파일 처리 중 오류: {e}"

    # --- .docx ---
    if low.endswith('.docx'):
        try:
            from io import BytesIO
            from docx import Document
            bio = BytesIO(file_bytes)
            doc = Document(bio)
            lines = [p.text for p in doc.paragraphs]
            # 표 텍스트도 일부 포함
            for table in doc.tables:
                for row in table.rows:
                    cells = [cell.text for cell in row.cells]
                    lines.append(" | ".join(cells))
            return "\n".join(lines), None
        except Exception as e:
            return None, f"DOCX 파일 처리 중 오류: {e}"

    # --- .hwp ---
    if low.endswith('.hwp') or low.endswith('.hwpx'):
        return None, "HWP/HWPX 파일은 현재 자동 추출을 지원하지 않습니다. 텍스트를 복사하여 붙여넣기 해주세요. (HWP 파서는 별도 라이브러리가 필요하며, 현재 서비스 런타임에 설치되어 있지 않습니다.)"

    return None, f"지원하지 않는 파일 형식입니다: {filename}. 지원 형식: txt, csv, xlsx, xls, docx"


# ---------------------------------------------------------------------------------------
# WSGI application (Vercel Python 함수용)
# ---------------------------------------------------------------------------------------

def application(environ: Dict[str, Any], start_response: callable) -> List[bytes]:
    """WSGI application — Vercel Python 런타임이 /api/admrul-diff/index.py 에서 찾습니다."""

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Headers", "Content-Type, X-File-Name"),
        ("Access-Control-Allow-Methods", "POST, OPTIONS"),
    ]

    # OPTIONS (CORS preflight)
    if environ.get("REQUEST_METHOD") == "OPTIONS":
        start_response("200 OK", headers)
        return [b""]

    # POST만 허용
    if environ.get("REQUEST_METHOD") != "POST":
        status = "405 Method Not Allowed"
        body = json.dumps({"error": True, "message": "POST 메서드만 지원됩니다."}, ensure_ascii=False).encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    # 멀티파트 폼 데이터 파싱 (파일 업로드용)
    content_type = environ.get("CONTENT_TYPE", "")
    is_multipart = content_type.startswith("multipart/form-data")

    if is_multipart:
        return _handle_multipart(environ, start_response, headers)

    # 기존 JSON API (텍스트 직접 입력)
    try:
        content_length = int(environ.get("CONTENT_LENGTH", 0))
        body_bytes = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception:
        body = {}

    if not isinstance(body, dict):
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": "요청 본문이 유효한 JSON 객체가 아닙니다."}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    old_text = body.get("old_text", "")
    new_text = body.get("new_text", "")

    # validation
    ok, msg = validate(old_text, new_text)
    if not ok:
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": msg}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    # 파싱
    try:
        old_articles = parse_articles(old_text)
        new_articles = parse_articles(new_text)
        old_enact = parse_enactment_date(old_text)
        new_enact = parse_enactment_date(new_text)

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
        resp = json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        status = "500 Internal Server Error"
        resp = json.dumps({"error": True, "message": f"서버 내부 오류: {str(e)}"}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    status = "200 OK"
    body = resp.encode("utf-8")
    headers.append(("Content-Length", str(len(body))))
    start_response(status, headers)
    return [body]


def _handle_multipart(environ, start_response, headers):
    """multipart/form-data 요청 처리: old_file + new_file 또는 old_text + new_text"""
    from cgi import FieldStorage

    try:
        fs = FieldStorage(
            fp=environ["wsgi.input"],
            environ=environ,
            keep_blank_values=True,
        )
    except Exception as e:
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": f"요청 파싱 실패: {e}"}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    def get_value(name: str) -> str:
        if name not in fs:
            return ""
        field = fs[name]
        # cgi.FieldStorage가 텍스트 필드를 FieldStorage 객체로 파싱할 수 있음
        # 이 경우 .value로 접근하면 문자열을 얻음 (파일 필드는 .file에 저장됨)
        if isinstance(field, str):
            return field
        # FieldStorage 객체일 때
        if hasattr(field, 'filename') and field.filename:
            # 파일 필드: .file에서 읽음
            if hasattr(field, 'file') and field.file:
                raw = field.file.read()
                if isinstance(raw, bytes):
                    return raw.decode('utf-8', errors='replace')
                return str(raw)
            return ""
        # 텍스트 필드: .value 또는 .file에서 읽음
        if hasattr(field, 'value'):
            val = field.value
            if isinstance(val, str):
                return val
            if isinstance(val, bytes):
                return val.decode('utf-8', errors='replace')
            return str(val)
        # fallback: .file에서 읽기
        if hasattr(field, 'file') and field.file:
            raw = field.file.read()
            if isinstance(raw, bytes):
                return raw.decode('utf-8', errors='replace')
            return str(raw)
        return ""

    def get_file(name: str):
        """파일 필드에서 (bytes, filename) 반환. 없으면 (None, None)."""
        if name not in fs:
            return None, None
        field = fs[name]
        if hasattr(field, 'file') and field.file:
            raw = field.file.read()
            filename = field.filename or name
            return raw, filename
        return None, None

    old_text = get_value("old_text") if "old_text" in fs else ""
    new_text = get_value("new_text") if "new_text" in fs else ""
    old_file_bytes, old_filename = get_file("old_file")
    new_file_bytes, new_filename = get_file("new_file")

    extracted_messages = []

    # 파일 → 텍스트 추출
    if old_file_bytes and not old_text:
        text, err = extract_text_from_file(old_file_bytes, old_filename or "old_file")
        if err:
            extracted_messages.append(f"구판 파일 오류: {err}")
        if text is not None:
            old_text = text

    if new_file_bytes and not new_text:
        text, err = extract_text_from_file(new_file_bytes, new_filename or "new_file")
        if err:
            extracted_messages.append(f"신판 파일 오류: {err}")
        if text is not None:
            new_text = text

    if old_file_bytes and old_text:
        # 파일은 있으나 이미 텍스트가 있으면 스킵(텍스트 우선)
        pass
    if new_file_bytes and new_text:
        pass

    # 파일로만 구성된 경우 old_text/new_text가 비어있을 수 있음
    if not old_text.strip() and not old_file_bytes:
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": "구판 텍스트 또는 구판 파일이 필요합니다."}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    if not new_text.strip() and not new_file_bytes:
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": "신판 텍스트 또는 신판 파일이 필요합니다."}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    # 파일 관련 경고가 있으면 400으로 반환 (추출 실패 시 전체 요청 실패)
    if extracted_messages:
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": " | ".join(extracted_messages)}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    # 기존 validate + diff 파이프라인 재사용
    ok, msg = validate(old_text, new_text)
    if not ok:
        status = "400 Bad Request"
        resp = json.dumps({"error": True, "message": msg}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    try:
        old_articles = parse_articles(old_text)
        new_articles = parse_articles(new_text)
        old_enact = parse_enactment_date(old_text)
        new_enact = parse_enactment_date(new_text)

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
            "input_method": "file" if (old_file_bytes or new_file_bytes) else "text",
            "file_info": {
                "old_file": old_filename,
                "new_file": new_filename,
            },
        }
        resp = json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        status = "500 Internal Server Error"
        resp = json.dumps({"error": True, "message": f"서버 내부 오류: {str(e)}"}, ensure_ascii=False)
        body = resp.encode("utf-8")
        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    status = "200 OK"
    body = resp.encode("utf-8")
    headers.append(("Content-Length", str(len(body))))
    start_response(status, headers)
    return [body]


# Vercel이 찾을 top-level name: 'app' 또는 'application'
app = application
