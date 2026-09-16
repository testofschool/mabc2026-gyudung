#!/usr/bin/env python3
"""
numbers_check.py — 초안 텍스트와 원본 텍스트 두 파일을 받아,
초안에 등장한 숫자·날짜·금액·직접인용문을 전부 추출해 원본과 대조하고
일치/근사/불일치로 판정한 결과를 JSON 으로 stdout 에 출력한다.

표준 라이브러리만 사용: re, json, sys, os, math
"""

import re
import json
import sys
import os
import math


# ---------------------------------------------------------------------------
# 1. 추출 정규식
# ---------------------------------------------------------------------------

QUOTE_RE = re.compile(
    r"""["'\u2018\u2019\u201c\u201d](?P<content>[\s\S]*?)["'\u2018\u2019\u201c\u201d]|「(?P<cjk1>[\s\S]*?)」|『(?P<cjk2>[\s\S]*?)』"""
)

DATE_RE = re.compile(
    r"""
    (?P<y>\d{4})\s*[년]\s*
    (?P<m>\d{1,2})\s*[월]\s*
    (?P<d>\d{1,2})\s*[일]?
    |
    (?P<y2>\d{4})\s*[-/.]\s*
    (?P<m2>\d{1,2})\s*[-/.]\s*
    (?P<d2>\d{1,2})
    |
    (?P<y3>\d{4})\s*년(?!\s*\d)
    """,
    re.VERBOSE,
)

FRACTION_RE = re.compile(r"100\s*분의\s*(\d+(?:\.\d+)?)")
PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")

MONEY_UNIT_RE = re.compile(
    r"""
    (?P<val>\d+(?:,\d{3})*(?:\.\d+)?)\s*
    (?P<unit>억|만|원)
    """,
    re.VERBOSE,
)

PURE_NUM_RE = re.compile(
    r"""
    (?P<num2>\d{1,3}(?:,\d{3})+)
    |
    (?P<num3>\d+(?:\.\d+)?)
    """,
    re.VERBOSE,
)

# 명·건·개·원·억·만 등 단위어가 붙은 숫자. 금액 단위어(억/원/만)는 별도 money 처리가 우선하고,
# 여기서는 비금액 단위어 숫자를 'number' 타입으로 추출한다.
UNIT_NUM_RE = re.compile(
    r"""
    (?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s*
    (?P<unit>명|건|개|차례|번|대|가지|곳|개월|회|권)
    """,
    re.VERBOSE,
)

ARTICLE_RE = re.compile(r"제\s*(\d+)\s*조")


# ---------------------------------------------------------------------------
# 2. 정규화 헬퍼
# ---------------------------------------------------------------------------

def _collapse_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _parse_krw(raw: str) -> float:
    """금액 문자열을 원 단위 값으로 파싱.

    지원 형식:
      - 단일 단위: "3.5억", "1,000만원", "10,000,000원"
      - 복합: "3억 5천만원", "3억 5000만원", "4억 5천만원", "3.5억 2천만원"
    """
    raw = raw.strip()

    # ---- 복합: "N억 M만[원]" (M에 '천' 포함 가능, 예: "5천만원") ----
    # 전략: "N억" + "만" 앞의 나머지(M)를 하나로 잡고, M에 '천'이 있으면 1000배.
    m = re.match(
        r"""
        ^\s*
        (?P<eok>\d+(?:\.\d+)?)\s*억\s*
        (?P<man_part>.+?)\s*만\s*
        (?P<won>원)?\s*$
        """,
        raw,
        re.VERBOSE,
    )
    if m:
        eok = float(m.group("eok").replace(",", ""))
        man_part = (m.group("man_part") or "").strip()
        man = 0.0
        if "천" in man_part:
            # "5천" → 5000, "1,200천" → 1,200,000
            num_str = man_part.replace("천", "").replace(",", "").strip()
            if num_str:
                man = float(num_str) * 1000
        else:
            man = float(man_part.replace(",", ""))
        return eok * 100_000_000 + man * 10_000

    # ---- 단일 금액 단위어: "N원", "N억", "N만" ----
    parts = []
    for m2 in MONEY_UNIT_RE.finditer(raw):
        num_str = m2.group("val").replace(",", "")
        unit = m2.group("unit")
        num = float(num_str)
        if unit == "억":
            parts.append(num * 100_000_000)
        elif unit == "만":
            parts.append(num * 10_000)
        else:
            parts.append(num)
    if parts:
        return sum(parts)

    return None


