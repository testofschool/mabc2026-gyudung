#!/usr/bin/env python3
"""규정다름 — A1 세로 포스터 생성 (강정민_포스터.pdf)
- 규격: A1 세로 1장, 10MB 이하, PDF
- 글꼴: 나눔스퀘어네오 임베딩 (인쇄 시 글꼴 깨짐 방지)
- 템플릿 파일이 없으므로 직접 디자인
"""
from fpdf import FPDF
import os

FONT_BOLD = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Bd.otf"
FONT_REG   = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Rg.otf"
FONT_LIGHT = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Lt.otf"

class PosterPDF(FPDF):
    def __init__(self):
        # A1 세로
        super().__init__(orientation='P', unit='mm', format=(594, 841))
        self.add_font('NS', '', FONT_REG)
        self.add_font('NS', 'B', FONT_BOLD)
        self.set_auto_page_break(False)

pdf = PosterPDF()
pdf.add_page()
W, H = 594, 841  # A1 세로 mm

# ===== 배경: 상단 남색 띠 =====
pdf.set_fill_color(25, 55, 110)
pdf.rect(0, 0, W, 180, 'F')

# ===== 상단 태그 =====
pdf.set_y(25)
pdf.set_font('NS', 'B', 12)
pdf.set_text_color(180, 200, 230)
pdf.cell(0, 8, 'MABC 2026 결선  ·  팀명 강정민', align='C')
pdf.ln(20)

# ===== 메인 타이틀 =====
pdf.set_font('NS', 'B', 58)
pdf.set_text_color(255, 255, 255)
pdf.multi_cell(0, 24, '규정다름', align='C')
pdf.ln(6)

# ===== 부제목 =====
pdf.set_font('NS', '', 18)
pdf.set_text_color(190, 205, 235)
pdf.multi_cell(0, 9, '행정규칙 신·구 조문 대조 및\n시행일 D-day 자동 산출 서비스', align='C')

# ===== 중앙 콘텐츠 영역 =====
pdf.set_y(220)

# 서비스 설명
pdf.set_font('NS', 'B', 15)
pdf.set_text_color(25, 55, 110)
pdf.multi_cell(0, 8, '행정규칙·지침·훈령·예규·요령의\n구판과 신판 텍스트를 붙여넣으면\n조문별 대조표와 시행일 D-day를\n자동으로 출력합니다.', align='C')
pdf.ln(6)

# 핵심 3단계
pdf.set_font('NS', 'B', 19)
pdf.set_text_color(25, 55, 110)
pdf.cell(0, 12, '입력  →  처리  →  출력', align='C')
pdf.ln(16)

steps = [
    ('STEP 1', '텍스트\n붙여넣기', '구판·신판 텍스트를\n각 입력란에 붙여넣기'),
    ('STEP 2', '대조\n실행', '[대조 실행] 버튼 클릭\n(수초 소요, 로그인 불필요)'),
    ('STEP 3', '결과\n확인', '신·구 조문 대조표\n+ 시행 D-day 표 즉시 확인'),
]

step_w = 160
gap = (W - 3 * step_w) / 2
start_x = gap
y0 = pdf.get_y()

for i, (step, title, desc) in enumerate(steps):
    x = start_x + i * (step_w + gap)
    # 카드 배경
    pdf.set_fill_color(240, 244, 250)
    pdf.set_draw_color(25, 55, 110)
    pdf.set_line_width(0.5)
    pdf.rect(x, y0, step_w, 52, 'DF')
    # 스텝 번호
    pdf.set_xy(x + 4, y0 + 3)
    pdf.set_font('NS', 'B', 10)
    pdf.set_text_color(25, 55, 110)
    pdf.cell(step_w - 8, 5, step, align='C')
    # 제목
    pdf.set_xy(x + 4, y0 + 12)
    pdf.set_font('NS', 'B', 15)
    pdf.set_text_color(25, 55, 110)
    pdf.multi_cell(step_w - 8, 7, title, align='C')
    # 설명
    pdf.set_xy(x + 4, y0 + 34)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(70, 70, 90)
    pdf.multi_cell(step_w - 8, 4.5, desc, align='C')

