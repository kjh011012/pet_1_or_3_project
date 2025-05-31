import openai
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from markupsafe import Markup
import os
import re
import pandas as pd

app = Flask(__name__)
# 전역 변수로 현재 대응 매뉴얼을 저장



# OpenAI API 키 설정
openai.api_key = "api key"



def QnA(question,input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 반려동물 전문가야.다음 내용을 참고해서 고객에게 정보를 제공해."},
            {"role": "user", "content": f"다음은 고객의 질문이야 이내용을 참고해서 상세한 답변을 제공해: {question}"},
        ],
        max_tokens=1000,
        temperature=0.5
    )
    return response.choices[0].message['content'].strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    if request.method == 'POST':
        question = request.form['question']
        answer = QnA(question)
        
    
    return render_template('index.html', answer=answer)
    
# 문단 및 문장 단위로 줄바꿈을 적용하는 nl2br 필터
@app.template_filter('nl2br')
def nl2br(value):
    # value가 None인 경우 빈 문자열로 처리
    if value is None:
        return ""
    
    # 문단을 줄바꿈 문자(\n)로 나눕니다.
    paragraphs = value.split('\n\n')
    formatted_paragraphs = []

    # 각 문단을 처리
    for paragraph in paragraphs:
        # 문장 단위로 마침표, 물음표, 느낌표 뒤에 <br> 추가
        sentences = re.split(r'([!?])', paragraph)
        formatted_paragraph = "".join([sentence + ('<br>' if sentence in '.!?' else '') for sentence in sentences])
        formatted_paragraphs.append(formatted_paragraph)

    # 문단 사이에 <br><br>을 추가하여 문단 구분
    result = "<br><br>".join(formatted_paragraphs)
    return Markup(result)

if __name__ == '__main__':
    # IoT 데이터 시뮬레이션을 백그라운드 스레드로 실행

    app.run(host='0.0.0.0', port=5002, debug=True)