def normalize_krw(raw: str) -> tuple:
    """호환용 래퍼: (원값, raw). 금액은 _parse_krw 로 처리."""
    val = _parse_krw(raw)
    return (val, raw) if val is not None else (None, raw)


def normalize_number(raw: str):
    """쉼표 제거한 float 값 반환."""
    return float(raw.replace(",", ""))


def normalize_date(raw: str) -> str:
    """절대 날짜를 ISO YYYY-MM-DD 로 정규화. 실패 시 None."""
    m = DATE_RE.search(raw)
    if not m:
        return None
    y = m.group("y") or m.group("y2") or m.group("y3")
    mo = m.group("m") or m.group("m2")
    d = m.group("d") or m.group("d2")
    if not (y and mo and d):
        return None
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


def normalize_percent(raw: str) -> float:
    """'60%' → 0.6, '100분의 60' → 0.6. 그 외 패턴이면 None."""
    fm = FRACTION_RE.search(raw)
    if fm:
        return float(fm.group(1)) / 100.0
    pm = PERCENT_RE.search(raw)
    if pm:
        return float(pm.group(1)) / 100.0
    return None


def decimal_places(raw: str) -> int:
    """문자열 표현상 소수점 이하 자리수. 없으면 0."""
    s = raw.replace(",", "")
    if "." in s:
        return len(s.split(".")[-1])
    return 0


def _eok_decimal_places(raw: str) -> int:
    """초안 raw 에서 전체 금액(만원 단위 복합 포함)의 '억 단위' 소수 정밀도.

    예: '13억' → 0, '3.5억' → 1, '3억 5천만원' → 1, '8억 4천만원' → 1,
    '12억 7천만원' → 1.
    억이 아예 없거나 파싱 실패면 0 으로 둔다.
    """
    val = _parse_krw(raw)
    if val is None:
        return 0
    eok = val / 100_000_000.0
    s = str(eok).rstrip("0").rstrip(".")
    if "." in s:
        return len(s.split(".")[-1])
    return 0


def _money_approx_equal(orig_val: float, draft_raw: str, draft_val: float) -> bool:
    """원본 금액을 '억 단위 정밀도' 관점에서 반올림/절사해 초안과 같아지는지.

    예: 원본 12억 7천만원(원본 정규값 1,270,000,000) vs 초안 '13억'
        → 12.7억을 억 단위 소수점 0자리로 반올림 → 13억 → 근사.
    """
    p = _eok_decimal_places(draft_raw)
    factor = 10 ** p
    orig_eok = orig_val / 100_000_000.0
    draft_eok = draft_val / 100_000_000.0
    r = round(orig_eok * factor) / factor
    t = math.floor(orig_eok * factor) / factor
    return (abs(r - draft_eok) < 1e-9) or (abs(t - draft_eok) < 1e-9)


def round_or_trunc_equal(orig_val: float, draft_raw: str, draft_val: float) -> bool:
    """원본 값을 초안의 정밀도로 반올림 OR 절사 → 초안 값과 같아지는지."""
    p = decimal_places(draft_raw)
    if p == 0:
        r = int(round(orig_val))
        t = int(math.floor(orig_val))
        return (r == draft_val) or (t == draft_val)
    factor = 10 ** p
    r = round(orig_val * factor) / factor
    t = math.floor(orig_val * factor) / factor
    return (abs(r - draft_val) < 1e-9) or (abs(t - draft_val) < 1e-9)


