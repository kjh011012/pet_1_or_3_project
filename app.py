from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, session
import os
from dbhandle import db_handle
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from faiss_gpt_law import get_answer  # NLP 및 LLM을 처리하는 모듈 임포트
from datetime import timedelta
import re
from faissgpt import QnA_with_RAG
from werkzeug.utils import secure_filename
from qna import qna_bp
from menubar import menubar_bp
from emergency import emergency_bp
from search_routes import search_bp
from recommend import recommend_bp
from travel_with_pet import travel_bp
from health import health_bp


app = Flask(__name__)

#블루 프린터를 이용한 app.py연결
app.register_blueprint(qna_bp)
app.register_blueprint(menubar_bp)
app.register_blueprint(emergency_bp)
app.register_blueprint(search_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(travel_bp)
app.register_blueprint(health_bp)
db_handler = db_handle('user', 'pw', 'localhost', 'dbname')


app.config['SECRET_KEY'] = 'scret_key'  # 세션 및 CSRF 보호를 위한 비밀 키 설
app.config['SESSION_TYPE'] = 'filesystem'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=10)#10분동안 로그인상태 유지
app.config['SESSION_COOKIE_SECURE'] = False #기본True(https로 접근만 허용)
Session(app)

# 업로드 폴더 설정
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask-Login 설정
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 사용자 클래스 정의
class User(UserMixin):
    def __init__(self, email):
        self.id = email  # Flask-Login은 'id' 속성을 사용해 세션 관리

# 사용자가 인증될 때 호출되는 함수
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    # db_handler 인스턴스 생성 및 데이터 가져오기
    lost_pets = db_handler.pet_serach_data_load()  # DB에서 잃어버린 반려동물 데이터를 가져옴
    return render_template('main.html', lost_pets=lost_pets)
@app.route('/chat')
def chat():
    return render_template('chat.html')
    
# 잃어버린 우리 아이 찾기 등록 페이지 라우트

@app.route('/find_lost_pet')
def find_lost_pet():
    pets = db_handler.pet_serach_data_load()  # db_handler 인스턴스 생성

    
    if not pets:  # 데이터가 없을 경우
        print("No pets data available.")
    
    return render_template('find_lost_pet.html', pets=pets)  # 데이터를 HTML로 전달


# 우리 아이 먹거리 페이지 라우트
@app.route('/pet_training')
def pet_training():
    return render_template('pet_training.html')

# 아이와 함께 여행을 페이지 라우트
@app.route('/travel_with_pet')
def travel_with_pet():
    return render_template('travel_with_pet.html')

# 가까운 동물 병원 찾기 페이지 라우트
@app.route('/find_vet')
def find_vet():
    return render_template('find_vet.html')

# 임시 보호 신청 페이지 라우트
@app.route('/temporary_shelter')
def temporary_shelter():
    return render_template('temporary_shelter.html')

# 유기견 입양 신청 페이지 라우트
@app.route('/adopt_pet')
def adopt_pet():
    return render_template('adopt_pet.html')


# 동물보호 법률정보 페이지 라우트
@app.route('/law')
def law():
    return render_template('law.html')
"""
@app.route('/law_input', methods=['POST'])
def law_input():
    # law.html에서 입력받은 키워드를 세션에 저장
    keyword1 = request.form['keyword1']
    keyword2 = request.form['keyword2']
    session['keywords'] = (keyword1, keyword2)
    return render_template('law_input.html')
"""
@app.route('/law_chat', methods=['POST'])
def law_chat():
    data = request.get_json()
    message = data.get("message")
    region = data.get("region")
    category = data.get("category")

    # FAISS 및 LLM을 이용해 답변 생성
    # 예시 함수: QnA_with_RAG
    response_text = QnA_with_RAG(f"{region} {category}에 관한 질문: {message}")

    return jsonify({"response": response_text})
