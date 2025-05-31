import mysql.connector
from mysql.connector import Error

class travel_db_handle:
    def __init__(self, user, password, host, database='places_db'):
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

    # 1차: 모든 고유한 province 값 로드
    def load_provinces(self):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT province FROM places_travel"
            cursor.execute(query)
            provinces = [row['province'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            provinces = []
        finally:
            cursor.close()
            db.close()
        
        return provinces

    # 2차: 특정 province에 해당하는 고유한 city 값 로드
    def load_cities(self, province):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT city FROM places_travel WHERE province = %s"
            cursor.execute(query, (province,))
            cities = [row['city'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            cities = []
        finally:
            cursor.close()
            db.close()
        
        return cities

    # 3차: 특정 province와 city에 해당하는 고유한 category3 값 로드
    def load_categories(self, province, city):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT category3 FROM places_travel WHERE province = %s AND city = %s"
            cursor.execute(query, (province, city))
            categories = [row['category3'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            categories = []
        finally:
            cursor.close()
            db.close()
        
        return categories

    # 최종 선택된 province, city, category3에 따라 추천 장소 로드
    def load_recommendations(self, province, city, category):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
    
        try:
            cursor = db.cursor(dictionary=True)
            query = """
        SELECT name, road_address, contact, latitude, longitude FROM places_travel 
        WHERE province = %s AND city = %s AND category3 = %s
        """
            cursor.execute(query, (province, city, category))
            recommendations = cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            recommendations = []
        finally:
            cursor.close()
            db.close()
    
        return recommendations

#=================================생활========================
     # 1차: 모든 고유한 province 값 로드
    def load_provinces2(self):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT province FROM places_life"
            cursor.execute(query)
            provinces = [row['province'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            provinces = []
        finally:
            cursor.close()
            db.close()
        
        return provinces

    # 2차: 특정 province에 해당하는 고유한 city 값 로드
    def load_cities2(self, province):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT city FROM places_life WHERE province = %s"
            cursor.execute(query, (province,))
            cities = [row['city'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            cities = []
        finally:
            cursor.close()
            db.close()
        
        return cities

    # 3차: 특정 province와 city에 해당하는 고유한 category3 값 로드
    def load_categories2(self, province, city):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT category3 FROM places_life WHERE province = %s AND city = %s"
            cursor.execute(query, (province, city))
            categories = [row['category3'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            categories = []
        finally:
            cursor.close()
            db.close()
        
        return categories

    # 최종 선택된 province, city, category3에 따라 추천 장소 로드
    def load_recommendations2(self, province, city, category):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
    
        try:
            cursor = db.cursor(dictionary=True)
            query = """
        SELECT name, road_address, contact, latitude, longitude FROM places_life 
        WHERE province = %s AND city = %s AND category3 = %s
        """
            cursor.execute(query, (province, city, category))
            recommendations = cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            recommendations = []
        finally:
            cursor.close()
            db.close()
    
        return recommendations

    #=================================의료========================
     # 1차: 모든 고유한 province 값 로드
    def load_provinces3(self):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT province FROM places_medical"
            cursor.execute(query)
            provinces = [row['province'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            provinces = []
        finally:
            cursor.close()
            db.close()
        
        return provinces

    # 2차: 특정 province에 해당하는 고유한 city 값 로드
    def load_cities3(self, province):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT city FROM places_medical WHERE province = %s"
            cursor.execute(query, (province,))
            cities = [row['city'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            cities = []
        finally:
            cursor.close()
            db.close()
        
        return cities

    # 3차: 특정 province와 city에 해당하는 고유한 category3 값 로드
    def load_categories3(self, province, city):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
        
        try:
            cursor = db.cursor(dictionary=True)
            query = "SELECT DISTINCT category3 FROM places_medical WHERE province = %s AND city = %s"
            cursor.execute(query, (province, city))
            categories = [row['category3'] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error: {e}")
            categories = []
        finally:
            cursor.close()
            db.close()
        
        return categories

    # 최종 선택된 province, city, category3에 따라 추천 장소 로드
    def load_recommendations3(self, province, city):
        db = self.get_db_connection()
        if db is None:
            print("Failed to connect to the database.")
            return []
    
        try:
            cursor = db.cursor(dictionary=True)
            query = """
        SELECT name, road_address, contact, latitude, longitude FROM places_medical 
        WHERE province = %s AND city = %s 
        """
            cursor.execute(query, (province, city))
            recommendations = cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            recommendations = []
        finally:
            cursor.close()
            db.close()
    
        return recommendations

   
#db3개로 나누기
# -> 식당,카페,반려동물용품점
# -> 숙박, 관광지,문화예술센터등등
# -> 의료(동물병원)