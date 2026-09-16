#!/usr/bin/env python3
"""
규정다름 — A1 세로 프로덕션 포스터 v3 (강정민_포스터.pdf)
- 판형: A1 세로 594x841mm, 여백 상30/하24/좌우24
- 폰트: NanumSquareNeoOTF (Regular/Bold) 임베딩 (fpdf add_font, OTF CFF 지원)
- 팔레트: 남색 테마 (#19376E, #2A4D8F, #3E6BB0), 배경 #F4F6FB, 카드 흰색
- 구성: 상단 밴드 → 스텝 3카드 → 특징 2x2 → ICP → 하단 라인 + URL
"""
from fpdf import FPDF
import os

FD = "/Users/felix/Library/Fonts"
FONT_BOLD = os.path.join(FD, "NanumSquareNeoOTF-Bd.otf")
FONT_REG   = os.path.join(FD, "NanumSquareNeoOTF-Rg.otf")

# 팔레트 (RGB 0-255)
NAVY      = (25, 55, 110)
NAVY2     = (42, 77, 143)
NAVY3     = (62, 107, 176)
BG        = (244, 246, 251)
CARD      = (255, 255, 255)
TEXT      = (26, 31, 43)
MUTED     = (90, 100, 120)
TAG       = (180, 200, 230)
WHITE     = (255, 255, 255)
CARD_LINE = (215, 222, 236)
FEAT_BAR  = (62, 107, 176)
FEAT_BG   = (247, 249, 252)

# 판형
W, H = 594, 841  # A1 세로 mm
ML, MR, MT, MB = 24, 24, 30, 24
CW = W - ML - MR  # 546

OUT = "/Users/felix/mabc-finals/강정민_포스터.pdf"

class Poster(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format=(W, H))
        self.add_font("NS", "", FONT_REG)
        self.add_font("NS", "B", FONT_BOLD)
        self.set_auto_page_break(False)

    # 편의: 중앙 정렬 텍스트 (multi_line 지원)
    def ctext(self, x, y, w, h, s, font, size, color, align="C"):
        self.set_xy(x, y)
        self.set_font(font, size)
        self.set_text_color(*color)
        if "\n" in s:
            self.set_xy(x, y)
            self.multi_cell(w, h, s, align=align)
        else:
            self.set_xy(x, y)
            self.cell(w, h, s, align=align)

pdf = Poster()
pdf.add_page()

# ================= 상단 밴드 =================
band_h = 190
pdf.set_fill_color(*NAVY)
pdf.rect(0, H - band_h, W, band_h, style="F")

# 태그
pdf.ctext(0, H - 34, W, 8, "MABC 2026 결선  ·  팀명 강정민", "NS", "B", 12, TAG, align="C")

# 메인 타이틀
pdf.ctext(0, H - 62, W, 24, "규정다름", "NS", "B", 72, WHITE, align="C")

# 타이틀 아래 강조선
pdf.set_draw_color(*NAVY3)
pdf.set_line_width(2.2)
y_line = H - 72
pdf.line(W/2 - 50, y_line, W/2 + 50, y_line)

# 부제목
pdf.ctext(0, H - 92, W, 9, "행정규칙 신·구 조문 대조 및\n시행일 D-day 자동 산출 서비스", "NS", "", 20, TAG, align="C")

# 밴드 하단 경계선
pdf.set_draw_color(*NAVY3)
pdf.set_line_width(0.6)
pdf.line(ML, H - band_h, W - MR, H - band_h)

# ================= 콘텐츠 =================
y = H - band_h - 16

# 섹션 제목: 입력→처리→출력
pdf.set_fill_color(*NAVY)
pdf.set_text_color(*NAVY)
pdf.set_font("NS", "B", 22)
pdf.cell(0, 12, "입력  →  처리  →  출력", align="C")
y -= 14

# 스텝 카드 3개
steps = [
    ("STEP 1", "텍스트\n붙여넣기", "구판·신판 텍스트를\n각 입력란에 붙여넣기"),
    ("STEP 2", "대조\n실행", "[대조 실행] 버튼 클릭\n(수초 소요, 로그인 불필요)"),
    ("STEP 3", "결과\n확인", "신·구 조문 대조표\n+ 시행 D-day 표 즉시 확인"),
]
card_h = 60
gap = 8
card_w = (CW - 2*gap) / 3
x0 = ML
card_y = y - card_h

