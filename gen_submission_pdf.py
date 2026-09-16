#!/usr/bin/env python3
"""
규정다름 — MABC 2026 결선 제출물 생성기 (강정민 팀)
- PRD PDF, 발표자료 PDF, 서비스 소개 텍스트 생성
- 폰트: 나눔스퀘어네오 (NanumSquareNeo)
"""

from fpdf import FPDF
import os

FONT_BOLD = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Bd.otf"
FONT_REG = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Rg.otf"
FONT_LIGHT = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Lt.otf"
FONT_HEAVY = "/Users/felix/Library/Fonts/NanumSquareNeoOTF-Hv.otf"

# ============================================
# 공통 스타일
# ============================================
class BasePDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('NS', '', FONT_REG)
        self.add_font('NS', 'B', FONT_BOLD)
        self.add_font('NS', 'I', FONT_REG)  # 이탤릭 없음, 정규로 대체
        self.set_auto_page_break(True, 15)
    
    def title_page(self, title, subtitle, team="강정민", date="2026.09.16"):
        self.add_page()
        self.ln(40)
        # 상단 라인
        self.set_draw_color(30, 60, 120)
        self.set_line_width(0.8)
        self.line(20, 50, 190, 50)
        self.ln(15)
        # 제목
        self.set_font('NS', 'B', 28)
        self.set_text_color(20, 40, 80)
        self.multi_cell(0, 12, title, align='C')
        self.ln(8)
        # 부제목
        self.set_font('NS', '', 14)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 7, subtitle, align='C')
        self.ln(20)
        # 팀명
        self.set_font('NS', 'B', 16)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, f'팀명: {team}', align='C')
        self.ln(10)
        self.set_font('NS', '', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, f'작성일: {date}', align='C')
        self.ln(7)
        self.cell(0, 7, 'MABC 2026 결선 제출용', align='C')
        self.ln(20)
        # 하단 라인
        self.set_draw_color(30, 60, 120)
        self.set_line_width(0.8)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)

    def section_heading(self, num, title):
        self.ln(8)
        self.set_font('NS', 'B', 15)
        self.set_text_color(20, 40, 80)
        text = f'{num}. {title}'
        self.cell(0, 8, text)
        self.ln(5)
        # 언더라인
        self.set_draw_color(30, 60, 120)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(20, y, 190, y)
        self.ln(4)
    
    def body(self, text, size=10, indent=0):
        self.set_font('NS', '', size)
        self.set_text_color(50, 50, 50)
        if indent:
            self.set_x(20 + indent)
            self.multi_cell(170 - indent, 5.5, text)
        else:
            self.multi_cell(0, 5.5, text)
        self.ln(2)
    
    def bullet(self, text, indent=5):
        self.set_font('NS', '', 10)
        self.set_text_color(50, 50, 50)
        self.set_x(20 + indent)
        self.cell(5, 5.5, '•')
        self.multi_cell(165 - indent, 5.5, text)
    
    def highlight_box(self, text):
        self.ln(3)
        self.set_fill_color(235, 240, 250)
        self.set_draw_color(30, 60, 120)
        y_before = self.get_y()
        self.set_font('NS', '', 10)
        self.set_text_color(40, 40, 60)
        # 박스 높이 계산
        self.set_x(25)
        self.multi_cell(160, 5.5, text, fill=True)
        y_after = self.get_y()
        # 박스 그리기
        self.set_line_width(0.3)
        self.rect(20, y_before, 170, y_after - y_before)
        self.ln(4)
    
    def table_simple(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [170 / len(headers)] * len(headers)
        self.ln(3)
        # 헤더
        self.set_fill_color(30, 60, 120)
        self.set_text_color(255, 255, 255)
        self.set_font('NS', 'B', 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, f' {h}', border=0, fill=True)
        self.ln()
        # 행
        for j, row in enumerate(rows):
            if j % 2 == 0:
                self.set_fill_color(245, 247, 250)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(40, 40, 40)
            self.set_font('NS', '', 9)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, f' {cell}', border=0, fill=True)
            self.ln()
        self.ln(4)


