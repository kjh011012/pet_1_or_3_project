import mysql.connector
from mysql.connector import Error


class SymptomDB:
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

    # 대분류, 중분류, 소분류 삽입 함수
    def insert_symptom(self,species, level, name, description, parent_id=None):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return None
        
        try:
            cursor = db.cursor()
            query = """
                INSERT INTO SymptomHierarchy (parent_id,species, level, name, description, first_response, user_feedback)
                VALUES (%s, %s, %s, %s, NULL, NULL)
            """
            cursor.execute(query, (parent_id,species, level, name, description))
            db.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    # 1차 답변 생성 및 저장
    def generate_first_response(self, symptom_id, symptom_data):
        # 벡터 DB와 GPT를 통해 1차 응답 생성 - 예시
        vector_response = self.find_similar_case(symptom_data)
        gpt_response = self.get_gpt_response(vector_response)

        # 1차 답변 컬럼에 저장
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = db.cursor()
            query = "UPDATE SymptomHierarchy SET first_response = %s WHERE id = %s"
            cursor.execute(query, (gpt_response, symptom_id))
            db.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()
            db.close()

 

    # 사용자 피드백 저장
    def save_user_feedback(self, symptom_id, feedback):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = db.cursor()
            query = "UPDATE SymptomHierarchy SET user_feedback = %s WHERE id = %s"
            cursor.execute(query, (feedback, symptom_id))
            db.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()
            db.close()
    

    def save_final_response(self, symptom_id, final_response):
        """
        최종 답변을 SymptomHierarchy 테이블의 final_response 컬럼에 저장
        """
        db = self.get_db_connection()

        if db is None:
            print("Failed to connect to the database.")
            return False
        
        try:
            cursor = db.cursor()
            query = "UPDATE SymptomHierarchy SET final_response = %s WHERE id = %s"
            cursor.execute(query, (final_response, symptom_id))
            db.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()
            db.close()

    # 종에 따라 대분류, 중분류, 소분류 필터링하는 메서드 추가
    def load_symptoms_by_level(self, level, parent_id=None, species=None):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            if parent_id is None:
                query = "SELECT * FROM SymptomHierarchy WHERE level = %s AND species = %s AND parent_id IS NULL"
                cursor.execute(query, (level, species))
            else:
                query = "SELECT * FROM SymptomHierarchy WHERE level = %s AND species = %s AND parent_id = %s"
                cursor.execute(query, (level, species, parent_id))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    # 계층적 구조 불러오기 메서드
    def load_symptom_hierarchy(self, species):
    # 대분류 불러오기
        categories = self.load_symptoms_by_level(level='대분류', species=species)
        hierarchy = []

        print("대분류 카테고리:", categories)  # 대분류 데이터 출력

        for category in categories:
        # 중분류 불러오기
            subcategories = self.load_symptoms_by_level(level='중분류', parent_id=category['id'], species=species)
            print(f"중분류 카테고리 for 대분류 {category['name']} (id={category['id']}):", subcategories)  # 중분류 데이터 출력
        
            category_data = {
            "대분류": category,
            "중분류": []
            }

            for subcategory in subcategories:
            # 소분류 불러오기
                subsubcategories = self.load_symptoms_by_level(level='소분류', parent_id=subcategory['id'], species=species)
                print(f"소분류 카테고리 for 중분류 {subcategory['name']} (id={subcategory['id']}):", subsubcategories)  # 소분류 데이터 출력
            
                subcategory_data = {
                "중분류": subcategory,
                "소분류": subsubcategories
                }

                category_data["중분류"].append(subcategory_data)

            hierarchy.append(category_data)
    
    # 최종 계층 구조 출력
        print("최종 계층 구조:", hierarchy)

        return hierarchy


#========================================================
     # 응급조치 답변 삽입 함수
    def insert_emergency_response(self, main_symptom, sub_symptom, detailed_symptom, response):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return None

        try:
            cursor = db.cursor()
            print("Inserting response:", main_symptom, sub_symptom, detailed_symptom, response)  # 디버깅용 출력
            query = """
            INSERT INTO EmergencyResponses (main_symptom, sub_symptom, detailed_symptom, response)
            VALUES (%s, %s, %s, %s)
        """
            cursor.execute(query, (main_symptom, sub_symptom, detailed_symptom, response))
            db.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error: {e}")  # 오류 출력
            return None
        finally:
            cursor.close()
            db.close()
     # 특정 ID의 대, 중, 소분류 이름 가져오기
    def get_symptom_name_by_id(self, symptom_id):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return None

        try:
            cursor = db.cursor()
            query = "SELECT name FROM SymptomHierarchy WHERE id = %s"
            cursor.execute(query, (symptom_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            db.close()

    # 응급조치 답변 조회 함수
    def get_emergency_response(self, main_symptom, sub_symptom, detailed_symptom):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return None

        try:
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT response FROM EmergencyResponses
                WHERE main_symptom = %s AND sub_symptom = %s AND detailed_symptom = %s
            """
            cursor.execute(query, (main_symptom, sub_symptom, detailed_symptom))
            result = cursor.fetchone()
            return result['response'] if result else None
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            db.close()

"""
    # 계층적 구조 불러오기 메서드에 species 필터 추가
    def load_symptom_hierarchy(self, species):
        categories = self.load_symptoms_by_level(level='대분류', species=species)
        hierarchy = []

        for category in categories:
            subcategories = self.load_symptoms_by_level(level='중분류', parent_id=category['id'], species=species)
            category_data = {
                "대분류": category,
                "중분류": []
            }

            for subcategory in subcategories:
                subsubcategories = self.load_symptoms_by_level(level='소분류', parent_id=subcategory['id'], species=species)
                subcategory_data = {
                    "중분류": subcategory,
                    "소분류": subsubcategories
                }
                category_data["중분류"].append(subcategory_data)

            hierarchy.append(category_data)
        
        return hierarchy

    # 종에 따라 대분류, 중분류, 소분류 필터링하는 로직 추가
    def load_symptoms_by_level(self, level, parent_id=None, species=None):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            if parent_id is None:
                query = "SELECT * FROM SymptomHierarchy WHERE level = %s AND species = %s AND parent_id IS NULL"
                cursor.execute(query, (level, species))
            else:
                query = "SELECT * FROM SymptomHierarchy WHERE level = %s AND species = %s AND parent_id = %s"
                cursor.execute(query, (level, species, parent_id))
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            db.close()
            """