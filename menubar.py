from flask import Blueprint, render_template, redirect, url_for,session,flash,request,jsonify
import requests
from googletrans import Translator


# menubar 블루프린트 생성
menubar_bp = Blueprint('menubar', __name__, template_folder='templates/menubar')

# 공지사항 페이지 라우트
@menubar_bp.route('/Noticeboard')
def Noticeboard():
    return render_template('Noticeboard.html')

# 자유게시판 페이지 라우트
@menubar_bp.route('/Free_bulletin_board')
def Free_bulletin_board():
    return render_template('Free_bulletin_board.html')


# The Dog API 설정
API_KEY = "api key"
BASE_URL = "https://api.thedogapi.com/v1/breeds"

@menubar_bp.route('/api/get_breeds_dog')
def get_breeds_dog():
    headers = {"x-api-key": API_KEY}
    response = requests.get(BASE_URL, headers=headers)
    
    if response.status_code == 200:
        breeds = response.json()
        breed_data = []

        for breed in breeds:
            breed_data.append({
                "name": breed['name'],
                "life_span": breed.get('life_span', 'N/A'),
                "temperament": breed.get('temperament', 'N/A'),
                "weight": f"{breed['weight']['metric']} kg",
                "height": f"{breed['height']['metric']} cm",
                "image": breed['image']['url'] if 'image' in breed else ''
            })
        
        return jsonify(breed_data)
    else:
        return jsonify({"error": "Failed to fetch breeds"}), response.status_code


# Cat API 설정
API_KEY2 = "api key"
CAT_BASE_URL = "https://api.thecatapi.com/v1/breeds"

@menubar_bp.route('/api/get_breeds_cat')
def get_breeds_cat():
    headers = {"x-api-key": API_KEY2}
    response = requests.get(CAT_BASE_URL, headers=headers)
    
    if response.status_code == 200:
        breeds = response.json()
        breed_data = []

        for breed in breeds:
            breed_data.append({
                "name": breed['name'],
                "life_span": breed.get('life_span', 'N/A'),
                "temperament": breed.get('temperament', 'N/A'),
                "weight": f"{breed['weight']['metric']} kg" if 'weight' in breed else 'N/A',
                "height": f"{breed['height']['metric']} cm" if 'height' in breed else 'N/A',
                "image": breed.get('image', {}).get('url', '')
            })
        
        return jsonify(breed_data)
    else:
        return jsonify({"error": "Failed to fetch breeds"}), response.status_code

# 견종백과 페이지 라우트
@menubar_bp.route('/encyclopedia')
def encyclopedia():
    return render_template('encyclopedia.html')
# 견종백과 페이지 라우트
@menubar_bp.route('/dog')
def dog():
    return render_template('dog.html')
# 견종백과 페이지 라우트
@menubar_bp.route('/cat')
def cat():
    return render_template('cat.html')



# "나의 정보" 페이지 라우트
@menubar_bp.route('/setting', methods=['GET'])
def setting():
    from app import db_handler
    if 'email' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))
    
    # 사용자 정보 로드
    user_info = db_handler.load_user_info(session['email'])
    
    if user_info is None:
        flash("사용자 정보를 불러오지 못했습니다.")
        return redirect(url_for('main'))
    
    return render_template('setting.html', user_info=user_info)

# 로그아웃 페이지 라우트
@menubar_bp.route('/logout')
def logout():
    # 세션 초기화
    session.clear()
    # 로그아웃 메시지와 함께 로그아웃 페이지로 이동
    return render_template('logout.html')


# 공지사항 글쓰기
@menubar_bp.route('/write_post', methods=['GET', 'POST'])
def write_post():
    if request.method == 'POST':
        # 글쓰기 폼 데이터 처리 로직
        title = request.form['title']
        content = request.form['content']
        # 데이터베이스에 제목과 내용을 저장하는 코드 추가

        flash("글이 성공적으로 작성되었습니다.")
        return redirect(url_for('menubar.noticeboard'))  # 공지사항 목록 페이지로 이동

    # 글쓰기 페이지 렌더링 (폼 포함)
    return render_template('write_post.html')



   


   
    
