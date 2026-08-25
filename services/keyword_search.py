from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi
from crud.chunk import get_all_chunks

def keyword_search(db: Session, query: str, top_k: int = 5):
    chunks = get_all_chunks(db) # 모든 청크를 가져옴

    # 전체 chunk 토큰화
    tokenized_chunks = [chunk.content.lower().split() for chunk in chunks] # 각 청크의 내용을 공백 기준으로 토큰화하여 리스트로 저장

    # BM25 모델 생성
    bm25 = BM25Okapi(tokenized_chunks) # BM25Okapi 모델을 생성하고, 토큰화된 청크를 학습 데이터로 사용

    # 쿼리 토큰화
    tokenized_query = query.lower().split() # 쿼리를 공백 기준으로 토큰화하여 리스트로 저장

    # 각 chunk의 bm25 점수 계산
    scores = bm25.get_scores(tokenized_query) # BM25 모델을 사용하여 각 청크에 대한 점수를 계산

    # 점수와 청크를 함께 묶어 정렬
    results = [
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "score" : float(score),
            "page_id" : chunk.page_id,
            "page_title" : chunk.page_title,
            "page_path" : chunk.page_path,
        }
        for chunk, score in zip(chunks, scores) # 각 청크와 점수를 묶어 딕셔너리 형태로 리스트에 저장
    ]

    results.sort(key=lambda x: x["score"], reverse=True) # 점수를 기준으로 내림차순 정렬

    return results[:top_k] # 상위 top_k개의 결과를 반환