# ---------------------------------------------------------------------------
# 3. 추출 엔진
# ---------------------------------------------------------------------------

EXCLUDE_SMALL_THRESHOLD = 100


def extract_quotes(lines):
    """각 줄에서 인용문 추출."""
    results = []
    for i, line in enumerate(lines, start=1):
        for m in QUOTE_RE.finditer(line):
            content = m.group("content") or m.group("cjk1") or m.group("cjk2")
            if content is None or content.strip() == "":
                continue
            norm = _collapse_space(content)
            results.append({
                "type": "quote",
                "raw": content,
                "normalized": norm,
                "line": i,
            })
    return results


def extract_dates(lines):
    """연도 포함 절대 날짜 추출. 'YYYY년' 단독(연도만)도 추출한다."""
    results = []
    for i, line in enumerate(lines, start=1):
        for m in DATE_RE.finditer(line):
            y = m.group("y") or m.group("y2") or m.group("y3")
            mo = m.group("m") or m.group("m2")
            d = m.group("d") or m.group("d2")
            if not y:
                continue
            if mo and d:
                iso = normalize_date(m.group(0))
                if iso is None:
                    continue
            else:
                iso = y  # standalone year
            results.append({
                "type": "date",
                "raw": m.group(0),
                "normalized": iso,
                "line": i,
            })
    return results


def extract_money_and_numbers(lines):
    """금액(money)·일반숫자(number)·% 를 한 번에 추출.

    반환: (추출리스트, 제외카운트 dict)
    제외카운트: article_number, denominator, small_standalone
    """
    extracted = []
    excl = {"article_number": 0, "denominator": 0, "small_standalone": 0}

    for i, line in enumerate(lines, start=1):
        processed_regions = []

        def mark_processed(start, end):
            processed_regions.append((start, end))

        def is_processed(pos):
            for s, e in processed_regions:
                if s <= pos < e:
                    return True
            return False

        # ---- 100분의 N (% 추출, 앞의 100은 분모 제외) ----
        for m in FRACTION_RE.finditer(line):
            if is_processed(m.start()):
                continue
            mark_processed(*m.span())
            val = normalize_percent(m.group(0))
            if val is not None:
                extracted.append({
                    "type": "percent",
                    "raw": m.group(0),
                    "normalized": val,
                    "line": i,
                    "draft_str": m.group(0),
                })
            excl["denominator"] += 1

        # ---- N% ----
        for m in PERCENT_RE.finditer(line):
            if is_processed(m.start()):
                continue
            mark_processed(*m.span())
            val = normalize_percent(m.group(0))
            if val is not None:
                extracted.append({
                    "type": "percent",
                    "raw": m.group(0),
                    "normalized": val,
                    "line": i,
                    "draft_str": m.group(0),
                })

        # ---- 복합 금액 "N억 M만[원]" (M에 천 포함 가능) ----
        for m in re.finditer(
            r"""
            (?P<eok>\d+(?:\.\d+)?)\s*억\s*
            (?P<man_part>.+?)\s*만\s*
            (?P<won>원)?
            """,
            line,
            re.VERBOSE,
        ):
            if is_processed(m.start()):
                continue
            mark_processed(*m.span())
            eok = float(m.group("eok").replace(",", ""))
            man_part = (m.group("man_part") or "").strip()
            man = 0.0
            if "천" in man_part:
                num_str = man_part.replace("천", "").replace(",", "").strip()
                if num_str:
                    man = float(num_str) * 1000
            else:
                man = float(man_part.replace(",", ""))
            val = eok * 100_000_000 + man * 10_000
            extracted.append({
                "type": "money",
                "raw": m.group(0),
                "normalized": val,
                "line": i,
                "draft_str": m.group(0),
            })

        # ---- 단일 금액 단위어 "N원", "N억", "N만" ----
        for m in MONEY_UNIT_RE.finditer(line):
            if is_processed(m.start()):
                continue
            mark_processed(*m.span())
            val = _parse_krw(m.group(0))
            if val is None:
                continue
            extracted.append({
                "type": "money",
                "raw": m.group(0),
                "normalized": val,
                "line": i,
                "draft_str": m.group(0),
            })

        # ---- 조문번호 "제N조" 제외 처리 ----
        for m in ARTICLE_RE.finditer(line):
            excl["article_number"] += 1

        # ---- 단위어 붙은 숫자 (명·건·개 등) ----
        for m in UNIT_NUM_RE.finditer(line):
            if is_processed(m.start()):
                continue
            mark_processed(*m.span())
            raw_num = m.group("num").replace(",", "")
            val = float(raw_num)
            extracted.append({
                "type": "number",
                "raw": m.group(0),
                "normalized": val,
                "line": i,
                "draft_str": m.group(0),
                "unit": m.group("unit"),
            })

        # ---- 일반 숫자 (단위어 없는 순수 수치) ----
        for m in PURE_NUM_RE.finditer(line):
            num = m.group("num2") or m.group("num3")
            if num is None or is_processed(m.start()):
                continue
            mark_processed(*m.span())
            cleaned = num.replace(",", "")
            val = float(cleaned)
            is_meaningful = (
                val >= EXCLUDE_SMALL_THRESHOLD
                or "." in cleaned
                or "," in num
            )
            if is_meaningful:
                extracted.append({
                    "type": "number",
                    "raw": num,
                    "normalized": val,
                    "line": i,
                    "draft_str": num,
                    "unit": None,
                })
            else:
                excl["small_standalone"] += 1

    return extracted, excl


