from sentence_transformers import CrossEncoder

MODEL_NAME = "BAAI/bge-reranker-v2-m3" # 사용할 CrossEncoder 모델 이름

model = CrossEncoder(MODEL_NAME)  # CrossEncoder 모델 로드

def rerank(query: str, results: list[dict],top_k: int = 5,) -> list[dict]:
    # 검색 결과가 없으면 빈 리스트 변환
    if not results:
        return []
    #Query + 각 result["content"]를 pair로 만들기
    pairs = [(query, result["content"]) for result in results]

    # model.predict()를 사용하여 각 쌍에 대한 점수를 계산
    scores = model.predict(pairs)

    # 점수를 결과에 추가
    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)
    
    # 점수를 기준으로 결과를 내림차순으로 정렬
    reranked_results = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    # top_k 개수만큼 결과를 반환
    return reranked_results[:top_k]