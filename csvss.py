import csv
import os

def split_csv_by_column(file_path, column_name, output_folder):
    # 출력 폴더가 없다면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 파일 열기
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as csv_file:
        reader = csv.DictReader(csv_file)
        files = {}

        for row in reader:
            # 열 이름을 기준으로 파일을 나누기
            key = row[column_name]

            if key not in files:
                # 파일이 없는 경우 새로 생성
                output_file_path = os.path.join(output_folder, f"{key}.csv")
                output_file = open(output_file_path, 'w', newline='', encoding='utf-8')
                writer = csv.writer(output_file)
                
                # CSV 파일의 헤더 작성
                writer.writerow(reader.fieldnames)
                
                # 파일 및 writer 객체를 딕셔너리에 저장
                files[key] = writer, output_file

            # 해당 writer를 사용해 행 쓰기
            files[key][0].writerow(row.values())

    # 모든 파일 닫기
    for writer, file in files.values():
        file.close()

# 사용 예시
input_file = 'csv_first_last.csv'  # 원본 CSV 파일 경로
column_name = 'pet_friendly'  # 기준 열 이름
output_folder = 'output_files'  # 분할된 파일이 저장될 폴더

split_csv_by_column(input_file, column_name, output_folder)
