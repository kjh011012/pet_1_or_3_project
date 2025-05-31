import pandas as pd
import mysql.connector
from mysql.connector import Error
import urllib.parse

# CSV 파일 경로
csv_file_path = './호텔.csv'  # 새 CSV 파일 경로

# 데이터프레임으로 CSV 파일 로드 (인코딩 자동 감지)
df = pd.read_csv(csv_file_path, encoding='utf-8')

# URL 인코딩 적용 (homepage 컬럼이 있는 경우)
if 'homepage' in df.columns:
    df['homepage'] = df['homepage'].apply(lambda x: urllib.parse.quote(str(x), safe=':/'))

# MariaDB 연결 설정
host = 'localhost'
database = 'dbname'
user = 'user'
password = 'pw'

try:
    # MariaDB 연결
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # 데이터 삽입 쿼리 작성
        cols = ", ".join([f"`{i}`" for i in df.columns.tolist()])
        values_placeholder = ", ".join(["%s"] * len(df.columns))
        
        for index, row in df.iterrows():
            try:
                sql = f"INSERT INTO places_travel ({cols}) VALUES ({values_placeholder})"
                cursor.execute(sql, tuple(row.values))
            except Error as e:
                print(f"Error inserting row {index}: {e}")  # 오류가 발생한 행 인덱스 출력
        
        # 커밋 (데이터베이스에 변경 사항 반영)
        connection.commit()

        print(f"Data inserted successfully into 'places_travel' table.")

except Error as e:
    print("Error while connecting to MariaDB", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MariaDB connection is closed")
