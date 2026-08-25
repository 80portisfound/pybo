from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.vector_sync import sync_all_document_vectors
from services.retrieval import semantic_search, retrieve
from crud.chunk import search_chunks_by_keyword
from services.hybrid_search import hybrid_search
from services.rag import answer_question

router = APIRouter(tags=["Search"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능

@router.get("/search")
def search(query: str , top_k: int = Query(default=5, ge=1, le=20),max_distance: float = Query(default=0.4, gt = 0), document_id: int | None = None, db: Session = Depends(get_db)): 
    """
    검색 API 엔드포인트
    - query: 검색할 쿼리 문자열
    """
    results = retrieve(db, query, top_k, max_distance = max_distance, document_id = document_id )  # retrieve 함수를 호출하여 검색 결과를 가져옴
    return {
        "query": query,
        "top_k": top_k,
        "max_distance": max_distance,
        "result_count": len(results),
        "results": results,
    }

@router.post("/vector/backfill")
def backfill_vectors(db: Session = Depends(get_db)):
    count = sync_all_document_vectors(db)
    return {
        "vector_count": count,
    }

@router.get("/search/debug/keyword")
def debug_keyword_search(
    keyword: str,
    db: Session = Depends(get_db),
):
    chunks = search_chunks_by_keyword(
        db,
        keyword,
    )

    return {
        "count": len(chunks),
        "results": [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "content": chunk.content,
            }
            for chunk in chunks
        ],
    }

@router.get("/search/hybrid")
def hybrid_search_endpoint(
    query: str,
    top_k: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    results = hybrid_search(db, query, top_k)
    return {
        "query": query,
        "top_k": top_k,
        "result_count": len(results),
        "results": results,
    }

@router.get("/ask")
def ask_question(
    query: str,
    top_k: int = Query(default=5, ge=1, le=20),
    min_rerank_score: float = Query(default=0.0),
    db: Session = Depends(get_db),
):
    return answer_question(db = db, query = query, top_k = top_k, min_rerank_score = min_rerank_score)