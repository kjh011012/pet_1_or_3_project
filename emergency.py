# emergency.py에서 라우트 코드
from flask import Blueprint, request, render_template, redirect, url_for, flash,send_file, make_response, jsonify, session
from emergencydbhandle import SymptomDB
from efp2 import QnA_with_RAG, search_similar_document  # GPT와 벡터 DB 활용 함수
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, KeepInFrame,Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.lib import colors
import os

# 블루프린트 등록
emergency_bp = Blueprint('emergency', __name__)
symptom_db = SymptomDB(user='user', password='pw', host='localhost', database='dbname')


@emergency_bp.route('/get_symptom_hierarchy', methods=['POST'])
def get_symptom_hierarchy():
    species = request.form.get('species')
    main_symptom_id = request.form.get('mainSymptom')
    sub_symptom_id = request.form.get('subSymptom')

    # 종별 대분류 데이터 불러오기
    symptoms = symptom_db.load_symptom_hierarchy(species=species)
    selected_main_symptom = None
    selected_sub_symptom = None

    if main_symptom_id:
        for main in symptoms:
            if main["대분류"]["id"] == int(main_symptom_id):
                selected_main_symptom = main
                break

    if selected_main_symptom and sub_symptom_id:
        for sub in selected_main_symptom["중분류"]:
            if sub["중분류"]["id"] == int(sub_symptom_id):
                selected_sub_symptom = sub
                break

    return render_template(
        'temporary_shelter.html',
        species=species,
        symptoms=symptoms,
        mainSymptom=main_symptom_id,
        subSymptoms=selected_main_symptom["중분류"] if selected_main_symptom else None,
        subSymptom=sub_symptom_id,
        detailedSymptoms=selected_sub_symptom["소분류"] if selected_sub_symptom else None
    )

@emergency_bp.route('/submit_response', methods=['POST'])
def submit_response():
    main_symptom_id = request.form.get("mainSymptom")
    sub_symptom_id = request.form.get("subSymptom")
    detailed_symptom_id = request.form.get("detailedSymptom")

    # ID 대신 이름을 가져오기
    main_symptom_name = symptom_db.get_symptom_name_by_id(main_symptom_id)
    sub_symptom_name = symptom_db.get_symptom_name_by_id(sub_symptom_id)
    detailed_symptom_name = symptom_db.get_symptom_name_by_id(detailed_symptom_id)

    # 유사 응급조치 설명 검색 (이름으로 검색)
    similar_doc_content = search_similar_document(main_symptom_name, sub_symptom_name, detailed_symptom_name)

    # GPT에 유사 문서 내용 전달 후 최종 응급조치 답변 생성
    final_response = QnA_with_RAG(main_symptom_name, sub_symptom_name, detailed_symptom_name) if similar_doc_content else "응급조치 정보를 찾지 못했습니다."

    if not final_response:
        flash("응급조치 생성에 실패했습니다.")
        return redirect(url_for('emergency.get_symptom_hierarchy'))

    # 응급조치 최종 응답을 DB에 저장 (ID 대신 이름으로 저장)
    symptom_db.insert_emergency_response(main_symptom_name, sub_symptom_name, detailed_symptom_name, final_response)

    # 최종 응답을 세션에 저장
    session['final_response'] = final_response

    # 최종 응답을 템플릿에 렌더링
    return render_template('temporary_shelter.html', final_response=final_response)

 

@emergency_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    final_response = session.get('final_response')

    if not final_response:
        flash("응급조치 결과가 없습니다.")
        return redirect(url_for('emergency.get_symptom_hierarchy'))

    # PDF 파일을 메모리에 생성
    pdf_buffer = BytesIO()
    pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # 한글 폰트 등록
    font_path = os.path.join("fonts", "NanumBarunGothic.ttf")
    pdfmetrics.registerFont(TTFont("NanumBarunGothic", font_path))

    # 스타일 정의
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', fontName='NanumBarunGothic', fontSize=18, leading=22, alignment=1, textColor=colors.HexColor("#FF6B6B")))  # 중앙 정렬, 색상 적용
    styles.add(ParagraphStyle(name='CustomBody', fontName='NanumBarunGothic', fontSize=12, leading=18, textColor=colors.HexColor("#333333")))  # 본문 스타일

    # 제목과 응급조치 결과 텍스트를 Paragraph로 생성
    title = Paragraph("응급조치 결과", styles['CustomTitle'])
    response_text = Paragraph(final_response, styles['CustomBody'])

    # 테두리 설정을 위한 Table 생성
    data = [[title], [Spacer(1, 0.3 * inch)], [response_text]]
    table = Table(data, colWidths=[5.5 * inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#FF6B6B")),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor("#FF6B6B")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FFF5F5"))
    ]))

    # PDF 내용 구성
    content = [
        Spacer(1, 0.5 * inch),  # 위쪽 여백
        table,
        Spacer(1, 0.5 * inch)   # 아래쪽 여백
    ]

    # PDF 생성
    pdf_doc.build(content)

    # PDF 파일을 다운로드로 전송
    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=emergency_response.pdf'
    return response