from flask import Blueprint, render_template

# travel 블루프린트 생성
travel_bp = Blueprint('travel', __name__)

# 메인 페이지 라우트 설정
@travel_bp.route('/travel')
def travel_home():
    return render_template('travel_with_pet.html')
