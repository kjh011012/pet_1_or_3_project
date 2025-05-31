from flask import Blueprint, render_template, request
from traveldbhandle import travel_db_handle

# Health 블루프린트 생성
health_bp = Blueprint('health', __name__, url_prefix='/health')

# DB 핸들러 초기화 (DB 연결 정보는 환경에 맞게 수정)
db = travel_db_handle(user='user', password='pw', host='localhost', database='dbname')

@health_bp.route('/find_vet_pharmacy', methods=['GET', 'POST'])
def find_vet_pharmacy():
    province = request.form.get('province')
    city = request.form.get('city')

    # 1차 선택: province 목록을 가져오기
    if not province:
        provinces = db.load_provinces3()
        return render_template('find_vet_pharmacy.html', provinces=provinces)

    # 2차 선택: 특정 province에 대한 city 목록을 가져오기
    elif not city:
        cities = db.load_cities3(province)
        return render_template('find_vet_pharmacy.html', province=province, cities=cities)


    # 모든 선택 완료 후: 동물병원 및 동물약국 로드
    else:
        vet_pharmacy_results = db.load_recommendations3(province, city)
        return render_template('vet_pharmacy_results.html', places=vet_pharmacy_results)