def extract_all(lines):
    """한 문서에서 모든 엔티티 추출."""
    quotes = extract_quotes(lines)
    dates = extract_dates(lines)
    others, excl = extract_money_and_numbers(lines)
    return quotes + dates + others, excl


# ---------------------------------------------------------------------------
# 4. 대조 판정
# ---------------------------------------------------------------------------

def find_best_original(ent, orig_entities, used_indices=None):
    """같은 type 의 원본 엔티티 중 가장 잘 대응하는 것을 찾는다.

    반환: (원본엔티티 or None, verdict, orig_index or None)
    orig_index는 매칭된 원본 엔티티의 orig_entities 내 인덱스.
    used_indices: number 타입에서 이미 매칭에 쓰인 원본 인덱스를 제외하는 집합.
    """
    import datetime as _dt
    typ = ent["type"]

    if typ == "quote":
        draft_norm = ent["normalized"]
        for i, o in enumerate(orig_entities):
            if o["type"] != "quote":
                continue
            if draft_norm in o["normalized"]:
                return (o, "match", i)
        return (None, "mismatch", None)

    if typ == "date":
        draft_norm = ent["normalized"]
        # 완전 일치 우선
        for i, o in enumerate(orig_entities):
            if o["type"] != "date":
                continue
            if o["normalized"] == draft_norm:
                return (o, "match", i)
        # standalone year: 원본의 어떤 날짜에도 그 연도가 있으면 대응
        if len(draft_norm) == 4 and draft_norm.isdigit():
            for i, o in enumerate(orig_entities):
                if o["type"] != "date":
                    continue
                if o["normalized"].startswith(draft_norm):
                    return (o, "match", i)
        # 완전일치/연도매치 모두 없으면: 원본 date 중 가장 가까운 날짜를 mismatch 로 채움
        best = None
        best_idx = None
        best_dist = None
        draft_ts = _date_to_timestamp(draft_norm)
        for i, o in enumerate(orig_entities):
            if o["type"] != "date":
                continue
            o_ts = _date_to_timestamp(o["normalized"])
            if draft_ts is None or o_ts is None:
                continue
            d = abs(o_ts - draft_ts)
            if best is None or d < best_dist:
                best = o
                best_idx = i
                best_dist = d
        if best is not None:
            return (best, "mismatch", best_idx)
        return (None, "mismatch", None)

    # 원본에 같은 type 이 아예 없으면 "원본에 없음"
    if not any(o["type"] == typ for o in orig_entities):
        return (None, "missing_in_original", None)

    def _unused_candidates():
        """같은 type 의 미사용 원본 엔티티 (인덱스, 엔티티) 목록."""
        cands = []
        for i, o in enumerate(orig_entities):
            if o["type"] != typ:
                continue
            if used_indices is not None and i in used_indices:
                continue
            cands.append((i, o))
        return cands

    # 정규화값 완전 일치 우선 (미사용 원본만 대상)
    for i, o in _unused_candidates():
        if abs(o["normalized"] - ent["normalized"]) < 1e-9:
            return (o, "match", i)

    # 완전 일치 없으면 근사 검사 (type 별 정밀도 반영, 미사용 원본만)
    if typ == "money":
        for i, o in _unused_candidates():
            if _money_approx_equal(o["normalized"], ent["raw"], ent["normalized"]):
                return (o, "approx", i)
    elif typ in ("percent", "number"):
        for i, o in _unused_candidates():
            if round_or_trunc_equal(o["normalized"], ent["raw"], ent["normalized"]):
                return (o, "approx", i)

    # 미사용 원본 후보가 하나도 없으면 원본에 없음
    cands = _unused_candidates()
    if not cands:
        return (None, "missing_in_original", None)

    # 근사/완전일치 모두 실패한 뒤: 가장 가까운 미사용 원본과 mismatch
    if typ == "money":
        best_idx, best_o = min(cands, key=lambda io: abs(io[1]["normalized"] - ent["normalized"]))
        return (best_o, "mismatch", best_idx)

    if typ == "number":
        draft_unit = ent.get("unit")
        unit_cands = [(i, o) for i, o in cands if o.get("unit") == draft_unit]
        if not unit_cands:
            return (None, "missing_in_original", None)
        # 완전 일치 우선
        for i, o in unit_cands:
            if abs(o["normalized"] - ent["normalized"]) < 1e-9:
                return (o, "match", i)
        # 가장 가까운 같은-단위 원본과 mismatch (오차 크기 무관)
        best_idx, best_o = min(unit_cands, key=lambda io: abs(io[1]["normalized"] - ent["normalized"]))
        return (best_o, "mismatch", best_idx)

    if typ == "percent":
        best_idx, best_o = min(cands, key=lambda io: abs(io[1]["normalized"] - ent["normalized"]))
        return (best_o, "mismatch", best_idx)

    return (None, "mismatch", None)


