#!/usr/bin/env python3
"""
ordin-gap: 지자체 조례의 상위 표준규정 준용 배제 및 특례 조항 대조(gap 분석) 전용 도구

순수 표준 JSON만 stdout으로 출력한다. 그 외 어떤 텍스트도 stdout에 내지 않는다.
"""
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_ASSETS_DIR = _SCRIPT_DIR.parent / "assets"

DEFAULT_UPPER = str(_ASSETS_DIR / "upper_sample_standard.txt")
DEFAULT_SAMPLES = {
    "하늘시": str(_ASSETS_DIR / "ordin_sample_haneul.txt"),
    "바다군": str(_ASSETS_DIR / "ordin_sample_bada.txt"),
    "들녘시": str(_ASSETS_DIR / "ordin_sample_deulnyeok.txt"),
}

ORDIN_ARTICLE_RE = re.compile(r"제(\d+조(?:\s*조의\d+)?)\s*(?:제\s*)?(.+?)(?:(?:조|항|호|목)\s*\d*|$)")
ORDIN_TITLE_CLEAN_RE = re.compile(r"[\s\(\)]+")
QUOTED_REGULATION_RE = re.compile(r"「([^}」]+)」")


# ---------------------------------------------------------------------------
# 오류 헬퍼
# ---------------------------------------------------------------------------
def emit_error(kind: str, message: str) -> None:
    """표준 에러 JSON을 stdout으로 출력하고 비정상 종료한다."""
    out: Dict[str, Any] = {
        "error": True,
        "kind": kind,
        "message": message,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(1)


# ---------------------------------------------------------------------------
# 파일 로드 및 기본 검증
# ---------------------------------------------------------------------------
def load_file(path: str) -> str:
    """파일을 읽어 텍스트를 반환한다. 존재하지 않으면 오류를 낸다."""
    if not os.path.isfile(path):
        emit_error("file_not_found", f"입력 파일 경로를 찾을 수 없습니다: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def detect_articles(text: str) -> List[Tuple[str, str]]:
    """
    조문 텍스트에서 (조문번호, 정규화된제목) 목록을 추출한다.

    제목 추출 규칙 (우선순위):
      1) '제N조(제목)' 형태이면 괄호 안 텍스트만 제목으로 추출한다.
         본문 내용(예: '이 조례는 ...')이 제목으로 들어가지 않도록 분리한다.
      2) 괄호가 없으면 '제N조' 뒤 첫 설명 경계(' 이 ', ' 다만' 등) 이전까지를 제목으로 본다.
    조문이 하나도 검출되지 않으면 빈 목록을 반환한다.
    """
    articles: List[Tuple[str, str]] = []

    for m in re.finditer(
        r"제(\d+(?:조(?:의\d+|제\d+항)?)?)\b(.+?)(?=제\d+(?:조(?:의\d+|제\d+항)?)?\b|$)",
        text,
        re.DOTALL,
    ):
        num_raw = m.group(1).replace(" ", "")
        rest = m.group(2)

        # 1) 괄호 안 제목 우선 추출: '제N조(제목)' 또는 '제N조(제목) ...'
        pm = re.match(r"\s*\(([^)]*)\)\s*", rest)
        if pm:
            raw_title = pm.group(1).strip()
            if raw_title:
                articles.append((num_raw, normalize_title(raw_title)))
                continue

        # 2) 괄호 없는 경우: 첫 자연 경계까지 잘라내어 제목으로 간주
        #    제목/본문 경계로 자주 쓰이는 표지로 분할한다.
        title = re.split(
            r"\s+(?:이 |다만|다만,|즉|즉,)",
            rest,
        )[0].strip()
        # 그래도 남는 괄호/구분자가 있으면 추가 정리
        title = title.split("(가상")[0].strip()
        title = re.sub(r"[,·\s]+$", "", title).strip()
        if title:
            articles.append((num_raw, normalize_title(title)))

    return articles


def normalize_title(title: str) -> str:
    """
    조문 제목을 비교용 정규형으로 만든다.
    - 연속 공백 → 단일 공백
    - 괄호 앞뒤 공백 정리
    - '지급 구분' / '지급구분' 같은 변형은 그대로 두되 공백 정규화만 수행
      (예: '여비의 지급구분' ↔ '여비의 지급 구분'이 동일 매핑되도록)
    """
    t = re.sub(r"\s+", " ", title).strip()
    # 괄호 앞뒤 공백 정리: ' ( ' → '(', ' ) ' → ')'
    t = re.sub(r"\s*\(\s*", " (", t)
    t = re.sub(r"\s*\)\s*", ") ", t)
    t = t.strip()
    return t


# ---------------------------------------------------------------------------
# 상위규정 특정 (3단계 우선순위)
# ---------------------------------------------------------------------------
def identify_regulation(
    ordinance_text: str,
    all_ordinances: Dict[str, str],
) -> Dict[str, Any]:
    """
    A. 상위규정 자동 특정 (3단계 우선순위)
    반환: {"name": ..., "method": "title"|"body"|"whole", "confidence": ...}
    """
    # ① 준용 조문 제목에 인용된 상위규정 특정
    title_matches: List[str] = []
    for line in ordinance_text.splitlines():
        if "준용" in line and "조" in line:
            hits = QUOTED_REGULATION_RE.findall(line)
            title_matches.extend(hits)

    if title_matches:
        counter = Counter(title_matches)
        name = counter.most_common(1)[0][0].strip()
        return {"name": name, "method": "title", "confidence": "high"}

    # ② 준용 조문 본문 내 인용 빈도가 가장 높은 상위규정 특정
    body_matches: List[str] = []
    in_junyon = False
    for line in ordinance_text.splitlines():
        if "준용" in line:
            in_junyon = True
        if in_junyon:
            hits = QUOTED_REGULATION_RE.findall(line)
            body_matches.extend(hits)
            # 준용 조문이 끝났다고 볼 수 있는 지점(다음 조 제목 등)에서 리셋
            if re.match(r"제\d+조", line.strip()) and "준용" not in line:
                in_junyon = False

    if body_matches:
        counter = Counter(body_matches)
        name = counter.most_common(1)[0][0].strip()
        return {"name": name, "method": "body", "confidence": "medium"}

    # ③ 전체 조문 내 언급 빈도가 가장 높은 상위규정 특정
    whole_matches: List[str] = QUOTED_REGULATION_RE.findall(ordinance_text)
    if whole_matches:
        counter = Counter(whole_matches)
        name = counter.most_common(1)[0][0].strip()
        return {"name": name, "method": "whole", "confidence": "low"}

    # 모두 실패 → 빈 이름
    return {"name": "", "method": "none", "confidence": "none"}


# ---------------------------------------------------------------------------
# 준용 배제 조항 탐지
# ---------------------------------------------------------------------------
def detect_exclusion_clauses(ordinance_text: str) -> List[Dict[str, Any]]:
    """
    '준용하지 아니한다' 등 배제 조항을 탐지한다.

    준용 배제 조문 탐색 규칙:
      - '제12조제3항'처럼 항이 포함된 경우, 먼저 '제12조'를 찾고
        그 내부에서 항(③항 / 제3항 등) 표기를 추출하여 배제 대상 원문을
        정확히 확보한다.
      - 배제 대상 원문 확보는 이 함수에서 수행하고,
        상위규정 대조(found/not_found)는 compute_gap에서 담당한다.

    반환: [{"article": "제7조", "excluded": [원문텍스트,...], "raw": "..."}]
    excluded는 원문에서 추출한 조문·항 표기 문자열을 그대로 담는다.
    """
    clauses: List[Dict[str, Any]] = []

    # 준용 조문(제N조 ... 준용) 단위로 순회
    for m in re.finditer(
        r"(제\d+조(?:\s*조의\d+)?)\s*(.+?)(?=제\d+조\b|$)",
        ordinance_text,
        re.DOTALL,
    ):
        article_num = re.sub(r"^제", "", m.group(1)).replace(" ", "")
        body = m.group(2)
        if "준용" not in body:
            continue

        excluded: List[str] = []

        # 1) 본문 내에서 '제N조' 단위(조 제목)를 먼저 찾는다.
        #    이렇게 찾은 각 조문 블록 안에서 항 표기를 추출하여
        #    배제 대상 여부를 판정한다.
        for art_m in re.finditer(
            r"(제\d+조(?:\s*조의\d+)?)\s*\(\?\s*\)", body
        ):
            art_cand = art_m.group(1).replace(" ", "")
            art_start = art_m.start()
            rest = body[art_start + len(art_m.group(0)):]
            # 다음 조문 시작 경계를 찾아 블록 범위를 잡는다
            next_art = re.search(r"제\d+조(?:\s*조의\d+)?", rest)
            if next_art:
                block = rest[: next_art.start()]
            else:
                block = rest

            # 항 포함 조문(예: 제12조제3항)이면,
            # 먼저 '제12조' 본문 블록에서 항 표기를 찾는다.
            # 항 표기는 '③항', '제3항', '제3항의', '항 제3' 등 여러 형태.
            if re.match(r"^\d+조(제\d+항)?$", art_cand) or re.match(r"^\d+조의\d+$", art_cand):
                simple_hang = re.search(
                    r"(제\d+항|③항|②항|①항|[1-9]항의?)", block
                )
                if simple_hang:
                    hang_raw = simple_hang.group(0)
                    ctx_start = max(0, simple_hang.start() - 120)
                    ctx_end = min(len(block), simple_hang.end() + 120)
                    ctx = block[ctx_start:ctx_end]
                    if any(k in ctx for k in ("준용하지", "적용하지", "제외", "배제")):
                        if art_cand.startswith("제"):
                            original = f"제{art_cand.lstrip('제')}{hang_raw}"
                        else:
                            original = f"제{art_cand}{hang_raw}"
                        if original not in excluded:
                            excluded.append(original)

            # 일반적인 배제 대상 조문(제X조의2, 제X조제Y항 등)은
            # 기존 방식으로도 확보
            pos = art_m.start()
            ctx = body[max(0, pos - 120): pos + 120]
            if any(k in ctx for k in ("준용하지", "적용하지", "제외", "배제")):
                if art_cand not in excluded:
                    excluded.append(art_cand)

        # 2) 쉼표/및/와로 이어지는 배제 목록도 보완적으로 추출
        junyong_idx = body.find("준용")
        if junyong_idx >= 0:
            ctx_body = body[max(0, junyong_idx - 200): junyong_idx + 200]
            for em in re.finditer(r"제(\d+조(?:의\d+|제\d+항)?)", ctx_body):
                cand = em.group(1).replace(" ", "")
                if cand in excluded:
                    continue
                near = ctx_body[max(0, em.start() - 100): em.end() + 100]
                if any(k in near for k in ("준용하지", "적용하지", "제외", "배제")):
                    excluded.append(cand)

        if excluded:
            clauses.append({
                "article": f"제{article_num}",
                "excluded": sorted(set(excluded)),
                "raw": body.strip()[:200],
            })

    return clauses


# ---------------------------------------------------------------------------
# Gap 분석 (상위규정 대조)
# ---------------------------------------------------------------------------
def compute_gap(
    exclusion_clauses: List[Dict[str, Any]],
    upper_articles: List[Tuple[str, str]],
) -> List[Dict[str, Any]]:
    """
    준용 배제 조항이 있으면 상위규정과 대조하여 found / not_found 판별.
    없으면 '제외 없음'.

    항 포함 배제 대상(예: '12조제3항') 처리:
      1) 먼저 조 단위(예: '12조')로 상위규정 존재 여부를 확인한다.
      2) 조가 존재하면 해당 조문 내 항 표기(예: '제3항')를 추출하여
         'found'로 처리하고 원문을 병기한다.
      3) 조 자체가 상위규정에 없을 때만 'not_found'로 처리한다.
    """
    if not exclusion_clauses:
        return [{"status": "제외 없음"}]

    results: List[Dict[str, Any]] = []
    upper_nums = {n for n, _ in upper_articles}

    for clause in exclusion_clauses:
        for excl in clause["excluded"]:
            # excl 예: '12조제3항', '15조', '8조의2', '23조'
            # 조 번호(바탕)와 항 표기로 분리
            art_match = re.match(r"^(\d+조(?:의\d+)?)(.*)$", excl)
            if art_match:
                base_art = art_match.group(1)   # '12조', '15조', '8조의2'
                hang_part = art_match.group(2)  # '제3항' 등, 없으면 ''
            else:
                base_art = excl
                hang_part = ""

            found = base_art in upper_nums
            excluded_article = f"제{base_art}"
            if hang_part:
                excluded_article += hang_part

            results.append({
                "source_article": clause["article"],
                "excluded_article": excluded_article,
                "status": "found" if found else "not_found",
            })

    return results


# ---------------------------------------------------------------------------
# 입력 검증 (4종 예외)
# ---------------------------------------------------------------------------
def validate_inputs(
    ordinance_paths: List[str],
    upper_path: Optional[str],
) -> Tuple[List[str], Optional[str]]:
    """
    입력된 파일 경로를 검증하고, 문제가 있으면 emit_error로 종료한다.
    정상이면 (조례경로목록, 상위규정경로)를 반환.
    """
    # ① 조례 파일이 1개인 경우 → 단일 파일 오류
    if len(ordinance_paths) == 1:
        emit_error(
            "single_file_error",
            f"조례 파일은 2개 이상 9개 이하를 입력해야 합니다. 현재 1개만 입력되었습니다: {ordinance_paths[0]}",
        )

    # ② 조례 파일이 9개를 초과하는 경우 → 입력 개수 초과 오류
    if len(ordinance_paths) > 9:
        emit_error(
            "too_many_files_error",
            f"조례 파일은 최대 9개까지 입력 가능합니다. 현재 {len(ordinance_paths)}개가 입력되었습니다.",
        )

    # ③ 존재하지 않는 파일 경로 → 파일 미존재 오류
    for p in ordinance_paths:
        if not os.path.isfile(p):
            emit_error("file_not_found", f"입력 파일 경로를 찾을 수 없습니다: {p}")

    # 상위규정 경로: 첨부되었으면 사용, 없으면 기본 fallback
    if upper_path is not None:
        if not os.path.isfile(upper_path):
            emit_error("file_not_found", f"상위규정 파일 경로를 찾을 수 없습니다: {upper_path}")
        upper_resolved = upper_path
    else:
        upper_resolved = DEFAULT_UPPER
        if not os.path.isfile(upper_resolved):
            emit_error(
                "file_not_found",
                f"기본 상위규정 파일을 찾을 수 없습니다: {upper_resolved}. 상위규정 파일을 함께 첨부해주세요.",
            )

    return ordinance_paths, upper_resolved


def validate_article_detection(ordinance_paths: List[str], texts: Dict[str, str]) -> None:
    """
    모든 조례 텍스트에서 조문이 1개 이상 검출되지 않으면 오류.
    """
    for name, text in texts.items():
        arts = detect_articles(text)
        if not arts:
            emit_error(
                "no_article_detected_error",
                f"파일 '{name}'({ordinance_paths[list(texts.keys()).index(name)]})에서 조문을 하나도 검출하지 못했습니다. "
                f"조문 형식이 아닌 비규격 텍스트가 입력된 것으로 보입니다.",
            )


# ---------------------------------------------------------------------------
# 메인 파이프라인
# ---------------------------------------------------------------------------
def run_pipeline(
    ordinance_paths: List[str],
    upper_path: Optional[str],
    municipality_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    전체 분석 파이프라인.
    """
    # --- 입력 검증 ---
    ordinance_paths, upper_resolved = validate_inputs(ordinance_paths, upper_path)

    # --- 파일 로드 ---
    ordinance_texts: Dict[str, str] = {}
    for i, p in enumerate(ordinance_paths):
        if municipality_names and i < len(municipality_names):
            name = municipality_names[i]
        else:
            # 파일명에서 지자체명 추정 (확장자 제거, 디렉토리 제거)
            stem = os.path.splitext(os.path.basename(p))[0]
            name = stem
        text = load_file(p)
        ordinance_texts[name] = text

    upper_text = load_file(upper_resolved)

    # --- 조문 검출 ---
    ordinance_articles: Dict[str, List[Tuple[str, str]]] = {}
    for name, text in ordinance_texts.items():
        arts = detect_articles(text)
        if not arts:
            # 이미 validate_article_detection에서 걸러지므로 여기선 안심
            pass
        ordinance_articles[name] = arts

    upper_articles = detect_articles(upper_text)

    # --- ④ 조문 미검출 검증 ---
    validate_article_detection(ordinance_paths, ordinance_texts)

    # --- 지자체명 결정 (파일명 기반 fallback) ---
    if municipality_names is None:
        municipality_names = list(ordinance_texts.keys())

    # --- [A] 상위규정 자동 특정 ---
    # ①②③을 첫 번째 조례 기준으로 판단 (가장 풍부할 것으로 가정)
    primary_name = municipality_names[0]
    primary_text = ordinance_texts[primary_name]
    regulation = identify_regulation(primary_text, ordinance_texts)

    # 모든 조례에 대해 상위규정 특정 결과를 집계 (info 목적)
    all_regulations: Dict[str, Dict[str, Any]] = {}
    for name, text in ordinance_texts.items():
        all_regulations[name] = identify_regulation(text, ordinance_texts)

    # 최종 상위규정명: 모든 조례에서 동일하게 지목된 것이 있으면 그것을, 없으면 첫 번째 기준
    reg_names = [r["name"] for r in all_regulations.values() if r["name"]]
    final_reg_name = regulation["name"] if regulation["name"] else ""
    if not final_reg_name and reg_names:
        # 최빈값
        c = Counter(reg_names)
        final_reg_name = c.most_common(1)[0][0]

    # --- [C] 준용 제외 및 Gap 분석 ---
    all_exclusions: List[Dict[str, Any]] = []
    gap_results: List[Dict[str, Any]] = []
    for name, text in ordinance_texts.items():
        clauses = detect_exclusion_clauses(text)
        for c in clauses:
            c["municipality"] = name
        all_exclusions.extend(clauses)
        gaps = compute_gap(clauses, upper_articles)
        gap_results.extend(gaps)

    gap_summary = {
        "exclusion_clauses": all_exclusions,
        "gap_against_upper": gap_results if gap_results else [{"status": "제외 없음"}],
    }

    # --- 지자체명 매핑 (핵심: 조례 파일과 지자체명 대응) ---
    name_map: Dict[str, str] = {}
    for i, p in enumerate(ordinance_paths):
        if municipality_names and i < len(municipality_names):
            name_map[p] = municipality_names[i]
        else:
            stem = os.path.splitext(os.path.basename(p))[0]
            name_map[p] = stem

    return {
        "regulation_identified": {
            "name": final_reg_name,
            "method": regulation["method"],
            "confidence": regulation["confidence"],
            "per_ordinance": all_regulations,
        },
        "gap": gap_summary,
        "municipalities": municipality_names,
        "ordinance_files": ordinance_paths,
        "upper_regulation_file": upper_resolved,
        "upper_articles_count": len(upper_articles),
    }


# ---------------------------------------------------------------------------
# 진입점
# ---------------------------------------------------------------------------
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="ordin-gap: 지자체 조례의 상위 표준규정 준용 배제 및 특례 조항 대조(gap 분석) 전용 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용법:
  python ordin_gap.py 조례1.txt 조례2.txt ... [--upper 상위규정.txt]
  python ordin_gap.py                                                    # 데모 모드 (기본 샘플 4개 자동 로드)
  python ordin_gap.py 조례1.txt 조례2.txt --names "하늘시" "바다군"        # 지자체명 직접 지정
        """,
    )
    parser.add_argument(
        "ordinances",
        nargs="*",
        help="비교할 조례 텍스트 파일 경로 (2~9개)",
    )
    parser.add_argument(
        "--upper",
        default=None,
        help="상위규정 텍스트 파일 경로 (미지정 시 upper_sample_standard.txt 자동 fallback)",
    )
    parser.add_argument(
        "--names",
        nargs="*",
        default=None,
        help="각 조례 파일에 대응할 지자체명 (조례 파일 개수와 일치해야 함)",
    )

    args = parser.parse_args()

    # --- 데모 모드: 조례 파일이 하나도 없을 때 ---
    if not args.ordinances:
        # 기본 샘플 4개를 자동 로드
        sample_paths = [
            DEFAULT_SAMPLES["하늘시"],
            DEFAULT_SAMPLES["바다군"],
            DEFAULT_SAMPLES["들녘시"],
            DEFAULT_UPPER,
        ]
        # 상위규정은 마지막 파일로 분리
        upper_path = sample_paths[-1]  # upper_sample_standard.txt
        ordinance_paths = sample_paths[:-1]  # 조례 3개
        municipality_names = ["하늘시", "바다군", "들녘시"]
        # 데모 모드임을 결과에 표시
        result = run_pipeline(ordinance_paths, upper_path, municipality_names)
        result["demo_mode"] = True
        result["note"] = "입력 파일이 없어 기본 샘플 4개(하늘시·바다군·들녘시·표준규정)를 자동 로드한 데모 모드입니다."
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 지자체명 개수 검증
    if args.names is not None and len(args.names) != len(args.ordinances):
        emit_error(
            "name_count_mismatch_error",
            f"--names 로 지정한 지자체명 개수({len(args.names)})가 조례 파일 개수({len(args.ordinances)})와 일치하지 않습니다.",
        )

    result = run_pipeline(args.ordinances, args.upper, args.names if args.names else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
