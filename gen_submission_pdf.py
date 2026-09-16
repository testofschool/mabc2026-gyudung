#!/usr/bin/env python3
"""규정다름 MABC 2026 제출물 생성기: PRD PDF · 포스터 PDF · 발표 PDF."""

import os
import textwrap
from datetime import date

from fpdf import FPDF

FONT_BOLD = "/Library/Fonts/NanumSquareNeoOTF-Bd.otf"
FONT_MED = "/Library/Fonts/NanumSquareNeoOTF-Eb.otf"
FONT_REG = "/Library/Fonts/NanumSquareNeoOTF-Rg.otf"
FONT_LT = "/Library/Fonts/NanumSquareNeoOTF-Lt.otf"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submission")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "PRD"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "poster"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "presentation"), exist_ok=True)

TEAM = "강정민"
TODAY = "2026. 9. 17."
SERVICE_URL = "https://mabc-finals.vercel.app"
GITHUB_URL = "https://github.com/testofschool/mabc2026-gyudung"


# --------------------------------------------------------------------------------
# 공통 유틸
# --------------------------------------------------------------------------------

def add_ko_fonts(pdf: FPDF):
    pdf.add_font("NJ", "", FONT_REG, uni=True)
    pdf.add_font("NJ", "B", FONT_BOLD, uni=True)


