from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.notion_sync import sync_all_notion_pages
from database import get_db
from notion_client import get_page_sections
from crud.document import get_document



router = APIRouter(tags=["Notion"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능

@router.post("/notion/sync", ) # Notion 페이지를 동기화하는 엔드포인트 정의
def sync_notion(db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    result = sync_all_notion_pages(db,force=False) # 모든 Notion 페이지를 동기화
    return result # 동기화 결과 반환

@router.post("/notion/reindex")
def reindex_notion(db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    result = sync_all_notion_pages(db, force=True) # 모든 Notion 페이지를 강제로 재동기화
    return result # 동기화 결과 반환

@router.get("/notion/debug/sections") # Notion 페이지의 섹션을 조회하는 엔드포인트 정의
def debug_notion_sections(document_id: int, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    document = get_document(db, document_id) # document_id를 기반으로 문서 조회
    if document is None: # document_id에 해당하는 문서가 없는 경우
        raise HTTPException(status_code=404, detail="Document not found") # 404 에러 반환
    
    sections = get_page_sections(page_id = document.notion_page_id, page_title = document.title) # Notion 페이지의 섹션 조회

    return {
        "document_id": document_id,
        "notion_page_id": document.notion_page_id,
        "count" : len(sections),
        "sections": sections,
    }
