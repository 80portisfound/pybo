from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small" # 자연어 처리 모델  

model = SentenceTransformer(MODEL_NAME)  # 사전 학습된 모델 로드

def embed_text(text: str) -> list[float]:
    text = f"passage: {text}"  # 텍스트를 "passage: " 접두사와 함께 포맷
    embedding = model.encode(text)  # 텍스트를 임베딩 벡터로 변환
    return embedding.tolist()  # 임베딩 벡터를 리스트로 반환

def embed_query(query: str) -> list[float]:
    query = f"query: {query}"  # 쿼리를 "query: " 접두사와 함께 포맷
    embedding = model.encode(query)  # 쿼리를 임베딩 벡터로 변환
    return embedding.tolist()  # 임베딩 벡터를 리스트로 반환

def embed_texts(texts: list[str]) -> list[list[float]]:
    formatted_texts = [f"passage: {text}" for text in texts]  # 각 텍스트를 "passage: " 접두사와 함께 포맷
    embeddings = model.encode(formatted_texts)  # 텍스트들을 임베딩 벡터로 변환
    return embeddings.tolist()  # 임베딩 벡터들을 리스트로 반환

def embed_chunks(chunks) -> list[dict]:
    texts = [
        chunk.content for chunk in chunks 
    ] # 각 청크의 내용을 리스트로 추출
    embeddings = embed_texts(texts)  # 청크 내용을 임베딩 벡터로 변환
    
    results = [] # 
    for chunk, embedding in zip(chunks, embeddings): # 청크와 임베딩 벡터를 순회하며 dict 생성
        results.append({
            "chunk_id": chunk.id,
            "embedding": embedding,
        })
    return results  # 청크 객체들을 딕셔너리 리스트로 반환