# ============================================
# 1. PRD PDF
# ============================================
def create_prd():
    pdf = BasePDF()
    
    pdf.title_page(
        '규정다름',
        '행정규칙 신·구 조문 대조 및\n시행일 D-day 자동 산출 서비스',
        team='강정민'
    )
    
    # 1. 서비스 개요
    pdf.section_heading('1', '서비스 개요')
    pdf.body('규정다름은 행정규칙·지침·훈령·예규·요령 등 조문 단위로 제·개정되는 문서의 구판과 신판 텍스트를 입력받아, 조문별 신설·변경·삭제 내역을 대조표로 출력하고 부칙 시행일을 파싱하여 오늘 기준 D-day와 시행상태를 함께 보여주는 웹 서비스입니다.')
    pdf.body('공무원은 행정규칙이 개정될 때마다 두 문서를 출력하여 눈으로 비교하는 수작업을 반복해 왔습니다. 규정다름은 이 과정을 자동화하여, 텍스트를 붙여넣는 것만으로 수초 내에 변경 내용과 시행 상태를 파악할 수 있게 합니다.')
    
    # 2. 문제 정의
    pdf.section_heading('2', '문제 정의')
    pdf.body('행정규칙은 현장에서 지속적으로 제·개정되지만, 실무자가 개정 내용을 확인하는 방식은 여전히 두 문서를 출력하여 눈으로 비교하는 수준에 머물러 있습니다.')
    pdf.bullet('국가법령정보센터(law.go.kr)는 법령 신·구조문 비교 기능을 제공하지만, 사용자가 구판·신판 텍스트를 직접 붙여넣어 조문 단위로 즉시 대조하고 시행일 D-day까지 한 화면에서 확인하는 방식은 아닙니다. 법제처 open API(open.law.go.kr)는 개발자용 조회 기능만 제공할 뿐, 비개발자가 바로 쓸 수 있는 대조표 산출로 이어지지 않습니다. 실무자는 구판·신판 텍스트를 각각 확보한 뒤 두 문서를 펼쳐놓고 조문별로 변경된 내용을 수동으로 확인하고, 별도로 해당 규정의 시행일을 조회해야 합니다.')
    pdf.body('규정 개정 빈도가 높은 기관일수록 이 부담은 커집니다.')
    
    # 3. 해결 방안
    pdf.section_heading('3', '해결 방안')
    pdf.body('규정다름은 위 문제를 다음 기능으로 해결합니다.')
    pdf.table_simple(
        ['기능', '설명', '기존 대비 우위'],
        [
            ['조문 대조', '구판·신판 텍스트를 붙여넣으면 스크립트가 조항 단위로 added/modified/deleted를 자동 판정', '눈으로 비교하는 수작업 대체, 수초 내 완료'],
            ['시행일 D-day', '부칙 시행일 문구를 파싱하여 오늘(KST) 기준 D-day/시행상태를 자동 산출', '별도 조회 없이 시행 상태 즉시 확인'],
            ['스크립트 기반', 'diff 판정, 시행일 파싱, D-day 계산 모두 Python 스크립트가 수행 (LLM 임의 추정 없음)', '계산 과정의 투명성·재현성 확보'],
            ['즉시 사용 가능', 'API 키 없이 웹 브라우저에서 바로 사용. 로그인·회원가입 불필요', '개방형 접근성, 진입 장벽 최소화'],
        ],
        [35, 80, 55]
    )
    
    # 4. 사용 시나리오
    pdf.section_heading('4', '사용 시나리오')
    pdf.body('상황: A시청 자치행정과 주무관 B가 소관 지침의 개정 통지를 받았습니다. 구판과 신판 텍스트를 이메일로 받았습니다.')
    pdf.bullet('주무관 B는 규정다름 웹사이트에 접속합니다. (로그인 불필요)')
    pdf.bullet('구판 텍스트와 신판 텍스트를 각 입력란에 붙여넣습니다.')
    pdf.bullet('[대조 실행] 버튼을 클릭합니다.')
    pdf.bullet('수초 내에 화면에 ① 어떤 조문이 신설·변경·삭제되었는지 나타낸 대조표와 ② 해당 지침의 시행일 및 현재 시행 상태(D-n / 시행중 / 오늘 시행)가 표시됩니다.')
    pdf.bullet('주무관 B는 변경된 조문만 빠르게 확인하고, 해당 지침이 현재 시행 중인지(또는 언제 시행 예정인지)를 별도 검색 없이 파악합니다.')
    pdf.bullet('필요하면 [JSON 보기] 토글로 원본 계산 결과를 확인할 수 있습니다.')
    pdf.body('전체 소요 시간: 약 30초 이내 (law.go.kr에서 동일 내용을 확인하는 경우 2~3분 추정).')
    
    # 5. 기술 아키텍처
    pdf.section_heading('5', '기술 아키텍처')
    pdf.body('규정다름은 단일 HTML 정적 페이지와 Vercel 서버리스 Python 함수로 구성된 경량 아키텍처입니다.')
    pdf.table_simple(
        ['구성 요소', '기술 스택', '역할'],
        [
            ['프론트엔드', '단일 HTML + Vanilla JS (CSS 변수 기반)', '사용자 입력 수신, API 호출, 결과 표 렌더링'],
            ['백엔드 API', 'Python (WSGI 기반), Vercel 서버리스', '텍스트 수신, diff 계산, 시행일 파싱, D-day 산출, JSON 응답'],
            ['핵심 로직', 'admrul-diff 스크립트 (Python stdlib)', '조문 파싱, diff 판정, 시행일 파싱, D-day 계산 — 모든 계산 수행'],
            ['배포', 'Vercel (정적 사이트 + 서버리스 함수)', '전 세계 CDN, HTTPS, 스케일 투 제로'],
            ['데이터 저장', '없음 (무상태)', '모든 계산은 요청 시점 메모리에서 수행, 데이터 저장하지 않음'],
        ],
        [35, 55, 80]
    )
    
    # 6. API 상세
    pdf.section_heading('6', 'API 상세')
    pdf.body('엔드포인트: POST /api/admrul-diff')
    pdf.body('요청 본문 (JSON):')
    pdf.highlight_box('{\n  "old_text": "구판 텍스트 (문자열)",\n  "new_text": "신판 텍스트 (문자열)"\n}')
    pdf.body('응답 본문 (JSON):')
    pdf.highlight_box('{\n  "diff": [\n    {\n      "article_number": "2",\n      "article_title": "운영시간",\n      "judgment": "modified",\n      "old_content": "...",\n      "new_content": "..."\n    }\n  ],\n  "enactment": {\n    "old_date": "2026-03-01",\n    "new_date": "2026-09-15",\n    "reference_date": "2026-09-16",\n    "new_d_day_status": "시행중",\n    "old_d_day_status": "시행중"\n  }\n}')
    pdf.body('judgment 값: added (신설) / modified (변경) / deleted (삭제)')
    pdf.body('d_day_status 값: D-n (시행일까지 n일 남음) / 오늘 시행 / 시행중 / 시행일 미검출')
    pdf.body('CORS: 모든 오리진 허용 (Access-Control-Allow-Origin: *)')
    
    # 7. 입력 검증
    pdf.section_heading('7', '입력 검증 및 오류 처리')
    pdf.bullet('구판 텍스트가 비어 있으면: "구판 입력이 비어 있습니다." (400 오류)')
    pdf.bullet('신판 텍스트가 비어 있으면: "신판 입력이 비어 있습니다." (400 오류)')
    pdf.bullet('구판에서 조문 패턴(제N조)이 검출되지 않으면: "구판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다." (400 오류)')
    pdf.bullet(' 신판에서 조문 패턴이 검출되지 않으면: 동일한 형식의 오류 (400 오류)')
    pdf.bullet('서버 내부 오류 발생 시: "서버 내부 오류" (500 오류) + 에러 메시지')
    pdf.body('모든 오류는 구조화된 JSON으로 반환되며, 프론트엔드에서 에러 박스 형태로 표시됩니다.')
    
    # 8. 차별화
    pdf.section_heading('8', '차별화 및 경쟁 우위')
    pdf.body('규정다름의 핵심 차별화는 \'붙여넣기 즉시성\'과 \'시행일 D-day 자동 산출\'의 결합입니다.')
    pdf.body('국가법령정보센터는 법령 신·구조문 비교 기능을 제공하며 공식성을 갖추고 있으나, 사용자가 구판·신판 텍스트를 직접 붙여넣어 조문 단위로 즉시 대조하고 시행일 D-day까지 한 화면에서 확인하는 방식은 아닙니다. 법제처 open API는 개발자용 조회 기능만 제공할 뿐, 비개발자가 바로 쓸 수 있는 대조표 산출로 이어지지 않습니다.')
    pdf.body('규정다름은 이 틈새를 메우며, 특히 다음과 같은 점에서 차별화됩니다:')
    pdf.bullet('속도: 텍스트를 붙여넣는 즉시 결과 출력 (law.go.kr에서 동일 작업 시 메뉴 탐색·별도 페이지 이동 필요)')
    pdf.bullet('완전성: 조문 대조 + 시행 D-day를 한 화면에서 동시에 제공')
    pdf.bullet('접근성: 로그인·회원가입·API 키 없이 누구나 사용 가능')
    pdf.bullet('신뢰성: LLM이 아닌 스크립트가 계산 수행. 계산 과정 재현 가능')
    pdf.bullet('행정규칙 포괄: 지침·훈령·예규·요령 등 다양한 행정규칙 형식 지원')
    pdf.bullet('폐쇄망 대응: 핵심 계산은 Python stdlib 기반 스크립트이므로, 내부망·폐쇄망 환경에서도 구판·신판 텍스트만 있으면 같은 방식으로 대조 가능')
    
    # 9. 향후 발전 방향
    pdf.section_heading('9', '향후 발전 방향')
    pdf.bullet('파일 업로드 지원: 텍스트 붙여넣기 외에 PDF/문서 파일 업로드로 직접 대조')
    pdf.bullet('국가법령정보센터/open API 연동: 행정규칙 원문을 자동 조회하여 비교')
    pdf.bullet('비교 결과 저장·공유: 대조 결과 링크를 생성하거나 PDF로 export')
    pdf.bullet('다크 모드 지원: CSS 변수 기반 테마 전환')
    pdf.bullet('다국어 지원: 한국어 외 영문 행정규칙 대조 확장')
    pdf.bullet('기관별 알림: 관심 규정의 개정 발생 시 알림 (옵트인 기반)')
    
    # 10. 팀 정보
    pdf.section_heading('10', '팀 정보')
    pdf.table_simple(
        ['항목', '내용'],
        [
            ['팀명', '강정민'],
            ['참가자', '강정민 (단독)'],
            ['플랫폼', 'Hermes Agent'],
            ['서비스 URL', 'https://mabc-finals.vercel.app'],
            ['GitHub', 'https://github.com/testofschool/mabc2026-gyudung'],
            ['핵심 기술', 'Python (admrul-diff 스크립트), Vercel 서버리스, HTML/CSS/JS'],
        ],
        [40, 130]
    )
    
    output_path = '/Users/felix/mabc-finals/강정민_PRD.pdf'
    pdf.output(output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f'✅ 강정민_PRD.pdf 생성 완료: {size_kb:.1f} KB ({pdf.page_no()}페이지)')
    return output_path


