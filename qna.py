# qna.py
import openai
from flask import Blueprint, render_template, request, redirect, url_for,flash
from datetime import datetime
from flask_login import login_required, current_user
from whoosh_helper import search_related_content, extract_keyword 

openai.api_key = "api key"
# 블루프린트 설정
qna_bp = Blueprint('qna', __name__, template_folder='templates/qna')

# QnA 목록 보기
@qna_bp.route('/qna')
def qna_list():
    from app import db_handler  # 이 부분에서 import하여 순환참조 문제를 해결
    qna_list = db_handler.get_qna_list()
    return render_template('qna/qna.html', qna_list=qna_list)

@qna_bp.route('/qna/detail/<int:qna_id>')
def detail_qna(qna_id):
    from app import db_handler
    qna_item = db_handler.get_qna_by_id(qna_id)
    return render_template('qna/detail_qna.html', qna=qna_item)


# QnA 질문 추가
@qna_bp.route('/qna/add', methods=['GET', 'POST'])
def add_qna():
    if request.method == 'POST':
        question = request.form['question']
        author = request.form['author']
        answer =QnA(question)
        from app import db_handler
        db_handler.add_qna(author,question,answer)
        return redirect(url_for('qna.qna_list'))
    return render_template('qna/add_qna.html')


  

#재 답변 저장 후 출력하기
@qna_bp.route('/qna/answer/<int:qna_id>', methods=['POST'])
def answer_qna(qna_id):
    # 질문 내용을 가져와서 GPT를 통해 답변 생성
    question = request.form['question']  # qna_id를 통해 질문을 DB에서 가져올 수도 있음
    answer = QnA(question)
    from app import db_handler
    # DB 핸들러의 update_qna 메소드를 사용하여 답변 업데이트
    db_handler.re_update_qna(qna_id,answer)
    
    return redirect(url_for('qna.qna_list'))

# GPT-3.5를 통해 질문에 대한 답변 생성 함수
def QnA(question):
    # 질문에서 키워드 추출
    keyword = extract_keyword(question)
    
    # Whoosh 검색 호출
    search_results = search_related_content(keyword)
    if not search_results:
        return "관련된 정보를 찾을 수 없습니다."

    # GPT-3.5를 사용해 답변 생성
    prompt = f"다음 내용을 바탕으로 질문에 답해주세요: {search_results[0]}\n\n질문: {question}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 동물보호법률정보의 관리자야. 질문에 대해 양질의 답변을 해"},
            {"role": "user", "content": f"제공된 내용을 참고해서 간략히 요약해서 답변을 제공해: {prompt}"}
        ],
        max_tokens=500,
        temperature=0.5
    )
    return response['choices'][0]['message']['content']

# QnA 수정
@qna_bp.route('/qna/edit/<int:qna_id>', methods=['GET', 'POST'])
def edit_qna(qna_id):
    from app import db_handler
    qna_item = db_handler.get_qna_by_id(qna_id)
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        db_handler.update_qna(qna_id, question, answer)
        return redirect(url_for('qna.qna_list'))
    return render_template('qna/edit_qna.html', qna=qna_item)

# QnA 삭제
@qna_bp.route('/qna/delete/<int:qna_id>', methods=['POST'])
def delete_qna(qna_id):
    from app import db_handler
    db_handler.delete_qna(qna_id)
    return redirect(url_for('qna.qna_list'))

@qna_bp.route('/qna/edit_answer/<int:qna_id>', methods=['GET', 'POST'])
@login_required
def edit_answer(qna_id):
    # 관리자 ID 확인
    if current_user.id != 'test@gmail.com':
        flash("접근 권한이 없습니다.")
        return redirect(url_for('qna/qna.qna_list'))
    from app import db_handler
    # 데이터베이스에서 해당 질문 가져오기
    qna = db_handler.get_qna_by_id(qna_id)
    
    if request.method == 'POST':
        answer = request.form['answer']
        db_handler.update_answer(qna_id, answer, datetime.now())
        return redirect(url_for('qna.qna_list'))
    
    return render_template('qna/edit_answer.html', qna=qna)