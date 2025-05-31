from flask import Blueprint, render_template, request
from traveldbhandle import travel_db_handle

# 검색 블루프린트 생성
search_bp = Blueprint('search', __name__, url_prefix='/search')

# DB 핸들러 초기화 (DB 연결 정보는 환경에 맞게 수정)
db = travel_db_handle(user='user', password='pw', host='localhost', database='dbname')

@search_bp.route('/places', methods=['GET', 'POST'])
def search_places():
    province = request.form.get('province')
    city = request.form.get('city')
    category = request.form.get('category')

    # 1차 선택: province 목록을 가져오기
    if not province:
        provinces = db.load_provinces()
        return render_template('search_places.html', provinces=provinces)

    # 2차 선택: 특정 province에 대한 city 목록을 가져오기
    elif not city:
        cities = db.load_cities(province)
        return render_template('search_places.html', province=province, cities=cities)

    # 3차 선택: 특정 province와 city에 대한 category 목록을 가져오기
    elif not category:
        categories = db.load_categories(province, city)
        return render_template('search_places.html', province=province, city=city, categories=categories)

    # 모든 선택 완료 후: 추천 장소 로드
    else:
        search_result = db.load_recommendations(province, city, category)
        return render_template('search_results.html', places=search_result)

    # 데이터베이스에서 추천 장소 데이터 로드