"""
@app.route('/law_response', methods=['POST'])
def law_response():
    # law_input.html에서 사용자가 입력한 질문과 세션에 저장된 키워드 두 개를 사용하여 답변 생성
    user_question = request.form['user_question']
    keyword1, keyword2 = session.get('keywords', ('', ''))
    # NLP로 키워드 분석 후 벡터 DB 검색 및 LLM을 사용해 답변 생성
    answer = get_answer(keyword1, keyword2, user_question)
    return render_template('law_input.html', answer=answer)
"""

# 데이터셋 로드
db_sqllode = db_handler.petchat_select_data_lode()
df = pd.DataFrame(db_sqllode)

# 데이터셋 컬럼 확인
print("Columns in dataframe:", df.columns)  # 이 부분을 로그에 추가
print("First few rows:", df.head())  # 데이터 첫 몇 줄 확인

# 드롭다운 옵션을 위한 고유 값 추출
gender_options = df['gender'].unique().tolist()
pet_gender_options = df['pet_gender'].unique().tolist()
pet_type_options = df['pet_type'].unique().tolist()

# 로그인 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']
        
        # dbhandler를 통해 이메일로 사용자 정보 가져오기
        user_data = db_handler.pet_login_load()
        user = next((u for u in user_data if u['email'] == email), None)
        
        if user:
            if check_password_hash(user['password'], password):
                # 세션에 사용자 정보 저장
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['pername'] = user['pername']
                session['age'] = user['age']
                session['gender'] = user['gender']
                session['tel'] = user['tel']
                session['pet_name'] = user['pet_name']
                session['pet_breed'] = user['pet_breed']
                session['pet_age'] = user['pet_age']
                session['pet_gender'] = user['pet_gender']
                session['pet_type'] = user['pet_type']
                
                login_user(User(user['email']))  # Flask-Login 사용
                return redirect(url_for('main'))
            else:
                error = '비밀번호가 일치하지 않습니다.'
        else:
            error = '해당 이메일을 가진 사용자가 존재하지 않습니다.'
    
    return render_template('login.html', error=error)

# 회원가입 라우트
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('signup'))
    
    if request.method == 'POST':
        age = request.form['age_select']
        gender = request.form['gender_select']
        tel = request.form['tel']
        pername = request.form['pername']
        email = request.form['Email']
        password = request.form['Password']
        pet_type = request.form['pet_type_select']
        pet_name = request.form['pet_name']
        pet_gender = request.form['pet_gender_select']
        pet_age = request.form['pet_age']
        pet_breed = request.form['pet_breed']

        # 비밀번호 해시 처리
        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        # DB에 사용자 정보 삽입
        db_handler.pet_login_insert(email,password,pername,age,gender,tel,pet_name,pet_breed,pet_age,pet_gender,pet_type)

        return redirect(url_for('login'))

    return render_template('signup.html', 
                           gender_options=gender_options, 
                           pet_gender_options=pet_gender_options,
                           pet_type_options=pet_type_options)

#잃어버린 반려동물 찾기 업로드
@app.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        pet_type = request.form['pet_type']
        breed = request.form['breed']
        feature = request.form['feature']
        
        personality = request.form['personality']
        favorite_things = request.form['favorite']
        lost_location = request.form['lost_location']

        # 사진 파일 처리
        photo_path = ''  # 기본적으로 빈 문자열을 설정
        photo = request.files.get('photo')  # 'photo' 필드에서 사진 파일을 가져옴
        if photo:
            filename = secure_filename(photo.filename)  # 파일명 안전하게 변환
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # 경로 설정
            photo.save(photo_path)  # 지정된 경로에 사진 저장

        # 데이터베이스에 반려동물 정보 삽입
        
        db_handler.pet_serach_data_insert(name, age, gender,pet_type,breed,feature, personality, favorite_things, lost_location, photo_path)
        
        return redirect(url_for('find_lost_pet'))

    return render_template('add_pet.html')



# POST 요청으로 사용자 질문을 받아 처리
@app.route('/chat', methods=['POST'])
def chat_bot():
    data = request.get_json()
    user_message = data.get('message')
    
    # faissgpt의 QnA_with_RAG 함수 호출
    response_message = QnA_with_RAG(user_message)

    return jsonify({'response': response_message})






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
