import pandas as pd
import mysql.connector
from mysql.connector import Error
"""
# CSV 파일 경로
csv_file_path = './Y.csv'
#csv는 콤마 스페이스 벨류 라는 뜻
# 데이터프레임으로 CSV 파일 로드
df = pd.read_csv(csv_file_path)

# 마리아DB 연결 설정
host = 'localhost'
database = 'dbname'
user = 'user'
password = 'pw'

try:
    # 마리아DB 연결
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        #테이블 생성 쿼리 작성
        table_name = 'places'
        #columns = ', '.join([f"`{col}` varchar(255)" for col in df.columns])  # 모든 열을 varchar(255) 형식으로 지정
        columns = []
        for col in df.columns:
            if col == 'homepage':  # 홈페이지는 VARCHAR(1500)으로 설정
                columns.append(f"`{col}` VARCHAR(1500)")
            else:
                columns.append(f"`{col}` VARCHAR(255)")  # 나머지 컬럼은 VARCHAR(255)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        
        # 테이블 생성
        cursor.execute(create_table_query)
        connection.commit()

        # 데이터 삽입 쿼리 작성
        cols = ", ".join([f"`{i}`" for i in df.columns.tolist()])
        values_placeholder = ", ".join(["%s"] * len(df.columns))
        
        for _, row in df.iterrows():
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({values_placeholder})"
            cursor.execute(sql, tuple(row.values)) 
        #for i, row in df.iterrows(): 테이블로 지하철 시간표 만들떄 사용했던 쿼리
         #   sql = f"INSERT INTO {table_name} ({cols}) VALUES ({'%s,%s, %s, %s, %s, %s, ' * (len(row) - 1)}%s)"
            #cursor.execute(sql, tuple(row))
            
        
        # 커밋 (데이터베이스에 변경 사항 반영)
        connection.commit()

        print(f"Table {table_name} created and data inserted successfully.")

except Error as e:
    print("Error while connecting to MariaDB", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MariaDB connection is closed")
"""
import pandas as pd
import mysql.connector
from mysql.connector import Error
import urllib.parse

# CSV 파일 경로
csv_file_path = './문예회관.csv'  # CSV 파일 경로
# 데이터프레임으로 CSV 파일 로드
df = pd.read_csv(csv_file_path)

# URL 인코딩 적용
df['homepage'] = df['homepage'].apply(lambda x: urllib.parse.quote(x, safe=':/'))

# 마리아DB 연결 설정
host = 'localhost'
database = 'dbname'
user = 'user'
password = 'pw'

try:
    # 마리아DB 연결
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS places")

        # 테이블 생성 쿼리 작성
        table_name = 'places_travel'
        columns = []
        for col in df.columns:
            if col == 'homepage':  # 홈페이지는 TEXT로 설정
                columns.append(f"`{col}` TEXT")
            else:
                columns.append(f"`{col}` VARCHAR(255)")  # 나머지 컬럼은 VARCHAR(255)

        # 컬럼들을 올바르게 조인하여 쿼리 생성
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        
        # 테이블 생성
        cursor.execute(create_table_query)
        connection.commit()

        # 데이터 삽입 쿼리 작성
        cols = ", ".join([f"`{i}`" for i in df.columns.tolist()])
        values_placeholder = ", ".join(["%s"] * len(df.columns))
        
        for index, row in df.iterrows():
            try:
                sql = f"INSERT INTO {table_name} ({cols}) VALUES ({values_placeholder})"
                cursor.execute(sql, tuple(row.values))
            except Error as e:
                print(f"Error inserting row {index}: {e}")  # 오류가 발생한 행 인덱스 출력
        
        # 커밋 (데이터베이스에 변경 사항 반영)
        connection.commit()

        print(f"Table {table_name} created and data inserted successfully.")

except Error as e:
    print("Error while connecting to MariaDB", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MariaDB connection is closed")
