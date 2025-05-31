from mysql.connector import connect
from werkzeug.security import generate_password_hash
from dbhandle import db_handle

# 데이터베이스 연결 설정
db_handler = db_handle('user', 'pw', 'localhost', 'dbname')

# 비밀번호 해시화 함수
def hash_passwords():
    try:
        # 데이터베이스 연결
        conn = db_handler.get_db_connection()
        cursor = conn.cursor()

        # "1234" 비밀번호를 가진 모든 사용자 찾기
        query_select = "SELECT id, Password FROM hackerthon2 WHERE Password = %s"
        cursor.execute(query_select, ("1234",))
        users = cursor.fetchall()

        # 비밀번호 해시화 및 업데이트
        for user in users:
            user_id = user[0]
            hashed_password = generate_password_hash(user[1])

            # 해시화된 비밀번호 업데이트 쿼리
            query_update = "UPDATE hackerthon2 SET Password = %s WHERE id = %s"
            cursor.execute(query_update, (hashed_password, user_id))

        # 변경사항 커밋
        conn.commit()

        print(f"{cursor.rowcount} passwords updated successfully.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

# 실행
if __name__ == "__main__":
    hash_passwords()
