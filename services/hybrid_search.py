from sqlalchemy.orm import Session
from services.retrieval import semantic_search
from services.keyword_search import keyword_search
from services.reranker import rerank

def hybrid_search(db: Session, query: str, top_k: int = 5):

    # 후보 k개
    candidate_k = top_k * 3 

    # 벡터 스토어에서 유사도 검색 수행
    vector_results = semantic_search(query, candidate_k,document_id=None)

    # BM25 기반 키워드 검색 수행
    keyword_results = keyword_search(db, query, candidate_k)

    # 결과를 합친다
    combined_results = {}

    # 벡터 검색 결과에 순위를 매긴다
    for rank, result in enumerate(vector_results, start=1):
        combined_results[result["id"]] = {
            "id" : result["id"],
            "document_id" : result["document_id"],
            "chunk_index" : result.get("chunk_index"),
            "content" : result.get("content"),
            "vector_distance" : result.get("distance"),
            "keyword_score" : None,
            "vector_rank" : rank,
            "keyword_rank" : None,
            "page_id" : result.get("page_id"),
            "page_title" : result.get("page_title"),
            "page_path" : result.get("page_path"),
        }
    # 키워드 검색 결과에 순위를 매긴다
    for rank, result in enumerate(keyword_results, start=1):
        chunk_id = result["id"]
        if chunk_id in combined_results: # 이미 벡터 검색 결과에 존재하는 경우
            combined_results[chunk_id]["keyword_score"] = float(result.get("score"))
            combined_results[chunk_id]["keyword_rank"] = rank
            if combined_results[chunk_id].get("page_id") is None: # page_id가 없는 경우에만 추가
                combined_results[chunk_id]["page_id"] = result.get("page_id")
                combined_results[chunk_id]["page_title"] = result.get("page_title")
                combined_results[chunk_id]["page_path"] = result.get("page_path")
        else:
            combined_results[chunk_id] = {
                "id" : result["id"],
                "document_id" : result["document_id"],
                "chunk_index" : result.get("chunk_index"),
                "content" : result.get("content"),
                "vector_distance" : None,
                "keyword_score" : float(result.get("score")),
                "vector_rank" : None,
                "keyword_rank" : rank,
                "page_id" : result.get("page_id"),
                "page_title" : result.get("page_title"),
                "page_path" : result.get("page_path"),
            }

    # RRF 점수 계산
    for result in combined_results.values():
        result["rrf_score"] = calculate_rrf_score(
            result.get("vector_rank"), 
            result.get("keyword_rank"),
        )

    # dict -> list 변환
    combined_results_list = list(combined_results.values())

    # RRF 점수를 기준으로 내림차순 정렬
    combined_results_list.sort(key=lambda x: x["rrf_score"], reverse=True)

    #RRF 상위 candidate_k 개수만큼 결과를 가져온다
    rrf_candidates = combined_results_list[:candidate_k]

    # CrossEncoder를 사용하여 최종적으로 rerank 수행
    return rerank(query, rrf_candidates, top_k=top_k)


def calculate_rrf_score(vector_rank, keyword_rank, k=60):
    score = 0.0
    # vector_rank가 존재하면 RRF 점수 계산에 추가
    if vector_rank is not None:
        score += 1 / (k + vector_rank)
    # keyword_rank가 존재하면 RRF 점수 계산에 추가
    if keyword_rank is not None:
        score += 1 / (k + keyword_rank)
    return score