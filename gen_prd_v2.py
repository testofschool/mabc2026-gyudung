#!/usr/bin/env python3
"""규정다름 — PRD PDF 생성 (강정민 팀, MABC 2026 결선)"""
from fpdf import FPDF
import os

FONT = '/Users/felix/Library/Fonts/NanumSquareNeoOTF-Rg.otf'
FONT_BOLD = '/Users/felix/Library/Fonts/NanumSquareNeoOTF-Bd.otf'
FONT_HEAVY = '/Users/felix/Library/Fonts/NanumSquareNeoOTF-Hv.otf'

class PRDPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.add_font('NS', '', FONT)
        self.add_font('NS', 'B', FONT_BOLD)
        self.set_auto_page_break(True, 15)

    def header(self):
        if self.page_no() > 1:
            self.set_font('NS', 'B', 7)
            self.set_text_color(120,120,120)
            self.cell(0, 4, '규정다름 — PRD (강정민 팀, MABC 2026 결선)', align='R')
            self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font('NS', '', 7)
        self.set_text_color(120,120,120)
        self.cell(0, 8, f'페이지 {self.page_no()}/{{nb}}', align='C')

    def section(self, title):
        self.ln(4)
        self.set_font('NS', 'B', 13)
        self.set_text_color(26, 39, 68)
        self.cell(0, 7, title)
        self.ln(5)
        self.set_draw_color(26, 39, 68)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(15, y, 195, y)
        self.ln(4)

    def body(self, text, size=9.5):
        self.set_font('NS', '', size)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(1.5)

    def bullet(self, text, indent=5):
        self.set_font('NS', '', 9.5)
        self.set_text_color(50, 50, 50)
        x0 = self.get_x()
        self.cell(indent, 5, '')
        self.cell(4, 5, '•')
        self.multi_cell(190 - indent - 4, 5, text)

    def table_header(self, cols, widths):
        self.set_fill_color(26, 39, 68)
        self.set_text_color(255, 255, 255)
        self.set_font('NS', 'B', 8)
        for i, c in enumerate(cols):
            self.cell(widths[i], 6, ' ' + c, border=0, fill=True)
        self.ln()

    def table_row(self, cells, widths, fill=False):
        if fill:
            self.set_fill_color(240, 243, 248)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_text_color(50, 50, 50)
        self.set_font('NS', '', 8)
        for i, c in enumerate(cells):
            self.cell(widths[i], 5.5, ' ' + c, border=0, fill=True)
        self.ln()


