#!/usr/bin/env python3
"""
규정다름 — A1 세로 프로덕션 포스터 (강정민_포스터.pdf)
- 판형: A1 세로 594x841mm, 여백 상30/하24/좌우24
- 폰트: NanumSquareNeo OTF (Regular/Bold/ExtraBold) 임베딩
- 팔레트: 남색 테마 (#19376E, #2A4D8F, #3E6BB0), 배경 #F4F6FB, 카드 흰색
- 구성: 상단 밴드 → 스텝 3카드 → 특징 2x2 → ICP → 하단 라인 + URL
"""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
import os

# ---------- 폰트 등록 ----------
FD = "/Users/felix/Library/Fonts"
pdfmetrics.registerFont(TTFont("NS_Rg",  os.path.join(FD, "NanumSquareNeoOTF-Rg.otf")))
pdfmetrics.registerFont(TTFont("NS_Bd",  os.path.join(FD, "NanumSquareNeoOTF-Bd.otf")))
pdfmetrics.registerFont(TTFont("NS_EB",  os.path.join(FD, "NanumSquareNeoOTF-Eb.otf")))
pdfmetrics.registerFont(TTFont("NS_Lt",  os.path.join(FD, "NanumSquareNeoOTF-Lt.otf")))

# ---------- 상수 ----------
W, H = 594*mm, 841*mm
M_L, M_R, M_T, M_B = 24*mm, 24*mm, 30*mm, 24*mm
CW = W - M_L - M_R  # 콘텐츠 폭 546mm

C_NAVY      = HexColor("#19376E")
C_NAVY2     = HexColor("#2A4D8F")
C_NAVY3     = HexColor("#3E6BB0")
C_BG        = HexColor("#F4F6FB")
C_CARD      = HexColor("#FFFFFF")
C_TEXT      = HexColor("#1A1F2B")
C_MUTED     = HexColor("#5A6478")
C_TAG       = HexColor("#B4C8E6")
C_WHITE     = HexColor("#FFFFFF")
C_ACCENT    = HexColor("#3E6BB0")
C_RULE      = HexColor("#2A4D8F")
C_CARD_LINE = HexColor("#D7DEEC")
C_FEAT_HEAD = HexColor("#19376E")
C_FEAT_BAR  = HexColor("#3E6BB0")
C_FEAT_BG   = HexColor("#F7F9FC")

OUT = "/Users/felix/mabc-finals/강정민_포스터.pdf"

c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("규정다름 — MABC 2026 강정민")
c.setAuthor("강정민")

# ================= 상단 밴드 =================
band_h = 190*mm
c.setFillColor(C_NAVY)
c.rect(0, H - band_h, W, band_h, fill=1, stroke=0)

# 태그
c.setFillColor(C_TAG)
c.setFont("NS_Bd", 12)
c.drawCentredString(W/2, H - 34*mm, "MABC 2026 결선  ·  팀명 강정민")

# 메인 타이틀
c.setFillColor(C_WHITE)
c.setFont("NS_EB", 72)
ty = H - 60*mm
c.drawCentredString(W/2, ty, "규정다름")

# 타이틀 아래 강조선
c.setStrokeColor(C_NAVY3)
c.setLineWidth(2.2*mm)
c.line(W/2 - 50*mm, ty - 10*mm, W/2 + 50*mm, ty - 10*mm)

# 부제목
c.setFillColor(C_TAG)
c.setFont("NS_Rg", 20)
c.drawCentredString(W/2, ty - 30*mm,
    "행정규칙 신·구 조문 대조 및\n시행일 D-day 자동 산출 서비스")

# 밴드 하단 얇은 경계선
c.setStrokeColor(C_NAVY3)
c.setLineWidth(0.6*mm)
c.line(M_L, H - band_h, W - M_R, H - band_h)

# ================= 콘텐츠 영역 시작 =================
# 밴드 바로 아래부터 여백 없이 콘텐츠 시작 (상단 여백은 밴드 자체가 확보)
y = H - band_h - 18*mm

# ---- 섹션: 입력→처리→출력 ----
c.setFillColor(C_NAVY)
c.setFont("NS_Bd", 22)
c.drawCentredString(W/2, y, "입력  →  처리  →  출력")
y -= 12*mm

# 스텝 카드 3개
steps = [
    ("STEP 1", "텍스트\n붙여넣기", "구판·신판 텍스트를\n각 입력란에 붙여넣기"),
    ("STEP 2", "대조\n실행", "[대조 실행] 버튼 클릭\n(수초 소요, 로그인 불필요)"),
    ("STEP 3", "결과\n확인", "신·구 조문 대조표\n+ 시행 D-day 표 즉시 확인"),
]
card_h = 60*mm
gap = 8*mm
card_w = (CW - 2*gap) / 3
x0 = M_L
card_y = y - card_h