def _date_to_timestamp(iso_or_year: str):
    """ISO(YYYY-MM-DD) 혹은 연도(YYYY) 문자열을 datetime으로 변환.
    연도만 있으면 해당 연도 1월 1일로 간주."""
    import datetime as _dt
    if iso_or_year is None:
        return None
    s = iso_or_year.strip()
    try:
        if len(s) == 4 and s.isdigit():
            return _dt.datetime(int(s), 1, 1).timestamp()
        parts = s.split("-")
        if len(parts) == 3:
            return _dt.datetime(int(parts[0]), int(parts[1]), int(parts[2])).timestamp()
    except (ValueError, OverflowError):
        return None
    return None


# ---------------------------------------------------------------------------
# 5. 메인
# ---------------------------------------------------------------------------

def build_result(original_path, draft_path):
    with open(original_path, encoding="utf-8") as f:
        orig_lines = f.read().splitlines()
    with open(draft_path, encoding="utf-8") as f:
        draft_lines = f.read().splitlines()

    orig_entities, _orig_excl = extract_all(orig_lines)
    draft_entities, draft_excl = extract_all(draft_lines)

    rows = []
    summary_counts = {
        "date": {"draft": 0, "match": 0, "approx": 0, "mismatch": 0, "missing": 0},
        "money": {"draft": 0, "match": 0, "approx": 0, "mismatch": 0, "missing": 0},
        "number": {"draft": 0, "match": 0, "approx": 0, "mismatch": 0, "missing": 0},
        "percent": {"draft": 0, "match": 0, "approx": 0, "mismatch": 0, "missing": 0},
        "quote": {"draft": 0, "match": 0, "approx": 0, "mismatch": 0, "missing": 0},
    }

    excluded_total = (
        draft_excl["article_number"] + draft_excl["denominator"] + draft_excl["small_standalone"]
    )

    used_indices = set()
    for ent in draft_entities:
        typ = ent["type"]
        summary_counts[typ]["draft"] += 1

        # number, money 모두 원본 1회용(1:1 매칭) 적용
        used_arg = used_indices if typ in ("number", "money") else None
        o_ent, verdict, orig_index = find_best_original(ent, orig_entities, used_arg)

        row = {
            "type": typ,
            "draft_value": ent["raw"],
            "draft_line": ent["line"],
            "draft_raw": ent["raw"],
            "normalized": ent["normalized"],
            "verdict": verdict,
        }
        if o_ent is not None:
            row["original_value"] = o_ent["raw"]
            row["original_line"] = o_ent["line"]
            row["original_raw"] = o_ent["raw"]
            row["original_normalized"] = o_ent["normalized"]
        else:
            row["original_value"] = None
            row["original_line"] = None
            row["original_raw"] = None
            row["original_normalized"] = None

        if verdict == "match":
            summary_counts[typ]["match"] += 1
        elif verdict == "approx":
            summary_counts[typ]["approx"] += 1
        elif verdict == "missing_in_original":
            summary_counts[typ]["missing"] += 1
        else:
            summary_counts[typ]["mismatch"] += 1

        if typ in ("number", "money") and o_ent is not None and orig_index is not None:
            used_indices.add(orig_index)

        rows.append(row)

    by_type = {}
    for typ in ["date", "money", "number", "percent", "quote"]:
        c = summary_counts[typ]
        by_type[typ] = {
            "draft": c["draft"],
            "match": c["match"],
            "approx": c["approx"],
            "mismatch": c["mismatch"],
            "missing": c["missing"],
        }

    result = {
        "status": "ok",
        "files": {
            "original": os.path.basename(original_path),
            "draft": os.path.basename(draft_path),
        },
        "summary": {
            "draft_total": len(draft_entities),
            "excluded": excluded_total,
            "by_type": by_type,
            "excluded_breakdown": {
                "article_number": draft_excl["article_number"],
                "denominator": draft_excl["denominator"],
                "small_standalone": draft_excl["small_standalone"],
            },
        },
        "rows": rows,
    }
    return result


def main():
    if len(sys.argv) != 3:
        err = {
            "status": "error",
            "error": "usage: python numbers_check.py <원본.txt> <초안.txt>",
            "code": 2,
        }
        print(json.dumps(err, ensure_ascii=False, indent=2))
        sys.exit(2)

    original_path = sys.argv[1]
    draft_path = sys.argv[2]

    if not os.path.isfile(original_path):
        err = {
            "status": "error",
            "error": f"원본 파일을 찾을 수 없음: {original_path}",
            "code": 1,
        }
        print(json.dumps(err, ensure_ascii=False, indent=2))
        sys.exit(1)

    if not os.path.isfile(draft_path):
        err = {
            "status": "error",
            "error": f"초안 파일을 찾을 수 없음: {draft_path}",
            "code": 1,
        }
        print(json.dumps(err, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        result = build_result(original_path, draft_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception as e:
        err = {
            "status": "error",
            "error": f"처리 중 예외: {e}",
            "code": 1,
        }
        print(json.dumps(err, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