def create_prd():
    pdf = PRDPDF()
    pdf.alias_nb_pages()

    # 표지
    pdf.add_page()
    pdf.ln(35)
    pdf.set_draw_color(26, 39, 68)
    pdf.set_line_width(0.6)
    pdf.line(20, 45, 190, 45)
    pdf.ln(12)
    pdf.set_font('NS', 'H', 26)
    pdf.set_text_color(26, 39, 68)
    pdf.multi_cell(0, 11, '규정다름')
    pdf.ln(4)
    pdf.set_font('NS', 'B', 12)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6, '행정규칙 신·구 조문 대조 및\n시행일 D-day 자동 산출 서비스')
    pdf.ln(12)
    pdf.set_draw_color(26, 39, 68)
    pdf.set_line_width(0.4)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)
    pdf.set_font('NS', 'B', 14)
    pdf.set_text_color(26, 39, 68)
    pdf.cell(0, 9, '팀명: 강정민', align='C')
    pdf.ln(9)
    pdf.set_font('NS', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, 'MABC 2026 결선 제출용', align='C')
    pdf.ln(6)
    pdf.cell(0, 6, '2026.09.16', align='C')

    # 1. 서비스 개요
    pdf.add_page()
    pdf.section('1. 서비스 개요')
    pdf.body('규정다름은 행정규칙·지침·훈령·예규·요령 등 조문 단위로 제·개정되는 문서의 구판(개정 전)과 신판(개정 후) 텍스트를 입력받아, 조문별로 무엇이 신설·변경·삭제되었는지 한눈에 보여주는 대조표와 함께 해당 규정의 시행일과 오늘 기준 D-day/시행상태를 자동으로 계산해 주는 단일 페이지 웹 서비스입니다.')
    pdf.body('공무원, 공공기관 실무자, 연구자 등이 행정규칙 개정 내용을 확인할 때 두 문서를 눈으로 비교하던 수작업을 대체합니다. 특히 부칙에 명시된 시행일을 파싱하여 현재 시점에서의 시행 상태(시행중, D-n, 오늘 시행, 시행일 미검출)를 함께 제공함으로써, 단순한 조문 대조를 넘어 실무적 의사결정을 지원합니다.')

    # 2. 대상 사용자
    pdf.section('2. 대상 사용자')
    pdf.bullet('행정규칙/지침을 다루는 공공기관 실무자 (법무, 감사, 자치행정과, 기획예산과 등)')
    pdf.bullet('규정 개정을 추적해야 하는 내부 감사·준법 담당자')
    pdf.bullet('행정규칙 변경 내용을 신속하게 파악해야 하는 정책 연구자 및 공무원')
    pdf.bullet('법령/행정규칙 비교 작업이 필요한 변호사, 법무사 등 법률 실무자')
    pdf.ln(2)
    pdf.body('핵심 사용 시나리오: 규정 개정 문서(구판·신판)를 수신한 직후, 30초 이내에 어떤 조항이 어떻게 바뀌었는지와 해당 규정의 현재 시행 상태를 동시에 파악한다.')

    # 3. 문제 정의
    pdf.section('3. 문제 정의')
    pdf.body('행정규칙은 현장에서 지속적으로 제·개정되지만, 실무자가 개정 내용을 확인하는 방식은 여전히 두 문서를 출력하여 눈으로 비교하는 수준에 머물러 있습니다.')
    pdf.bullet('국가법령정보센터(law.go.kr)에 법령 비교 기능이 있으나, 행정규칙 전용이 아니고 조문 단위 즉시 대조나 시행일 D-day 계산 기능은 제공되지 않습니다.')
    pdf.bullet('법제처 open API(open.law.go.kr)는 개발자용 조회 기능만 제공할 뿐, 비개발자가 바로 쓸 수 있는 대조표 산출로 이어지지 않습니다.')
    pdf.bullet('실무자는 구판·신판 텍스트를 각각 확보한 뒤 두 문서를 펼쳐놓고 조문별로 변경된 내용을 수동으로 확인하고, 별도로 해당 규정의 시행일을 조회해야 합니다.')
    pdf.body('규정 개정 빈도가 높은 기관일수록 이 부담은 커집니다.')

    # 4. 해결 방안
    pdf.section('4. 해결 방안')
    pdf.body('규정다름은 위 문제를 다음 기능으로 해결합니다.')
    pdf.ln(1)
    pdf.table_header(['기능', '설명', '기존 대비 우위'], [32, 88, 60])
    pdf.table_row(['조문 대조', '구판·신판 텍스트를 붙여넣으면 스크립트가 조항 단위로 added/modified/deleted를 자동 판정', '눈으로 비교하는 수작업 대체, 수초 내 완료'], [32, 88, 60], fill=True)
    pdf.table_row(['시행일 D-day', '부칙 시행일 문구를 파싱하여 오늘(KST) 기준 D-day/시행상태를 자동 산출', '별도 조회 없이 시행 상태 즉시 확인'], [32, 88, 60])
    pdf.table_row(['스크립트 기반 계산', 'diff 판정, 시행일 파싱, D-day 계산 모두 Python 스크립트가 수행 (LLM 임의 추정 없음)', '계산 과정의 투명성·재현성 확보'], [32, 88, 60], fill=True)
    pdf.table_row(['즉시 사용 가능', 'API 키 없이 웹 브라우저에서 바로 사용. 로그인·회원가입 불필요', '개방형 접근성, 진입 장벽 최소화'], [32, 88, 60])

    # 5. 동작 방식
    pdf.section('5. 동작 방식 (입력 → 처리 → 출력)')
    pdf.body('5.1 입력', 10)
    pdf.bullet('사용자가 구판 텍스트와 신판 텍스트를 각 텍스트 영역에 붙여넣습니다.')
    pdf.bullet('텍스트는 행정규칙/지침/훈령/예규/요령 등의 전문이며, 조문 번호(제N조)와 부칙 시행일이 포함되어야 합니다.')
    pdf.bullet('샘플 불러오기 버튼으로 데모용 구판(시립도서관 자료실 운영 지침, 2026.3.1. 시행)과 신판(2026.9.15. 시행) 텍스트를 바로 입력할 수 있습니다.')
    pdf.ln(1)
    pdf.body('5.2 처리', 10)
    pdf.bullet('[대조 실행] 버튼을 누르면 구판·신판 텍스트가 JSON 형태로 Vercel 서버리스 API(/api/admrul-diff)에 POST 전송됩니다.')
    pdf.bullet('서버에서는 admrul-diff 스크립트(admrul_diff.py와 동일 로직)가 다음 계산을 수행합니다:')
    pdf.bullet('텍스트에서 제N조 패턴으로 모든 조문을 파싱', indent=8)
    pdf.bullet('구판·신판 조문을 비교하여 added/modified/deleted 판정', indent=8)
    pdf.bullet('부칙 시행일 문구를 정규식으로 파싱하여 시행일자 추출', indent=8)
    pdf.bullet('오늘(KST) 기준 시행일자와 비교하여 D-day/시행상태 산출', indent=8)
    pdf.bullet('모든 계산과 판정은 스크립트가 수행하며, LLM이 임의 추정하지 않습니다.')
    pdf.ln(1)
    pdf.body('5.3 출력', 10)
    pdf.bullet('신·구 조문 대조표: 변경 유형(신설/변경/삭제) 배지, 조문 번호·제목, 구판 내용, 신판 내용을 표로 표시')
    pdf.bullet('시행 D-day 표: 구판·신판 각각의 시행일, 기준일자, 시행상태(D-n/오늘 시행/시행중/시행일 미검출)를 표시')
    pdf.bullet('각 표의 하단에 JSON 보기 토글 버튼이 있어 원본 계산 결과를 확인 가능')
    pdf.bullet('변경된 조문이 없으면 변경 조문이 없다는 메시지 표시')

    # 6. 기술 아키텍처
    pdf.section('6. 기술 아키텍처')
    pdf.table_header(['구성 요소', '기술 스택', '역할'], [38, 55, 87])
    pdf.table_row(['프론트엔드', '단일 HTML + Vanilla JS (CSS 변수 기반)', '사용자 입력 수신, API 호출, 결과 표 렌더링'], [38, 55, 87], fill=True)
    pdf.table_row(['백엔드 API', 'Python (WSGI), Vercel 서버리스', '텍스트 수신, diff 계산, 시행일 파싱, D-day 산출, JSON 응답'], [38, 55, 87])
    pdf.table_row(['핵심 로직', 'admrul-diff 스크립트 (Python stdlib)', '조문 파싱, diff 판정, 시행일 파싱, D-day 계산 — 모든 계산 수행'], [38, 55, 87], fill=True)
    pdf.table_row(['배포', 'Vercel (정적 사이트 + 서버리스 함수)', '전 세계 CDN, HTTPS, 스케일 투 제로'], [38, 55, 87])
    pdf.table_row(['데이터 저장', '없음 (무상태)', '모든 계산은 요청 시점 메모리에서 수행, 데이터 저장하지 않음'], [38, 55, 87], fill=True)

    # 7. 차별화
    pdf.section('7. 차별화 및 경쟁 우위')
    pdf.table_header(['비교 항목', '규정다름', '국가법령정보센터', '법제처 open API'], [28, 52, 55, 55])
    pdf.table_row(['접근 방식', '텍스트 붙여넣기 즉시', '웹사이트 탐색 후 비교 메뉴', 'API 호출 (개발자용)'], [28, 52, 55, 55], fill=True)
    pdf.table_row(['행정규칙 대응', '전용 (모든 행정문서 형식)', '법령 중심, 행정규칙 제한적', '행정규칙 조회 가능'], [28, 52, 55, 55])
    pdf.table_row(['조문 단위 대조표', '자동 생성 (added/modified/deleted)', '3단 비교 등 별도 기능', '별도 구현 필요'], [28, 52, 55, 55], fill=True)
    pdf.table_row(['시행일 D-day 계산', '자동 산출 (오늘 기준)', '제공 안 함', '제공 안 함'], [28, 52, 55, 55])
    pdf.table_row(['사용 자격', '누구나 (로그인 불필요)', '누구나', 'API 키 필요'], [28, 52, 55, 55], fill=True)
    pdf.table_row(['계산 신뢰성', '스크립트 기반 (LLM 추정 없음)', '공식 시스템', '공식 데이터'], [28, 52, 55, 55])

    # 8. 향후 발전 방향
    pdf.section('8. 향후 발전 방향')
    pdf.bullet('파일 업로드 지원: 텍스트 붙여넣기 외에 PDF/문서 파일 업로드로 직접 대조')
    pdf.bullet('국가법령정보센터/open API 연동: 행정규칙 원문을 자동 조회하여 비교')
    pdf.bullet('비교 결과 저장·공유: 대조 결과 링크를 생성하거나 PDF로 export')
    pdf.bullet('다크 모드 지원: CSS 변수 기반 테마 전환')
    pdf.bullet('다국어 지원: 한국어 외 영문 행정규칙 대조 확장')
    pdf.bullet('기관별 알림: 관심 규정의 개정 발생 시 알림 (옵트인 기반)')

    # 9. 팀 정보
    pdf.section('9. 팀 정보')
    pdf.table_header(['항목', '내용'], [35, 145])
    pdf.table_row(['팀명', '강정민'], [35, 145], fill=True)
    pdf.table_row(['참가자', '강정민 (단독)'], [35, 145])
    pdf.table_row(['플랫폼', 'Hermes Agent'], [35, 145], fill=True)
    pdf.table_row(['서비스 URL', 'https://mabc-finals.vercel.app'], [35, 145])
    pdf.table_row(['GitHub', 'https://github.com/testofschool/mabc2026-gyudung'], [35, 145], fill=True)
    pdf.table_row(['핵심 기술', 'Python (admrul-diff), Vercel 서버리스, HTML/CSS/JS'], [35, 145])

    output_path = '/Users/felix/mabc-finals/강정민_PRD.pdf'
    pdf.output(output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print(f'✅ 강정민_PRD.pdf 생성 완료: {size_kb:.1f} KB ({pdf.page_no()}페이지)')
    return output_path


if __name__ == '__main__':
    create_prd()
