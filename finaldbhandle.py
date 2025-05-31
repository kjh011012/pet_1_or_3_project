import mysql.connector
from mysql.connector import Error

class FinalDiagnosisDB:
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

    def save_final_answer_to_final_db(self, symptom_hierarchy_id, final_answer):
        """
        2차 DB에 최종 답변 저장
        """
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return False

        try:
            cursor = db.cursor()
            query = "INSERT INTO FinalDiagnosis (symptom_hierarchy_id, final_answer) VALUES (%s, %s)"
            cursor.execute(query, (symptom_hierarchy_id, final_answer))
            db.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()
            db.close()
