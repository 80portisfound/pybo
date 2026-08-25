from sqlalchemy.orm import Session
from crud.document import get_document
from crud.chunk import get_chunk
from services.embedding import embed_query
from services.vector_store import search_vectors


def semantic_search(query: str, top_k: int = 5, document_id: int | None = None) -> list[dict]:
    query_embedding = embed_query(query)
    return search_vectors(query_embedding, top_k,document_id)  # 검색 결과 반환

def retrieve(db: Session, query: str, top_k: int = 5, max_distance: float = 0.4, document_id: int | None = None) -> list[dict]:
    candidate_K = top_k * 3  # 후보 K를 top_k의 세 배로 설정

    results = semantic_search(query, candidate_K,document_id)  # 쿼리 임베딩 벡터를 기반으로 유사한 벡터 검색
    retrieval_results = []

    for result in results:
        if result["distance"] > max_distance: # 유사도가 지정된 최대 거리 이상인 경우만 결과에 포함
            continue

        if result.get("chunk_index") is None:
            chunk = get_chunk(db, result["id"])
            if chunk is None:
                continue
            result["chunk_index"] = chunk.chunk_index

        if is_nearby_chunks(result, retrieval_results): # 이미 선택된 결과와 인접한 청크인 경우 제외
            continue
        result_document_id = result["document_id"] # result["document_id"]를 이용해서 SQLite에서 Document 조회
        document = get_document(db, result_document_id)
        if document: 
            retrieval_results.append({ # 조회된 문서와 점수를 딕셔너리 형태로 리스트에 추가
                "chunk_id": result["id"],
                "document_id": document.id,
                "chunk_index": result["chunk_index"],
                "title": document.title,
                "source": document.source,
                "content" : result["content"],
                "distance": result["distance"],
            })
            if len(retrieval_results) >= top_k:  # 결과가 top_k보다 많으면 top_k만 반환
                break
    return retrieval_results

def is_nearby_chunks(result : dict, selected_results: list[dict]) -> bool: # 
    for selected in selected_results:
        same_document = result["document_id"] == selected["document_id"] # 같은 문서인지 확인

        result_chunk_index = result.get("chunk_index") # 결과의 청크 인덱스 가져오기
        selected_chunk_index = selected.get("chunk_index") # 선택된 결과의 청크 인덱스 가져오기
        if result_chunk_index is None or selected_chunk_index is None: # 청크 인덱스가 None인 경우 False 반환
            continue 

        nearby_chunk_index = abs(result_chunk_index - selected_chunk_index) <= 1 # 청크 인덱스가 1 이하로 차이나는지 확인

        if same_document and nearby_chunk_index: # 같은 문서이면서 청크 인덱스가 1 이하로 차이나면 True 반환
            return True
    
    return False # 같은 문서이면서 청크 인덱스가 1 이하로 차이나는 경우가 없으면 False 반환
