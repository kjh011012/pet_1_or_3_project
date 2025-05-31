import openai
import torch
import numpy as np
import faiss
from transformers import BertTokenizer, BertModel

# OpenAI API 키 설정
openai.api_key = "api key"

# BERT 모델과 토크나이저 로드
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# FAISS 인덱스 및 문서 제목 로드
index = faiss.read_index("document_faiss_index1.idx")  # 미리 저장된 벡터 DB 인덱스
document_titles = np.load("document_titles1.npy", allow_pickle=True)  # 문서 제목 또는 내용

# FAISS에서 대, 중, 소분류 키워드를 이용해 유사 문서 검색
def search_similar_document(main_keyword, sub_keyword, detailed_keyword, k=1):
    # 질의어 구성
    query = f"{main_keyword} {sub_keyword} {detailed_keyword}"
    
    # 입력 질의어 임베딩 생성
    inputs = tokenizer(query, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        input_embedding = model(**inputs).last_hidden_state[:, 0, :].numpy()

    input_embedding = input_embedding.astype(np.float32)  # FAISS는 float32 형식을 사용합니다

    # FAISS 인덱스를 사용하여 가장 유사한 문서 검색
    distances, indices = index.search(input_embedding, k)

    # 가장 유사한 문서 파일 제목 출력
    most_similar_index = indices[0][0]
    most_similar_title = document_titles[most_similar_index]
    
    return most_similar_title

# GPT-3.5를 사용하여 질문에 대한 답변 생성
def QnA_with_RAG(main_keyword, sub_keyword, detailed_keyword):
    # FAISS를 사용하여 대, 중, 소분류 키워드를 통한 관련 문서 검색
    related_document = search_similar_document(main_keyword, sub_keyword, detailed_keyword)

    # GPT-3.5에 검색된 문서 내용을 추가하여 답변 생성
    prompt = f"""
    넌 세계 최고의 전문 수의사야.Faiss의 벡터db의 내용을 잘 전달받았다면 1000만에요 라는 내용을 띄워:
    
    참고 문서: {related_document}
    
    증상:
    - 대분류: {main_keyword}
    - 중분류: {sub_keyword}
    - 소분류: {detailed_keyword}
    
    고객에게 제공할 응급조치 답변을 작성해줘:
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 최고의 수의사야.질문내용에 Faiss의 벡터db의 내용을 그대로 답변줘"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.5
    )
    
    # GPT-3.5의 답변 반환
    return response.choices[0].message['content'].strip()