def wrap_ko(text: str, width_chars: int) -> list:
    """한글 어절 기준 근사 줄바꿈."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width_chars:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def section_title(pdf: FPDF, text: str, size: int = 13, space_before: int = 10, space_after: int = 5):
    pdf.ln(space_before)
    pdf.set_font("NJ", "B", size)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, size * 0.42, text, align="L")
    pdf.ln(space_after)


def body(pdf: FPDF, text: str, size: int = 10, indent: int = 0):
    pdf.set_font("NJ", "", size)
    pdf.set_text_color(51, 51, 51)
    x0 = pdf.get_x()
    pdf.set_x(x0 + indent)
    pdf.multi_cell(pdf.w - pdf.r_margin - x0 - indent, size * 0.42, text, align="L")
    pdf.set_x(x0)


def bullet(pdf: FPDF, text: str, size: int = 10):
    pdf.set_font("NJ", "", size)
    pdf.set_text_color(51, 51, 51)
    x0 = pdf.get_x()
    pdf.cell(6, size * 0.42, "·", align="C")
    pdf.multi_cell(pdf.w - pdf.r_margin - x0 - 6, size * 0.42, text, align="L")


def table_header(pdf: FPDF, cols: list, widths: list, size: int = 10):
    pdf.set_font("NJ", "B", size)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(33, 33, 33)
    x0 = pdf.get_x()
    for c, w in zip(cols, widths):
        pdf.cell(w, size * 0.5, c, border=0, fill=True, align="C")
    pdf.ln()


def table_row(pdf: FPDF, cells: list, widths: list, size: int = 10, fill: bool = False):
    pdf.set_font("NJ", "", size)
    pdf.set_text_color(51, 51, 51)
    if fill:
        pdf.set_fill_color(248, 248, 248)
    else:
        pdf.set_fill_color(255, 255, 255)
    x0 = pdf.get_x()
    max_h = 0
    y0 = pdf.get_y()
    # 1차: 줄바꿈 필요한 셀 높이 계산
    cell_lines = []
    for c, w in zip(cells, widths):
        lines = []
        for seg in c.split("\n"):
            lines.extend(wrap_ko(seg, max(1, int((w - 4) / (size * 0.35)))))
        cell_lines.append(lines)
        h = len(lines) * size * 0.42 + 2
        max_h = max(max_h, h)
    # 셀 그리기
    for (lines, w) in zip(cell_lines, widths):
        pdf.set_xy(x0, y0)
        pdf.multi_cell(w, size * 0.42, "\n".join(lines), border=0, align="L", fill=fill)
        x0 += w
    pdf.set_xy(pdf.l_margin, y0 + max_h)


def caption(pdf: FPDF, text: str, size: int = 9):
    pdf.ln(2)
    pdf.set_font("NJ", "L", size)
    pdf.set_text_color(102, 102, 102)
    pdf.multi_cell(0, size * 0.4, text, align="L")
    pdf.ln(2)


# --------------------------------------------------------------------------------
# 1) PRD PDF
# --------------------------------------------------------------------------------

def gen_prd():
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=22)
    add_ko_fonts(pdf)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # 표지
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("NJ", "B", 26)
    pdf.set_text_color(22, 60, 120)
    pdf.multi_cell(0, 12, "규정다름", align="C")
    pdf.ln(4)
    pdf.set_font("NJ", "M", 13)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, 7, "행정규칙 신·구 조문 대조 및 시행일 D-day 자동 산출 서비스", align="C")
    pdf.ln(8)
    pdf.set_draw_color(22, 60, 120)
    pdf.set_line_width(0.4)
    y = pdf.get_y()
    pdf.line(50, y, 160, y)
    pdf.ln(8)
    pdf.set_font("NJ", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, f"팀명: {TEAM}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"작성일: {TODAY}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "MABC 2026 결선 제출용", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("NJ", "L", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"서비스 URL: {SERVICE_URL}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"GitHub: {GITHUB_URL}", align="C", new_x="LMARGIN", new_y="NEXT")

    # 본문
    pdf.add_page()
    section_title(pdf, "1. 서비스 개요")
    body(pdf, "규정다름은 행정규칙·지침·훈령·예규·요령 등 조문 단위로 제·개정되는 문서의 구판과 신판 텍스트를 입력받아, 조문별 신설·변경·삭제 내역을 대조표로 출력하고 부칙 시행일을 파싱하여 오늘 기준 D-day와 시행상태를 함께 보여주는 웹 서비스입니다.")
    body(pdf, "공무원은 행정규칙이 개정될 때마다 두 문서를 출력하여 눈으로 비교하는 수작업을 반복해 왔습니다. 규정다름은 이 과정을 자동화하여, 텍스트를 붙여넣는 것만으로 수초 내에 변경 내용과 시행 상태를 파악할 수 있게 합니다.")

    section_title(pdf, "2. 문제 정의")
    body(pdf, "행정규칙은 현장에서 지속적으로 제·개정되지만, 실무자가 개정 내용을 확인하는 방식은 여전히 두 문서를 출력하여 눈으로 비교하는 수준에 머물러 있습니다.")
    bullet(pdf, "국가법령정보센터(law.go.kr)는 법령 신·구조문 비교 기능을 제공하지만, 사용자가 구판·신판 텍스트를 직접 붙여넣어 조문 단위로 즉시 대조하고 시행일 D-day까지 한 화면에서 확인하는 방식은 아닙니다.")
    bullet(pdf, "법제처 open API(open.law.go.kr)는 개발자용 조회 기능만 제공할 뿐, 비개발자가 바로 쓸 수 있는 대조표 산출로 이어지지 않습니다.")
    bullet(pdf, "실무자는 구판·신판 텍스트를 각각 확보한 뒤 두 문서를 펼쳐놓고 조문별로 변경된 내용을 수동으로 확인하고, 별도로 해당 규정의 시행일을 조회해야 합니다.")
    bullet(pdf, "개정 빈도가 높은 기관일수록 이 부담은 커집니다.")
    caption(pdf, "※ 위 주장은 서비스의 문제 의식 설명이며, 세부 수치·이용량 등 정량 비교는 별도 출처 확인 전에는 단정하지 않습니다.")

    section_title(pdf, "3. 해결 방안")
    cols = ["기능", "설명", "기존 대비 우위"]
    widths = [32, 96, 40]
    table_header(pdf, cols, widths)
    rows = [
        ("조문 대조", "구판·신판 텍스트를 붙여넣으면 스크립트가 조항 단위로 added/modified/deleted를 자동 판정", "눈으로 비교하는 수작업 대체, 수초 내 완료"),
        ("시행일 D-day", "부칙 시행일 문구를 파싱하여 오늘(KST) 기준 D-day/시행상태를 자동 산출", "별도 조회 없이 시행 상태 즉시 확인"),
        ("스크립트 기반", "diff 판정, 시행일 파싱, D-day 계산 모두 Python 스크립트가 수행 (LLM 임의 추정 없음)", "계산 과정의 투명성·재현성 확보"),
        ("즉시 사용 가능", "API 키 없이 웹 브라우저에서 바로 사용. 로그인·회원가입 불필요", "개방형 접근성, 진입 장벽 최소화"),
    ]
    for i, r in enumerate(rows):
        table_row(pdf, r, widths, fill=(i % 2 == 0))
    caption(pdf, "표 1. 규정다름 핵심 기능 및 기존 대비 우위")

    section_title(pdf, "4. 사용 시나리오")
    body(pdf, "상황: A시청 자치행정과 주무관 B가 소관 지침의 개정 통지를 받았습니다. 구판과 신판 텍스트를 이메일로 받았습니다.")
    bullet(pdf, "주무관 B는 규정다름 웹사이트에 접속합니다. (로그인 불필요)")
    bullet(pdf, "구판 텍스트와 신판 텍스트를 각 입력란에 붙여넣습니다.")
    bullet(pdf, "[대조 실행] 버튼을 클릭합니다.")
    bullet(pdf, "수초 내에 화면에 ① 어떤 조문이 신설·변경·삭제되었는지 나타낸 대조표와 ② 해당 지침의 시행일 및 현재 시행 상태(D-n / 시행중 / 오늘 시행)가 표시됩니다.")
    bullet(pdf, "주무관 B는 변경된 조문만 빠르게 확인하고, 해당 지침이 현재 시행 중인지(또는 언제 시행 예정인지)를 별도 검색 없이 파악합니다.")
    bullet(pdf, "필요하면 [JSON 보기] 토글로 원본 계산 결과를 확인할 수 있습니다.")
    body(pdf, "전체 소요 시간: 약 30초 이내 (law.go.kr에서 동일 내용을 확인하는 경우 메뉴 탐색·별도 페이지 이동 수반).", indent=0)

    section_title(pdf, "5. 기술 아키텍처")
    cols = ["구성 요소", "기술 스택", "역할"]
    widths = [40, 56, 80]
    table_header(pdf, cols, widths)
    arch = [
        ("프론트엔드", "단일 HTML + Vanilla JS\n(CSS 변수 기반)", "사용자 입력 수신, API 호출, 결과 표 렌더링"),
        ("백엔드 API", "Python (WSGI 기반)\nVercel 서버리스", "텍스트 수신, diff 계산,\n시행일 파싱, D-day 산출, JSON 응답"),
        ("핵심 로직", "admrul-diff 스크립트\n(Python stdlib)", "조문 파싱, diff 판정, 시행일 파싱,\nD-day 계산 — 모든 계산 수행"),
        ("배포", "Vercel\n(정적 사이트 + 서버리스 함수)", "전 세계 CDN, HTTPS,\n스케일 투 제로"),
        ("데이터 저장", "없음 (무상태)", "모든 계산은 요청 시점 메모리에서 수행,\n데이터 저장하지 않음"),
    ]
    for i, r in enumerate(arch):
        table_row(pdf, r, widths, fill=(i % 2 == 0))
    caption(pdf, "표 2. 규정다름 기술 아키텍처 구성 요소")

    section_title(pdf, "6. API 상세")
    body(pdf, "엔드포인트: POST /api/admrul-diff")
    body(pdf, "요청 본문(JSON):")
    pdf.set_font("NJ", "", 9)
    pdf.set_text_color(40, 40, 40)
    req_example = '{"old_text": "구판 텍스트 (문자열)",\n "new_text": "신판 텍스트 (문자열)"}'
    x0 = pdf.get_x()
    pdf.set_x(x0 + 8)
    for line in req_example.split("\n"):
        pdf.set_x(x0 + 8)
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    body(pdf, "응답 본문(JSON) 예시:")
    pdf.set_font("NJ", "", 9)
    pdf.set_text_color(40, 40, 40)
    resp_example = '{"diff": [{"article_number": "2", "article_title": "운영시간", "judgment": "modified",\n   "old_content": "...", "new_content": "..."}],\n "enactment": {"old_date": "2026-03-01",\n   "new_date": "2026-09-15", "reference_date": "2026-09-16",\n   "new_d_day_status": "시행중", "old_d_day_status": "시행중"}}'
    for line in resp_example.split("\n"):
        pdf.set_x(x0 + 8)
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    bullet(pdf, "d_day_status 값: D-n (시행일까지 n일 남음) / 오늘 시행 / 시행중 / 시행일 미검출")
    bullet(pdf, "judgment 값: added (신설) / modified (변경) / deleted (삭제)")
    bullet(pdf, "CORS: 모든 오리진 허용 (Access-Control-Allow-Origin: *)")
    caption(pdf, "오류 응답 예시: 구판에서 조문 패턴(제N조)이 검출되지 않으면 HTTP 400 + {\"error\": true, \"message\": \"구판에서 조문 패턴(제N조)을 찾을 수 없습니다. ...\"} 형태로 반환됩니다.")

    section_title(pdf, "7. 입력 검증 및 오류 처리")
    bullet(pdf, "구판 텍스트가 비어 있으면: \"구판 입력이 비어 있습니다.\" (400 오류)")
    bullet(pdf, "신판 텍스트가 비어 있으면: \"신판 입력이 비어 있습니다.\" (400 오류)")
    bullet(pdf, "구판/신판에서 조문 패턴이 검출되지 않으면: \"행정규칙/지침 형식이 아닌 것으로 보입니다.\" (400 오류)")
    bullet(pdf, "서버 내부 오류 발생 시: \"서버 내부 오류\" (500 오류) + 에러 메시지")
    body(pdf, "모든 오류는 구조화된 JSON으로 반환되며, 프론트엔드에서 에러 박스 형태로 표시됩니다.", indent=0)

    section_title(pdf, "8. 차별화 및 경쟁 우위")
    body(pdf, "규정다름의 핵심 차별화는 '붙여넣기 즉시성'과 '시행일 D-day 자동 산출'의 결합입니다.")
    body(pdf, "국가법령정보센터는 법령 신·구조문 비교 기능을 제공하며 공식성을 갖추고 있으나, 사용자가 구판·신판 텍스트를 직접 붙여넣어 조문 단위로 즉시 대조하고시행일 D-day까지 한 화면에서 확인하는 방식은 아닙니다. 법제처 open API는 개발자용 조회 기능만 제공할 뿐, 비개발자가 바로 쓸 수 있는 대조표 산출로 이어지지 않습니다. 규정다름은 이 틈새를 메웁니다.")
    bullet(pdf, "완전성: 조문 대조 + 시행 D-day를 한 화면에서 동시에 제공")
    bullet(pdf, "접근성: 로그인·회원가입·API 키 없이 누구나 사용 가능")
    bullet(pdf, "속도: 텍스트를 붙여넣는 즉시 결과 출력 (별도 메뉴 탐색·페이지 이동 불필요)")
    bullet(pdf, "신뢰성: LLM이 아닌 스크립트가 계산 수행. 계산 과정 재현 가능")
    bullet(pdf, "행정규칙 포괄: 지침·훈령·예규·요령 등 다양한 행정규칙 형식 지원")
    bullet(pdf, "폐쇄망 대응: 핵심 계산은 Python stdlib 기반 스크립트이므로, 내부망 환경에서도 텍스트만 있으면 같은 방식 대조 가능")

    section_title(pdf, "9. 향후 발전 방향")
    bullet(pdf, "파일 업로드 지원: 텍스트 붙여넣기 외에 PDF/문서 파일 업로드로 직접 대조")
    bullet(pdf, "국가법령정보센터/open API 연동: 행정규칙 원문을 자동 조회하여 비교")
    bullet(pdf, "비교 결과 저장·공유: 대조 결과 링크를 생성하거나 PDF로 export")
    bullet(pdf, "다크 모드 지원: CSS 변수 기반 테마 전환")
    bullet(pdf, "기관별 알림: 관심 규정의 개정 발생 시 알림 (옵트인 기반)")

    section_title(pdf, "10. 팀 정보")
    cols = ["항목", "내용"]
    widths = [40, 136]
    table_header(pdf, cols, widths)
    team_rows = [
        ("팀명", TEAM),
        ("참가자", "강정민 (단독)"),
        ("플랫폼", "Hermes Agent"),
        ("서비스 URL", SERVICE_URL),
        ("GitHub", GITHUB_URL),
        ("핵심 기술", "Python (admrul-diff 스크립트), Vercel 서버리스, HTML/CSS/JS"),
    ]
    for i, r in enumerate(team_rows):
        table_row(pdf, r, widths, fill=(i % 2 == 0))

    path = os.path.join(OUT_DIR, "PRD", f"{TEAM}_PRD.pdf")
    pdf.output(path)
    size_kb = os.path.getsize(path) / 1024
    print(f"[PRD] 작성 완료: {path} ({size_kb:.0f} KB)")
    return path


# --------------------------------------------------------------------------------
# 2) 포스터 PDF (A1 세로: 594 x 841 mm)
# --------------------------------------------------------------------------------

def gen_poster():
    W, H = 594, 841  # A1 세로 (mm)
    pdf = FPDF(orientation="P", unit="mm", format=(W, H))
    pdf.set_auto_page_break(auto=False)
    add_ko_fonts(pdf)
    pdf.set_left_margin(24)
    pdf.set_right_margin(24)
    lm = pdf.l_margin
    rm = W - pdf.r_margin
    content_w = rm - lm

    pdf.add_page()
    # 배경 톤
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(0, 0, W, H, "F")

    # 상단 띠
    pdf.set_fill_color(22, 60, 120)
    pdf.rect(0, 0, W, 60, "F")
    pdf.set_xy(lm, 16)
    pdf.set_font("NJ", "B", 36)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(content_w, 20, "규정다름", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(lm, pdf.get_y() + 2)
    pdf.set_font("NJ", "L", 14)
    pdf.set_text_color(200, 215, 240)
    pdf.cell(content_w, 8, "행정규칙 신·구 조문 대조 및 시행일 D-day 자동 산출", align="C")

    # 태그 라인
    pdf.set_xy(lm, 78)
    pdf.set_font("NJ", "M", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(content_w, 7, "두 문서를 붙여넣기만 하면, 조문별 대조표 + 시행일 D-day가 수초 만에 나옵니다.", align="C")

    # 핵심 수치
    pdf.set_xy(lm, 108)
    pdf.set_draw_color(22, 60, 120)
    pdf.set_line_width(0.3)
    y0 = pdf.get_y()
    pdf.line(lm, y0, rm, y0)
    pdf.ln(6)

    stat_items = [
        ("붙여넣기 즉시\n대조 완료", "본문만 넣으면\n조문별 신설·변경·삭제 판정"),
        ("시행일 D-day\n자동 산출", "부칙 날짜를 파싱해\n오늘 기준 D-n / 시행중 표시"),
        ("로그인·API키\n불필요", "웹 브라우저에서\n바로 사용 가능"),
    ]
    n = len(stat_items)
    slot_w = content_w / n
    x = lm
    for i, (big, small) in enumerate(stat_items):
        pdf.set_xy(x + 4, pdf.get_y())
        pdf.set_font("NJ", "B", 12)
        pdf.set_text_color(22, 60, 120)
        for line in big.split("\n"):
            pdf.set_x(x + 4)
            pdf.cell(slot_w - 8, 8, line, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        pdf.ln(2)
        pdf.set_font("NJ", "", 10)
        pdf.set_text_color(90, 90, 90)
        for line in small.split("\n"):
            pdf.set_x(x + 4)
            pdf.cell(slot_w - 8, 6, line, align="C", new_x="LMARGIN", new_y="NEXT")
        x += slot_w

    pdf.ln(10)

    # 사용 방법 (왼쪽) + 아키텍처 (오른쪽) 나란히
    col_w = content_w / 2 - 4
    left_x = lm
    right_x = lm + col_w + 8
    y = pdf.get_y() + 4

    # 왼쪽 카드
    pdf.set_xy(left_x, y)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(220, 225, 235)
    pdf.set_line_width(0.3)
    card_h = 150
    pdf.rect(left_x, y, col_w, card_h, "DF")
    pdf.set_xy(left_x + 8, y + 6)
    pdf.set_font("NJ", "B", 13)
    pdf.set_text_color(22, 60, 120)
    pdf.cell(col_w - 16, 8, "3단계로 바로 사용", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    steps = [
        ("① 입력", "구판 텍스트와 신판 텍스트를\n각 입력란에 붙여넣기"),
        ("② 실행", "[대조 실행] 버튼 클릭\n(샘플 불러오기로도 가능)"),
        ("③ 결과", "조문별 대조표 + 시행일 D-day\n표 즉시 표시, JSON 보기도 가능"),
    ]
    yy = pdf.get_y() + 4
    for title, desc in steps:
        pdf.set_xy(left_x + 8, yy)
        pdf.set_font("NJ", "B", 11)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(col_w - 16, 7, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(left_x + 10)
        pdf.set_font("NJ", "", 10)
        pdf.set_text_color(80, 80, 80)
        for line in desc.split("\n"):
            pdf.set_x(left_x + 10)
            pdf.cell(col_w - 18, 6, line, new_x="LMARGIN", new_y="NEXT")
        yy = pdf.get_y() + 3
    pdf.set_y(y + card_h + 8)

    # 오른쪽 카드: 아키텍처
    y = pdf.get_y()
    pdf.set_xy(right_x, y)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(220, 225, 235)
    card_h2 = 150
    pdf.rect(right_x, y, col_w, card_h2, "DF")
    pdf.set_xy(right_x + 8, y + 6)
    pdf.set_font("NJ", "B", 13)
    pdf.set_text_color(22, 60, 120)
    pdf.cell(col_w - 16, 8, "경량 아키텍처", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    arch_items = [
        "프론트: 단일 HTML + Vanilla JS",
        "백엔드: Python WSGI, Vercel 서버리스",
        "핵심 로직: admrul-diff 스크립트(Python stdlib)",
        "계산은 모두 스크립트가 수행, LLM 임의 추정 없음",
        "데이터 저장 없음 (무상태)",
    ]
    yy = pdf.get_y() + 4
    for a in arch_items:
        pdf.set_x(right_x + 10)
        pdf.set_font("NJ", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.cell(col_w - 18, 6, "· " + a, new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y + card_h2 + 8)

    # 하단:_diff 예시 표
    pdf.set_y(pdf.get_y() + 6)
    pdf.set_draw_color(22, 60, 120)
    pdf.set_line_width(0.3)
    y0 = pdf.get_y()
    pdf.line(lm, y0, rm, y0)
    pdf.ln(6)
    pdf.set_xy(lm, pdf.get_y())
    pdf.set_font("NJ", "B", 13)
    pdf.set_text_color(22, 60, 120)
    pdf.cell(content_w, 8, "실동작 예시: 시립도서관 자료실 운영 지침 (구판 2026.3.1. → 신판 2026.9.15.)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    ex_cols = ["구분", "조문", "구판 내용", "신판 내용"]
    ex_widths = [18, 56, 180, 180]
    table_header(pdf, ex_cols, ex_widths, size=9)
    ex_rows = [
        ("변경", "제2조(운영시간)",
         "자료실의 운영시간은 오전 9시부터 오후 6시까지로 한다.",
         "자료실의 운영시간은 오전 9시부터 오후 9시까지로 한다."),
        ("변경", "제4조(자료 대출)",
         "이용자는 1인당 5권의 자료를 14일간 대출할 수 있다.",
         "이용자는 1인당 7권의 자료를 21일간 대출할 수 있다."),
        ("삭제", "제5조(음식물 반입 금지)",
         "자료실 내에는 음료를 포함한 일체의 음식물을 반입할 수 없다.",
         "(삭제)"),
        ("신설", "제6조(디지털 자료실 운영)",
         "(신설)",
         "디지털 자료실은 회원증을 발급받은 이용자에 한하여\n1일 2시간 이내로 이용할 수 있다."),
    ]
    for i, r in enumerate(ex_rows):
        table_row(pdf, r, ex_widths, size=9, fill=(i % 2 == 0))

    # 시행일 D-day 표
    pdf.ln(4)
    pdf.set_font("NJ", "B", 11)
    pdf.set_text_color(22, 60, 120)
    pdf.cell(content_w, 7, "시행 D-day", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    dd_cols = ["항목", "구판", "신판"]
    dd_widths = [50, 78, 78]
    table_header(pdf, dd_cols, dd_widths, size=9)
    dd_rows = [
        ("시행일", "2026-03-01", "2026-09-15"),
        ("기준일자", "2026-09-17", "2026-09-17"),
        ("시행상태", "시행중", "시행중"),
    ]
    for i, r in enumerate(dd_rows):
        table_row(pdf, r, dd_widths, size=9, fill=(i % 2 == 0))

    # 하단 메타
    pdf.set_y(H - 40)
    pdf.set_draw_color(220, 225, 235)
    pdf.set_line_width(0.2)
    y0 = pdf.get_y()
    pdf.line(lm, y0, rm, y0)
    pdf.ln(4)
    pdf.set_xy(lm, pdf.get_y())
    pdf.set_font("NJ", "L", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(content_w, 6, f"팀명: {TEAM}  |  플랫폼: Hermes Agent", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(lm + content_w / 2 - 70)
    pdf.cell(140, 6, f"서비스: {SERVICE_URL}", align="C", new_x="LMARGIN", new_y="NEXT")

    path = os.path.join(OUT_DIR, "poster", f"{TEAM}_포스터.pdf")
    pdf.output(path)
    size_kb = os.path.getsize(path) / 1024
    print(f"[포스터] 작성 완료: {path} ({size_kb:.0f} KB / A1 세로 {W}x{H}mm)")
    return path


# --------------------------------------------------------------------------------
# 3) 발표자료 PDF
# --------------------------------------------------------------------------------

def gen_presentation():
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    add_ko_fonts(pdf)
    pdf.set_left_margin(22)
    pdf.set_right_margin(22)
    lm = pdf.l_margin
    content_w = pdf.w - lm - pdf.r_margin

    def slide(num, title, body_lines=None, note=None):
        pdf.add_page()
        # 헤더 바
        pdf.set_fill_color(22, 60, 120)
        pdf.rect(lm, 14, content_w, 22, "F")
        pdf.set_xy(lm + 4, 16)
        pdf.set_font("NJ", "B", 12)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(40, 8, f"규정다름  {num:02d}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_xy(lm + 4, pdf.get_y() + 1)
        pdf.set_font("NJ", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(content_w - 4, 9, title, new_x="LMARGIN", new_y="NEXT")

        yy = pdf.get_y() + 8
        pdf.set_xy(lm, yy)
        if body_lines:
            pdf.set_font("NJ", "", 12)
            pdf.set_text_color(51, 51, 51)
            for bl in body_lines:
                if bl == "---":
                    pdf.ln(4)
                    continue
                if bl.startswith(">>"):
                    # 강조 하위 항목
                    pdf.set_x(lm + 8)
                    pdf.set_font("NJ", "M", 11)
                    pdf.set_text_color(70, 70, 70)
                    pdf.multi_cell(content_w - 8, 7, bl[2:].strip(), align="L")
                elif bl.startswith("•"):
                    pdf.set_x(lm + 6)
                    pdf.set_font("NJ", "", 11)
                    pdf.set_text_color(51, 51, 51)
                    pdf.multi_cell(content_w - 6, 7, bl, align="L")
                else:
                    pdf.set_x(lm + 2)
                    pdf.set_font("NJ", "", 12)
                    pdf.set_text_color(51, 51, 51)
                    pdf.multi_cell(content_w - 4, 7, bl, align="L")
                pdf.ln(1)
        if note:
            pdf.set_y(pdf.get_y() + 6)
            pdf.set_draw_color(220, 225, 235)
            pdf.set_line_width(0.2)
            y0 = pdf.get_y()
            pdf.line(lm, y0, rm := pdf.w - pdf.r_margin, y0)
            pdf.ln(2)
            pdf.set_x(lm)
            pdf.set_font("NJ", "L", 9)
            pdf.set_text_color(130, 130, 130)
            pdf.multi_cell(content_w, 5, note, align="L")

    # 01 표지
    slide(
        1,
        "행정규칙 신·구 조문 대조 및\n시행일 D-day 자동 산출 서비스",
        [
            "규정다름",
            "---",
            ">> 팀명: 강정민  |  플랫폼: Hermes Agent",
            ">> 서비스: https://mabc-finals.vercel.app",
            ">> GitHub: https://github.com/testofschool/mabc2026-gyudung",
            "---",
            f">> MABC 2026 결선  ·  {TODAY}",
        ],
        note="로그인·회원가입·API 키 없이 웹 브라우저에서 바로 사용 가능한 경량 웹 서비스.",
    )

    # 02 문제 정의
    slide(
        2,
        "왜 이 서비스가 필요한가",
        [
            "• 행정규칙·지침은 현장에서 계속 제·개정되지만,",
            "  실무자의 개정 확인 방식은 여전히 두 문서를 출력해",
            "  눈으로 비교하는 수준에 머물러 있습니다.",
            "---",
            "• 국가법령정보센터(law.go.kr)는 법령 신·구조문 비교",
            "  기능을 제공하지만, 붙여넣기 즉시 대조는 아닙니다.",
            "• 법제처 open API(open.law.go.kr)는 개발자용 조회",
            "  기능만 제공 — 비개발자가 바로 쓰기 어렵습니다.",
            "---",
            ">> 구판·신판 텍스트만 준비돼 있으면, 조문별 변경 내용과",
            "   시행 D-day를 별도 조회 없이 한눈에 보고 싶습니다.",
        ],
        note="정량적 이용량·건수 비교는 별도 출처 확인 전에는 단정하지 않습니다.",
    )

    # 03 서비스 개요
    slide(
        3,
        "규정다름은 무엇을 하는가",
        [
            "• 구판 · 신판 텍스트를 붙여넣으면 조문 단위로",
            "  신설(added) · 변경(modified) · 삭제(deleted)를 판정",
            "• 부칙 시행일을 파싱해 오늘(KST) 기준 D-day/시행상태 산출",
            "• 로그인 · 회원가입 · API 키 없이 바로 사용",
            "• 계산 전 과정은 Python 스크립트가 수행 (LLM 임의 추정 없음)",
        ],
        note="admrul-diff 스크립트(st scripts/admrul_diff.py)가 모든 diff·시행일·D-day 계산을 수행합니다.",
    )

    # 04 핵심 기능 표
    slide(
        4,
        "핵심 기능",
        [
            ">> 기능 · 설명 · 기존 대비 우위",
        ],
        note=None,
    )
    # 본문을 표로 별도 페이지
    pdf.add_page()
    pdf.set_font("NJ", "B", 14)
    pdf.set_text_color(22, 60, 120)
    pdf.set_xy(lm, 18)
    pdf.cell(content_w, 9, "핵심 기능 및 기존 대비 우위", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    cols = ["기능", "설명", "기존 대비 우위"]
    widths = [34, 94, 48]
    table_header(pdf, cols, widths, size=10)
    rows = [
        ("조문 대조", "구판·신판 텍스트를 붙여넣으면 스크립트가\n조항 단위로 added/modified/deleted를 자동 판정", "눈으로 비교하는\n수작업 대체\n수초 내 완료"),
        ("시행일 D-day", "부칙 시행일 문구를 파싱하여 오늘(KST)\n기준 D-day/시행상태를 자동 산출", "별도 조회 없이\n시행 상태 즉시 확인"),
        ("스크립트 기반", "diff 판정, 시행일 파싱, D-day 계산 모두\nPython 스크립트가 수행 (LLM 임의 추정 없음)", "계산 과정의\n투명성·재현성 확보"),
        ("즉시 사용 가능", "API 키 없이 웹 브라우저에서 바로 사용.\n로그인·회원가입 불필요.", "개방형 접근성\n진입 장벽 최소화"),
    ]
    for i, r in enumerate(rows):
        table_row(pdf, r, widths, size=10, fill=(i % 2 == 0))
    pdf.ln(4)
    pdf.set_font("NJ", "L", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(content_w, 5, "표. 규정다름 핵심 기능 및 기존 대비 우위", align="L")

    # 05 사용 시나리오
    slide(
        5,
        "사용 시나리오",
        [
            "상황: A시청 자치행정과 주무관 B가 소관 지침의",
            "개정 통지를 받고, 구판·신판 텍스트를 이메일로 받음.",
            "---",
            "• 규정다름 웹사이트에 접속 (로그인 불필요)",
            "• 구판 텍스트와 신판 텍스트를 각 입력란에 붙여넣기",
            "• [대조 실행] 버튼 클릭",
            "• 수초 내에 화면에 ① 조문별 대조표",
            "  (신설·변경·삭제)와 ② 시행일 및 시행 상태 표시",
            "• 필요하면 [JSON 보기] 토글로 원본 결과 확인",
            "---",
            ">> 전체 소요 시간 약 30초 이내",
        ],
        note="데모 페이지(https://mabc-finals.vercel.app)의 '샘플 불러오기'로 동일 시나리오를 바로 체험할 수 있습니다.",
    )

    # 06 기술 아키텍처
    slide(
        6,
        "기술 아키텍처",
        [
            "• 프론트엔드: 단일 HTML + Vanilla JS (CSS 변수 기반)",
            "  → 사용자 입력 수신, API 호출, 결과 표 렌더링",
            "• 백엔드 API: Python (WSGI 기반), Vercel 서버리스",
            "  → 텍스트 수신, diff 계산, 시행일 파싱, D-day 산출, JSON 응답",
            "• 핵심 로직: admrul-diff 스크립트 (Python stdlib)",
            "  → 조문 파싱, diff 판정, 시행일 파싱, D-day 계산",
            "• 배포: Vercel (정적 사이트 + 서버리스 함수) — HTTPS, CDN",
            "• 데이터 저장: 없음 (무상태)",
        ],
        note="모든 계산은 요청 시점 메모리에서 수행되며, 데이터가 저장되지 않습니다.",
    )

    # 07 API
    slide(
        7,
        "API 상세",
        [
            "POST /api/admrul-diff",
            "---",
            "요청 본문(JSON):",
            '  { "old_text": "구판 텍스트", "new_text": "신판 텍스트" }',
            "---",
            "응답 본문(JSON):",
            '  { "diff": [...], "enactment": {',
            '      "old_date", "new_date", "reference_date",',
            '      "new_d_day_status", "old_d_day_status" } }',
            "---",
            "• 판단값(d_day_status): D-n / 오늘 시행 / 시행중 / 시행일 미검출",
            "• 판정값(judgment): added · modified · deleted",
            "• CORS: 모든 오리진 허용 (Access-Control-Allow-Origin: *)",
        ],
        note="모든 오류는 구조화된 JSON으로 반환됩니다. 예: 조문 패턴이 없으면 HTTP 400 + 에러 메시지.",
    )

    # 08 입력 검증/오류
    slide(
        8,
        "입력 검증 및 오류 처리",
        [
            "• 구판 텍스트가 비어 있으면:",
            '  "구판 입력이 비어 있습니다." (HTTP 400)',
            "• 신판 텍스트가 비어 있으면:",
            '  "신판 입력이 비어 있습니다." (HTTP 400)',
            "• 구판/신판에서 조문 패턴이 검출되지 않으면:",
            '  "행정규칙/지침 형식이 아닌 것으로 보입니다." (HTTP 400)',
            "• 서버 내부 오류 발생 시:",
            '  "서버 내부 오류" (HTTP 500) + 에러 메시지',
            "---",
            ">> 모든 오류는 구조화된 JSON으로 반환되며",
            "   프론트엔드에서 에러 박스 형태로 표시됩니다.",
        ],
        note="규칙: diff 판정·시행일/D-day 계산은 반드시 스크립트에서만 수행합니다. LLM 임의 추정 금지.",
    )

    # 09 차별화
    slide(
        9,
        "차별화 및 경쟁 우위",
        [
            "규정다름의 핵심 차별화는",
            "'붙여넣기 즉시성' + '시행일 D-day 자동 산출'의 결합",
            "---",
            "• 완전성: 조문 대조 + 시행 D-day를 한 화면에서 제공",
            "• 접근성: 로그인·회원가입·API 키 없이 누구나 사용 가능",
            "• 속도: 텍스트 붙여넣기 즉시 결과 출력",
            "• 신뢰성: LLM이 아닌 스크립트가 계산 수행, 재현 가능",
            "• 행정규칙 포괄: 지침·훈령·예규·요령 등 다양한 형식 지원",
            "• 폐쇄망 대응: 핵심 계산은 Python stdlib 기반 —",
            "  내부망에서도 텍스트만 있으면 같은 방식 대조 가능",
        ],
        note="국가법령정보센터·법제처 open API의 강점을 부정하는 것이 아니라, 그 틈새를 메우는 보완 도구로 포지셔닝합니다.",
    )

    # 10 향후 계획
    slide(
        10,
        "향후 발전 방향",
        [
            "• 파일 업로드 지원: PDF/문서 파일 업로드로 직접 대조",
            "• 국가법령정보센터/open API 연동:",
            "  행정규칙 원문을 자동 조회하여 비교",
            "• 비교 결과 저장·공유:",
            "  대조 결과 링크 생성 또는 PDF export",
            "• 다크 모드 지원: CSS 변수 기반 테마 전환",
            "• 기관별 알림:",
            "  관심 규정의 개정 발생 시 알림 (옵트인 기반)",
        ],
        note="현재는 무상태 경량 서비스이며, 향후 기능은 우선순위에 따라 단계적으로 도입합니다.",
    )

    # 11 감사합니다
    slide(
        11,
        "감사합니다",
        [
            "규정다름 — 행정규칙 신·구 조문 대조 및 시행일 D-day 자동 산출",
            "---",
            f"서비스: {SERVICE_URL}",
            f"GitHub: {GITHUB_URL}",
            f"팀명: {TEAM}  |  플랫폼: Hermes Agent",
            f"연락처: gangjeongmin23@gmail.com",
            "---",
            "데모: 홈페이지 '샘플 불러오기'로 바로 체험 가능",
        ],
        note=None,
    )

    path = os.path.join(OUT_DIR, "presentation", f"{TEAM}_발표자료.pdf")
    pdf.output(path)
    size_kb = os.path.getsize(path) / 1024
    print(f"[발표자료] 작성 완료: {path} ({size_kb:.0f} KB)")
    return path


if __name__ == "__main__":
    print(f"규정다름 제출물 생성 시작 (팀명: {TEAM}, 날짜: {TODAY})")
    print("=" * 60)
    gen_prd()
    gen_poster()
    gen_presentation()
    print("=" * 60)
    print("모든 제출물 PDF 생성 완료.")
    for sub in ["PRD", "poster", "presentation"]:
        d = os.path.join(OUT_DIR, sub)
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            print(f"  {sub}/{f}  ({os.path.getsize(p)/1024:.0f} KB)")