for i, (num, title, desc) in enumerate(steps):
    x = x0 + i*(card_w + gap)
    # 카드 배경
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*CARD_LINE)
    pdf.set_line_width(0.5)
    pdf.round_rect(x, card_y, card_w, card_h, 3, style="DF")
    # 상단 색상 바
    pdf.set_fill_color(*NAVY2)
    pdf.rect(x, card_y + card_h - 6, card_w, 6, style="F")
    # 번호 원
    r = 8
    cx = x + card_w/2
    cy = card_y + card_h - 18
    pdf.set_fill_color(*NAVY)
    pdf.circle(cx, cy, r, style="F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("NS", "B", 12)
    pdf.set_xy(cx - 6, cy - 4)
    pdf.cell(12, 8, num.split()[1], align="C")
    # 제목
    pdf.set_text_color(*NAVY)
    pdf.set_font("NS", "B", 18)
    ty2 = card_y + card_h - 34
    for j, line in enumerate(title.split("\n")):
        pdf.set_xy(x, ty2 - j*7)
        pdf.cell(card_w, 7, line, align="C")
    # 설명
    pdf.set_text_color(*MUTED)
    pdf.set_font("NS", "", 11)
    dy = card_y + card_h - 50
    for j, line in enumerate(desc.split("\n")):
        pdf.set_xy(x, dy - j*5.2)
        pdf.cell(card_w, 5.2, line, align="C")

y = card_y - 12

# 섹션 제목: 핵심 특징
pdf.set_text_color(*NAVY)
pdf.set_font("NS", "B", 22)
pdf.cell(0, 12, "핵심 특징", align="C")
y -= 14

features = [
    ("조문 대조",
     "구판·신판 텍스트를 붙여넣으면\n스크립트가 조항 단위로\nadded / modified / deleted를\n자동 판정합니다."),
    ("시행일 D-day",
     "부칙의 시행일 문구를 파싱하여\n오늘(KST) 기준 D-day /\n시행상태를 자동 산출합니다."),
    ("스크립트 기반",
     "diff 판정, 시행일 파싱, D-day 계산\n모두 Python 스크립트가 수행.\nLLM이 임의로 추정하지 않습니다."),
    ("즉시 사용 가능",
     "API 키 없이 웹 브라우저에서\n바로 사용 가능.\n로그인·회원가입 불필요."),
]
cols, rows = 2, 2
feat_w = (CW - 6) / cols
feat_h = 62
feat_gap = 6
fx0 = ML + 3
fy0 = y - feat_h

for idx, (ftitle, fdesc) in enumerate(features):
    r = idx // cols
    cc = idx % cols
    fx = fx0 + cc*(feat_w + feat_gap)
    fy = fy0 - r*(feat_h + feat_gap)
    # 카드
    pdf.set_fill_color(*FEAT_BG)
    pdf.set_draw_color(*CARD_LINE)
    pdf.set_line_width(0.4)
    pdf.round_rect(fx, fy, feat_w, feat_h, 2.5, style="DF")
    # 상단 컬러 바
    pdf.set_fill_color(*FEAT_BAR)
    pdf.rect(fx, fy + feat_h - 4, feat_w, 4, style="F")
    # 제목
    pdf.set_text_color(*NAVY)
    pdf.set_font("NS", "B", 16)
    pdf.set_xy(fx, fy + feat_h - 18)
    pdf.cell(feat_w, 8, ftitle, align="C")
    # 설명
    pdf.set_text_color(*MUTED)
    pdf.set_font("NS", "", 11)
    dy2 = fy + feat_h - 34
    for j, line in enumerate(fdesc.split("\n")):
        pdf.set_xy(fx, dy2 - j*5.6)
        pdf.cell(feat_w, 5.6, line, align="C")

y = fy0 - rows*(feat_h + feat_gap) - 4

# 섹션: ICP
pdf.set_text_color(*NAVY)
pdf.set_font("NS", "B", 22)
pdf.cell(0, 12, "주요 사용처 (ICP)", align="C")
y -= 14

icps = [
    "금융위원회 보험과",
    "개인정보보호위원회 개인정보보호정책과",
    "조달청 규제개혁법무담당관",
]
pdf.set_text_color(*TEXT)
pdf.set_font("NS", "B", 14)
for icp in icps:
    pdf.set_xy(0, y)
    pdf.cell(0, 8.5, "·  " + icp, align="C")
    y -= 8.5

y -= 6

# 하단 라인
pdf.set_draw_color(*NAVY)
pdf.set_line_width(0.6)
pdf.line(ML, y, W - MR, y)
y -= 10

# URL + GitHub
pdf.set_text_color(*NAVY)
pdf.set_font("NS", "B", 15)
pdf.set_xy(0, y)
pdf.cell(0, 8, "서비스: https://mabc-finals.vercel.app", align="C")
y -= 9

pdf.set_text_color(*MUTED)
pdf.set_font("NS", "", 13)
pdf.set_xy(0, y)
pdf.cell(0, 7, "GitHub: https://github.com/testofschool/mabc2026-gyudung  (Public)", align="C")
y -= 12

pdf.set_text_color(*MUTED)
pdf.set_font("NS", "", 11)
pdf.set_xy(0, y)
pdf.cell(0, 6, "핵심 로직: admrul-diff 스크립트 (prelim/admrul-diff/scripts/admrul_diff.py)", align="C")
y -= 6
pdf.set_xy(0, y)
pdf.cell(0, 6, "모든 계산은 스크립트가 수행, LLM이 임의로 추정하지 않습니다.", align="C")

pdf.output(OUT)
size_kb = os.path.getsize(OUT) / 1024
print(f"✅ 강정민_포스터.pdf 생성 완료: {size_kb:.1f} KB (A1 세로 1장, fpdf + NanumSquareNeo 임베딩)")