for i, (num, title, desc) in enumerate(steps):
    x = x0 + i*(card_w + gap)
    # 카드 배경
    c.setFillColor(C_CARD)
    c.setStrokeColor(C_CARD_LINE)
    c.setLineWidth(0.5*mm)
    c.roundRect(x, card_y, card_w, card_h, 3*mm, fill=1, stroke=1)
    # 상단 색상 바
    c.setFillColor(C_NAVY2)
    c.rect(x, card_y + card_h - 6*mm, card_w, 6*mm, fill=1, stroke=0)
    # 번호 원
    circ_r = 8*mm
    c.setFillColor(C_NAVY)
    c.circle(x + card_w/2, card_y + card_h - 18*mm, circ_r, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("NS_Bd", 12)
    c.drawCentredString(x + card_w/2, card_y + card_h - 20.5*mm, num.split()[1])
    # 제목
    c.setFillColor(C_NAVY)
    c.setFont("NS_Bd", 18)
    ty2 = card_y + card_h - 34*mm
    for j, line in enumerate(title.split("\n")):
        c.drawCentredString(x + card_w/2, ty2 - j*7*mm, line)
    # 설명
    c.setFillColor(C_MUTED)
    c.setFont("NS_Rg", 11)
    dy = card_y + card_h - 50*mm
    for j, line in enumerate(desc.split("\n")):
        c.drawCentredString(x + card_w/2, dy - j*5.2*mm, line)

y = card_y - 12*mm

# ---- 섹션: 핵심 특징 ----
c.setFillColor(C_NAVY)
c.setFont("NS_Bd", 22)
c.drawCentredString(W/2, y, "핵심 특징")
y -= 12*mm

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
feat_w = (CW - 6*mm) / cols
feat_h = 62*mm
feat_gap = 6*mm
fx0 = M_L + 3*mm
fy0 = y - feat_h

for idx, (ftitle, fdesc) in enumerate(features):
    r = idx // cols
    cc = idx % cols
    fx = fx0 + cc*(feat_w + feat_gap)
    fy = fy0 - r*(feat_h + feat_gap)
    # 카드
    c.setFillColor(C_FEAT_BG)
    c.setStrokeColor(C_CARD_LINE)
    c.setLineWidth(0.4*mm)
    c.roundRect(fx, fy, feat_w, feat_h, 2.5*mm, fill=1, stroke=1)
    # 상단 컬러 바
    c.setFillColor(C_FEAT_BAR)
    c.rect(fx, fy + feat_h - 4*mm, feat_w, 4*mm, fill=1, stroke=0)
    # 제목
    c.setFillColor(C_FEAT_HEAD)
    c.setFont("NS_Bd", 16)
    c.drawCentredString(fx + feat_w/2, fy + feat_h - 18*mm, ftitle)
    # 설명
    c.setFillColor(C_MUTED)
    c.setFont("NS_Rg", 11)
    dy2 = fy + feat_h - 34*mm
    for j, line in enumerate(fdesc.split("\n")):
        c.drawCentredString(fx + feat_w/2, dy2 - j*5.6*mm, line)

y = fy0 - rows*(feat_h + feat_gap) - 4*mm

# ---- 섹션: ICP ----
c.setFillColor(C_NAVY)
c.setFont("NS_Bd", 22)
c.drawCentredString(W/2, y, "주요 사용처 (ICP)")
y -= 12*mm

icps = [
    "금융위원회 보험과",
    "개인정보보호위원회 개인정보보호정책과",
    "조달청 규제개혁법무담당관",
]
c.setFillColor(C_TEXT)
c.setFont("NS_Bd", 14)
for icp in icps:
    c.drawCentredString(W/2, y, "·  " + icp)
    y -= 8.5*mm

y -= 6*mm

# ---- 하단 라인 ----
c.setStrokeColor(C_NAVY)
c.setLineWidth(0.6*mm)
c.line(M_L, y, W - M_R, y)
y -= 10*mm

# ---- URL + GitHub ----
c.setFillColor(C_NAVY)
c.setFont("NS_Bd", 15)
c.drawCentredString(W/2, y, "서비스: https://mabc-finals.vercel.app")
y -= 9*mm

c.setFillColor(C_MUTED)
c.setFont("NS_Rg", 13)
c.drawCentredString(W/2, y, "GitHub: https://github.com/testofschool/mabc2026-gyudung  (Public)")
y -= 12*mm

c.setFillColor(C_MUTED)
c.setFont("NS_Rg", 11)
c.drawCentredString(W/2, y, "핵심 로직: admrul-diff 스크립트 (prelim/admrul-diff/scripts/admrul_diff.py)")
y -= 6*mm
c.drawCentredString(W/2, y, "모든 계산은 스크립트가 수행, LLM이 임의로 추정하지 않습니다.")

# 저장
c.showPage()
c.save()
size_kb = os.path.getsize(OUT) / 1024
print(f"✅ 강정민_포스터.pdf 생성 완료: {size_kb:.1f} KB (A1 세로 1장, reportlab + NanumSquareNeo 임베딩)")
