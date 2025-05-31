import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

class db_handle:
    def __init__(self, user, password, host, database):
        self.db_config = {
            'user': user,
            'password': password,
            'host': host,
            'database': database
        }

    def get_db_connection(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"Error: {e}")
            return None

    def pet_login_insert(self,email,password,pername,age,gender,tel,pet_name,pet_breed,pet_age,pet_gender,pet_type):
        #회원가입 테이블(insert)
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return
        
        try:
            cursor = db.cursor()
            query = """
            INSERT INTO pet_login (email,password,pername,age,gender,tel,pet_name,pet_breed,pet_age,pet_gender,pet_type) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            """
            cursor.execute(query, (email,password,pername,age,gender,tel,pet_name,pet_breed,pet_age,pet_gender,pet_type))
            db.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            db.close()
    
    #회원가입 및 로그인 테이블(로드)
    def pet_login_load(self):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT * FROM pet_login"
            cursor.execute(query)
            petchat = cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            petchat = []
        finally:
            cursor.close()
            db.close()
        
        return petchat

    def petchat_select_data_lode(self):
        #데이터셋 로드용(회원가입 및 로그인 테이블 gender,pet_gender, pet_type)
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT gender,pet_gender,pet_type FROM pet_login"
            cursor.execute(query)
            petchat = cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            petchat = []
        finally:
            cursor.close()
            db.close()
        
        return petchat


    #나의정보 수정용
    def load_user_info(self, email):
    # 데이터베이스 연결 설정
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return None

        try:
            cursor = db.cursor()
        
        # 사용자 정보 가져오는 쿼리
            query = "SELECT pername, age, gender, tel, pet_name, pet_breed, pet_age, pet_gender, pet_type FROM pet_login WHERE email = %s"
        
        # 쿼리 실행
            cursor.execute(query, (email,))
        
        # 사용자 정보 가져오기
            user_info = cursor.fetchone()
        
        # 정보가 없을 경우 None 반환
            if user_info is None:
                print("User not found.")
                return None
        
        # 딕셔너리로 변환
            return {
            "pername": user_info[0],
            "age": user_info[1],
            "gender": user_info[2],
            "tel": user_info[3],
            "pet_name": user_info[4],
            "pet_breed": user_info[5],
            "pet_age": user_info[6],
            "pet_gender": user_info[7],
            "pet_type": user_info[8]
        }
        
        except Exception as e:
            print(f"Error loading user info: {e}")
            return None
        finally:
            cursor.close()
            db.close()


#=================================================================================
    def pet_serach_data_insert(self,name, age, gender, pet_type,breed,feature, personality, favorite_things, lost_location, photo_path):
        #잃어버린 강아지찾기 등록 테이블
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return
        
        try:
            cursor = db.cursor()
            query = """
            INSERT INTO pet_search_data (name, age, gender, pet_type,breed,feature, personality, favorite_things, lost_location, photo_path) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)

            """
            cursor.execute(query, (name, age, gender, pet_type,breed,feature, personality, favorite_things, lost_location, photo_path))
            db.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            db.close()
 
    
    #잃어 버린 강아지 찾기 로드 테이블
    def pet_serach_data_load(self):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT name,age,gender,breed,lost_location,personality,photo_path FROM pet_search_data"
            cursor.execute(query)
            petchat = cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            petchat = []
        finally:
            cursor.close()
            db.close()
        
        return petchat
    
    
 #==============================================================================================   
    #qna게시판
    def get_qna_list(self):
        connection = self.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM qna_board ORDER BY created_at DESC"
        cursor.execute(query)
        qna_list = cursor.fetchall()
        cursor.close()
        connection.close()
        return qna_list

    # QnA 추가
    def add_qna(self,author, question,answer):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO qna_board (author,question,answer) VALUES (%s,%s,%s)"
        cursor.execute(query, (author,question,answer))
        connection.commit()
        cursor.close()
        connection.close()

    # QnA ID로 특정 질문 가져오기
    def get_qna_by_id(self, qna_id):
        connection = self.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM qna_board WHERE id = %s"
        cursor.execute(query, (qna_id,))
        qna_item = cursor.fetchone()
        cursor.close()
        connection.close()
        return qna_item

    # QnA 수정
    def update_qna(self, qna_id, question, answer):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        query = "UPDATE qna_board SET question = %s, answer = %s WHERE id = %s"
        cursor.execute(query, (question, answer, qna_id))
        connection.commit()
        cursor.close()
        connection.close()
    
    # QnA 답변하기 수정
    def re_update_qna(self, qna_id,answer):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        query = "UPDATE qna_board SET answer = %s WHERE id = %s"
        cursor.execute(query, (answer, qna_id))
        connection.commit()
        cursor.close()
        connection.close()

    # QnA 삭제
    def delete_qna(self, qna_id):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        query = "DELETE FROM qna_board WHERE id = %s"
        cursor.execute(query, (qna_id,))
        connection.commit()
        cursor.close()
        connection.close()

   