# ============================================
# 2. 발표자료 PDF
# ============================================
def create_presentation():
    pdf = BasePDF()
    
    # 표지
    pdf.add_page()
    pdf.ln(50)
    pdf.set_draw_color(20, 40, 80)
    pdf.set_line_width(1.0)
    pdf.line(20, 60, 190, 60)
    pdf.ln(20)
    pdf.set_font('NS', 'B', 32)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(0, 14, '규정다름', align='C')
    pdf.ln(16)
    pdf.set_font('NS', '', 14)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7, '행정규칙 신·구 조문 대조 및 시행 D-day 서비스', align='C')
    pdf.ln(20)
    pdf.set_draw_color(20, 40, 80)
    pdf.set_line_width(0.5)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(12)
    pdf.set_font('NS', 'B', 16)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 10, '강정민', align='C')
    pdf.ln(10)
    pdf.set_font('NS', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, 'MABC 2026 결선', align='C')
    pdf.ln(7)
    pdf.cell(0, 7, '2026.09.16', align='C')
    pdf.ln(30)
    
    # 슬라이드 1: 문제 인식
    pdf.add_page()
    pdf.section_heading('01', '문제 인식')
    pdf.body('행정규칙은 현장에서 지속적으로 제·개정됩니다.', size=11)
    pdf.ln(2)
    pdf.body('그러나 실무자의 개정 내용 확인 방식은 20년 전과 크게 다르지 않습니다.', size=11)
    pdf.ln(4)
    pdf.body('현행 방식의 문제점:', size=11)
    pdf.bullet('국가법령정보센터는 법령 신·구조문 비교 기능을 제공하지만, 사용자가 구판·신판 텍스트를 붙여넣어 조문 단위로 즉시 대조하고 시행일 D-day까지 한 화면에서 확인하는 방식은 아닙니다.')
    pdf.bullet('시행일 확인을 위해 별도 검색 필요')
    pdf.bullet('법제처 open API는 개발자용, 비개발자 사용 어려움')
    pdf.ln(4)
    pdf.highlight_box('"규정 개정 통지서를 받고, 두 문서를 펼쳐놓고 조문별로 변경된 내용을 확인하고, 시행일을 따로 찾아보는 — 이 모든 과정이 아직도 수작업입니다."')
    
    # 슬라이드 2: 해결책
    pdf.add_page()
    pdf.section_heading('02', '해결책: 규정다름')
    pdf.body('텍스트를 붙여넣기만 하면, 조문별 대조표 + 시행 D-day가 즉시 출력됩니다.', size=12)
    pdf.ln(6)
    pdf.body('핵심 기능 3가지:', size=11)
    pdf.ln(2)
    pdf.set_font('NS', 'B', 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, '① 조문 대조 (added / modified / deleted)')
    pdf.ln(6)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.body('구판·신판 텍스트에서 제N조 패턴으로 모든 조문을 파싱한 뒤, 조문 단위로 신설·변경·삭제 여부를 자동 판정합니다. 판례나 해석이 아니라 조문 텍스트 자체에 근거한 기계적 비교입니다.')
    pdf.ln(2)
    pdf.set_font('NS', 'B', 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, '② 시행 D-day 자동 산출')
    pdf.ln(6)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.body('부칙의 "이 지침은 2026년 9월 15일부터 시행한다." 같은 문구를 정규식으로 파싱하여 시행일자를 추출하고, 오늘(KST) 기준 D-day / 오늘 시행 / 시행중 / 시행일 미검출 상태를 자동 계산합니다.')
    pdf.ln(2)
    pdf.set_font('NS', 'B', 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, '③ 스크립트 기반 계산 (LLM 임의 추정 없음)')
    pdf.ln(6)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.body('diff 판정, 시행일 파싱, D-day 계산 모두 Python 스크립트(admrul-diff)가 수행합니다. LLM이 임의로 추정하지 않으며, 계산 과정은 재현 가능합니다.')
    
    # 슬라이드 3: 사용 흐름
    pdf.add_page()
    pdf.section_heading('03', '사용 흐름')
    pdf.body('3단계로 끝납니다.', size=12)
    pdf.ln(8)
    pdf.set_fill_color(30, 60, 120)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('NS', 'B', 11)
    steps = [
        ('STEP 1', '텍스트\n붙여넣기', '구판·신판 텍스트를\n각 입력란에 붙여넣기'),
        ('STEP 2', '대조\n실행', '[대조 실행] 버튼\n클릭 (수초 소요)'),
        ('STEP 3', '결과\n확인', '대조표 + D-day 표\n즉시 확인'),
    ]
    for i, (step_num, step_title, step_desc) in enumerate(steps):
        x = 20 + i * 55
        # 카드 배경
        pdf.set_fill_color(240, 244, 250)
        pdf.set_draw_color(30, 60, 120)
        pdf.set_line_width(0.3)
        pdf.rect(x, pdf.get_y(), 50, 40, style='DF')
        # 스텝 번호
        pdf.set_font('NS', 'B', 9)
        pdf.set_text_color(30, 60, 120)
        pdf.set_xy(x + 2, pdf.get_y() + 3)
        pdf.cell(46, 5, step_num)
        # 제목
        pdf.set_font('NS', 'B', 12)
        pdf.set_text_color(20, 40, 80)
        pdf.set_xy(x + 2, pdf.get_y() + 2)
        pdf.multi_cell(46, 6, step_title, align='C')
        # 설명
        pdf.set_font('NS', '', 8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(x + 2, pdf.get_y() + 4)
        pdf.multi_cell(46, 4, step_desc, align='C')
        # 화살표 (중간)
        if i < 2:
            pdf.set_xy(x + 51, pdf.get_y() - 30)
            pdf.set_font('NS', '', 14)
            pdf.set_text_color(30, 60, 120)
            pdf.cell(4, 5, '→')
    pdf.ln(45)
    pdf.body('샘플 입력: 서비스 화면의 \'샘플 불러오기\' 버튼으로 데모용 데이터(구판: 시립도서관 자료실 운영 지침 2026.3.1. 시행 / 신판: 2026.9.15. 시행)를 바로 넣어볼 수 있습니다.', size=9)
    
    # 슬라이드 4: 기술 구조
    pdf.add_page()
    pdf.section_heading('04', '기술 구조')
    pdf.body('경량 아키텍처 — 단일 HTML + Vercel 서버리스', size=11)
    pdf.ln(6)
    pdf.table_simple(
        ['구성 요소', '기술', '역할'],
        [
            ['프론트엔드', 'HTML + Vanilla JS', '입력·출력 화면'],
            ['백엔드 API', 'Python (WSGI) + Vercel', 'diff 계산·D-day 산출'],
            ['핵심 로직', 'admrul-diff (Python stdlib)', '조문 파싱·diff·시행일 파싱'],
            ['배포', 'Vercel CDN', 'HTTPS·전 세계 서비스'],
            ['데이터 저장', '없음 (무상태)', '계산만 수행, 저장 안 함'],
        ],
        [40, 50, 80]
    )
    pdf.ln(4)
    pdf.body('보안: 사용자 데이터를 저장하지 않습니다. 모든 계산은 요청 시점의 메모리에서 수행되며, 요청이 끝나면 데이터가 남지 않습니다.', size=9)
    pdf.body('CORS: 모든 오리진에서 접근 가능 (Access-Control-Allow-Origin: *).', size=9)
    
    # 슬라이드 5: 차별화
    pdf.add_page()
    pdf.section_heading('05', '경쟁 서비스와의 비교')
    pdf.table_simple(
        ['비교 항목', '규정다름', '국가법령정보센터', '법제처 open API'],
        [
            ['접근 방식', '텍스트 붙여넣기 즉시', '웹사이트 탐색 후 비교 메뉴', 'API 호출 (개발자용)'],
            ['행정규칙 대응', '구판·신판 텍스트를 직접 붙여넣어 비교', '법령 중심, 신·구조문 비교 기능 있음', '행정규칙 조회 가능'],
            ['조문 대조표', '자동 생성', '법령별 신·구조문 비교 제공', '별도 구현 필요'],
            ['시행 D-day 계산', '자동 산출 (오늘 기준)', '제공 안 함', '제공 안 함'],
            ['사용 자격', '누구나 (로그인 불필요)', '누구나', 'API 키 필요'],
            ['계산 신뢰성', '스크립트 기반', '공식 시스템', '공식 데이터'],
        ],
        [30, 45, 47, 48]
    )
    pdf.body('핵심 차별화: \'붙여넣기 즉시성\' + \'시행일 D-day 자동 산출\' + \'로그인 없이 누구나 사용\'', size=10)
    pdf.ln(2)
    pdf.body('특히 규제기관, 지자체, 공공기관 실무자는 내부망·폐쇄망 환경에서도 구판·신판 텍스트만 있으면 동일한 대조 결과를 얻을 수 있습니다. 규정다름의 핵심 계산은 Python stdlib 기반 스크립트이므로, 인터넷 연결 없이도 로컬에서 같은 방식으로 실행 가능합니다.', size=9)
    
    # 슬라이드 6: 데모
    pdf.add_page()
    pdf.section_heading('06', '데모')
    pdf.body('지금 바로 사용해 볼 수 있습니다.', size=11)
    pdf.ln(4)
    pdf.set_font('NS', 'B', 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, '서비스 URL: https://mabc-finals.vercel.app')
    pdf.ln(8)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.body('1. 위 URL에 접속합니다. (로그인 불필요)')
    pdf.body('2. 화면 중앙의 두 텍스트 영역에 구판·신판 텍스트를 붙여넣습니다.')
    pdf.body('3. [샘플 불러오기] 버튼을 클릭하면 데모용 데이터가 자동 입력됩니다.')
    pdf.body('4. [대조 실행] 버튼을 클릭하면 수초 내에 결과가 표시됩니다.')
    pdf.body('5. 화면에 ① 신·구 조문 대조표(신설/변경/삭제 구분)와 ② 시행 D-day 표가 출력됩니다.')
    pdf.ln(4)
    pdf.highlight_box('샘플: 구판 \'시립도서관 자료실 운영 지침\'(2026.3.1. 시행)과 신판(2026.9.15. 시행)을 비교하면, 제2조(운영시간) 변경, 제4조(자료 대출) 변경, 제5조(음식물 반입 금지) 삭제, 제6조(디지털 자료실 운영) 신설이 자동 검출됩니다.')
    
    # 슬라이드 7: 향후 계획 + 팀 소개
    pdf.add_page()
    pdf.section_heading('07', '향후 발전 방향')
    pdf.bullet('파일 업로드 지원 검토: 현재는 텍스트 붙여넣기 방식이며, 향후 PDF/문서 파일 업로드를 통한 직접 대조 기능을 검토할 수 있습니다.')
    pdf.bullet('국가법령정보센터/open API 연동: 행정규칙 원문 자동 조회')
    pdf.bullet('비교 결과 저장·공유: 링크 생성, PDF export')
    pdf.bullet('다크 모드 지원: CSS 변수 기반 테마 전환')
    pdf.bullet('다국어 지원: 영문 행정규칙 대조 확장')
    pdf.bullet('기관별 알림: 관심 규정 개정 시 알림 (옵트인 기반)')
    pdf.ln(8)
    pdf.section_heading('', '팀 소개')
    pdf.table_simple(
        ['항목', '내용'],
        [
            ['팀명', '강정민'],
            ['참가자', '강정민 (단독)'],
            ['플랫폼', 'Hermes Agent'],
            ['서비스 URL', 'https://mabc-finals.vercel.app'],
            ['GitHub', 'https://github.com/testofschool/mabc2026-gyudung'],
            ['핵심 기술', 'Python (admrul-diff), Vercel 서버리스, HTML/CSS/JS'],
        ],
        [40, 130]
    )
    
    output_path = '/Users/felix/mabc-finals/강정민_발표자료.pdf'
    pdf.output(output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f'✅ 강정민_발표자료.pdf 생성 완료: {size_kb:.1f} KB ({pdf.page_no()}페이지)')
    return output_path


# ============================================
# 3. 서비스 동작 방식 설명 (400자 이내)
# ============================================
def create_description():
    description = (
        "규정다름은 행정규칙·지침·훈령·예규·요령 등 조문 단위로 제·개정되는 문서의 "
        "구판 텍스트와 신판 텍스트를 입력받아, 조문별 신설·변경·삭제 내역을 대조표로 출력하고 "
        "부칙 시행일을 파싱하여 오늘 기준 D-day와 시행상태를 함께 보여주는 서비스입니다. "
        "사용자는 구판·신판 텍스트를 각 입력란에 붙여넣고 [대조 실행] 버튼을 누릅니다. "
        "서버는 두 텍스트에서 조문 번호(제N조)와 부칙 시행일 문구를 파싱한 뒤, 조문 단위로 "
        "added/modified/deleted를 판별합니다. 판례나 해석이 아니라 조문 텍스트 자체에 근거해 "
        "기계적으로 비교하며, LLM이 임의로 추정하지 않습니다. 화면에는 ① 조문별 신·구 대조표"
        "(구분·조문·구판 내용·신판 내용)와 ② 시행일 정보(시행일·기준일자·시행상태) 표가 출력됩니다. "
        "변경된 조문이 없으면 '변경된 조문이 없습니다'가 표시됩니다. "
        "예외 처리: 구판 또는 신판이 비어 있거나, 조문 패턴(제N조)이 검출되지 않으면 오류 메시지를 보여줍니다. "
        "로그인 없이 누구나 바로 사용할 수 있습니다. "
        "샘플 입력: '샘플 불러오기' 버튼으로 구판('시립도서관 자료실 운영 지침' 2026.3.1. 시행)과 "
        "신판(2026.9.15. 시행) 텍스트를 바로 넣어볼 수 있습니다."
    )
    
    desc_path = '/Users/felix/mabc-finals/강정민_서비스소개.txt'
    with open(desc_path, 'w', encoding='utf-8') as f:
        f.write(description)
    
    char_count = len(description)
    print(f'✅ 강정민_서비스소개.txt 생성 완료: {char_count}자 (400자 {"이내" if char_count <= 400 else "초과 — 수정 필요!!!"})')
    return desc_path, char_count


# ============================================
# 실행
# ============================================
if __name__ == '__main__':
    print('=' * 50)
    print('규정다름 — MABC 2026 결선 제출물 생성 (강정민 팀)')
    print('=' * 50)
    print()
    
    prd_path = create_prd()
    print()
    
    ppt_path = create_presentation()
    print()
    
    desc_path, char_count = create_description()
    print()
    
    print('=' * 50)
    print('생성 완료 요약')
    print('=' * 50)
    print(f'  PRD PDF:        {prd_path} ({os.path.getsize(prd_path)/1024:.1f} KB)')
    print(f'  발표자료 PDF:   {ppt_path} ({os.path.getsize(ppt_path)/1024:.1f} KB)')
    print(f'  서비스 소개:    {desc_path} ({char_count}자)')
    print()
    print('팀명: 강정민')
    print('서비스 URL: https://mabc-finals.vercel.app')
    print('GitHub: https://github.com/testofschool/mabc2026-gyudung')