pdf.set_y(y0 + 65)

# ===== 4대 특징 박스 =====
pdf.set_font('NS', 'B', 16)
pdf.set_text_color(25, 55, 110)
pdf.cell(0, 10, '핵심 특징', align='C')
pdf.ln(12)

features = [
    ('조문 대조', '구판·신판 텍스트를 붙여넣으면\n스크립트가 조항 단위로\nadded/modified/deleted를\n자동 판정합니다.'),
    ('시행일 D-day', '부칙의 시행일 문구를 파싱하여\n오늘(KST) 기준 D-day /\n시행상태를 자동 산출합니다.'),
    ('스크립트 기반', 'diff 판정, 시행일 파싱, D-day 계산\n모두 Python 스크립트가 수행.\nLLM이 임의로 추정하지 않습니다.'),
    ('즉시 사용 가능', 'API 키 없이 웹 브라우저에서\n바로 사용 가능.\n로그인·회원가입 불필요.'),
]

feat_y = pdf.get_y()
cols = 2
rows = 2
cell_w = (W - 24) / cols
cell_h = 62

for idx, (ftitle, fdesc) in enumerate(features):
    r = idx // cols
    c = idx % cols
    x = 12 + c * cell_w
    y = feat_y + r * (cell_h + 6)
    # 박스
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(200, 205, 215)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, cell_w, cell_h, 'DF')
    # 특징 제목
    pdf.set_xy(x + 8, y + 6)
    pdf.set_font('NS', 'B', 14)
    pdf.set_text_color(25, 55, 110)
    pdf.cell(cell_w - 16, 6, ftitle, align='C')
    # 특징 설명
    pdf.set_xy(x + 8, y + 16)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(60, 60, 80)
    pdf.multi_cell(cell_w - 16, 5, fdesc, align='C')

pdf.set_y(feat_y + 2 * (cell_h + 6) + 6)

# ===== ICP 타겟 =====
pdf.set_font('NS', 'B', 15)
pdf.set_text_color(25, 55, 110)
pdf.cell(0, 9, '주요 사용처 (ICP)', align='C')
pdf.ln(14)

icps = [
    '금융위원회 보험과',
    '개인정보보호위원회 개인정보보호정책과',
    '조달청 규제개혁법무담당관',
]
for icp in icps:
    pdf.set_font('NS', 'B', 13)
    pdf.set_text_color(40, 60, 100)
    pdf.cell(0, 7, f'·  {icp}', align='C')
    pdf.ln(7)

pdf.ln(8)

# ===== 하단 라인 =====
y_line = pdf.get_y()
pdf.set_draw_color(25, 55, 110)
pdf.set_line_width(0.5)
pdf.line(30, y_line, W - 30, y_line)
pdf.ln(10)

# ===== URL + GitHub =====
pdf.set_font('NS', 'B', 14)
pdf.set_text_color(25, 55, 110)
pdf.cell(0, 8, '서비스: https://mabc-finals.vercel.app', align='C')
pdf.ln(8)
pdf.set_font('NS', '', 12)
pdf.set_text_color(70, 70, 90)
pdf.cell(0, 7, 'GitHub: https://github.com/testofschool/mabc2026-gyudung  (Public)', align='C')
pdf.ln(14)

pdf.set_font('NS', '', 10)
pdf.set_text_color(100, 100, 120)
pdf.cell(0, 6, '핵심 로직: admrul-diff 스크립트 (prelim/admrul-diff/scripts/admrul_diff.py)', align='C')
pdf.ln(6)
pdf.cell(0, 6, '모든 계산은 스크립트가 수행, LLM이 임의로 추정하지 않습니다.', align='C')

# 저장
out = '/Users/felix/mabc-finals/강정민_포스터.pdf'
pdf.output(out)
size_kb = os.path.getsize(out) / 1024
print(f'✅ 강정민_포스터.pdf 생성 완료: {size_kb:.1f} KB ({pdf.page_no()}페이지, A1 세로)')
