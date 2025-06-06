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
index = faiss.read_index("document_faiss_index.idx")  # 미리 저장된 벡터 DB 인덱스
document_titles = np.load("document_titles.npy", allow_pickle=True)  # 문서 제목 또는 내용

# 질의어를 사용하여 FAISS에서 가장 유사한 문서 검색
def search_similar_document(query, k=1):
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
def QnA_with_RAG(question):
    # 1. FAISS를 사용하여 질문과 관련된 문서를 검색
    related_document = search_similar_document(question)

    # 2. GPT-3.5에 검색된 문서 내용을 추가하여 답변 생성
    prompt = f"""
    넌 법률 전문가야. 문서를 참고해서 고객의 질문에 간략히 요약해서 답변을 제공해줘:
    참고 문서: {related_document}
    
    질문: {question}
    
    고객에게 제공할 답변을 작성해줘:
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 키워드를 가장 잘 뽑아내는 키워드 전문가야."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.5
    )
    
    # GPT-3.5의 답변 반환
    return response.choices[0].message['content'].strip()

# 키워드 추출 함수
def extract_keywords(text):
    # BERT를 통해 키워드를 추출
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.numpy()

# 입력된 키워드를 FAISS 검색과 LLM을 사용하여 답변 생성
def get_answer(keyword1, keyword2, user_question):
    # 키워드 결합
    combined_query = f"{keyword1} {keyword2} {user_question}"
    
    # 유사한 문서 검색 후 답변 생성
    answer = QnA_with_RAG(combined_query)
    return answer
