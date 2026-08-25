from sqlalchemy.orm import Session
from schemas.document import DocumentCreate
from crud.document import upsert_document, get_document_by_notion_page_id
from crud.chunk import create_chunks_for_document,delete_chunks_by_document_id
from notion_client import extract_page_metadata,extract_page_text, get_pages, get_all_blocks,get_page_sections
from services.chunking import split_text
from services.vector_sync import sync_document_vectors
from services.vector_store import delete_document_vectors

def sync_notion_page(db: Session, page: dict): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    metadata = extract_page_metadata(page) # Notion 페이지에서 메타데이터 추출
    document_data = DocumentCreate(
        title=metadata["title"],
        source=metadata["source"],
        notion_page_id=metadata["notion_page_id"],
        last_edited_time=metadata["last_edited_time"],
    ) # DocumentCreate 모델 인스턴스 생성
    return upsert_document(db, document_data) # upsert_document 함수를 사용하여 문서 동기화
def sync_full_notion_page(db: Session, page: dict, chunk_size: int = 500, overlap: int = 100, force: bool = False): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    metadata = extract_page_metadata(page) # Notion 페이지에서 메타데이터 추출
    existing_document = get_document_by_notion_page_id(db, metadata["notion_page_id"]) # 데이터베이스에서 해당 Notion 페이지 ID에 해당하는 문서 조회
    if existing_document is None: # 데이터베이스에 문서가 존재하지 않으면 새로 생성
        document = sync_notion_page(db, page) # Notion 페이지 메타데이터 동기화

        sections = get_page_sections(page_id = page["id"], page_title = metadata["title"]) # Notion 페이지의 섹션 조회
        replace_document_index(db = db, document_id = document.id, sections = sections, chunk_size = chunk_size, overlap = overlap) # 기존 청크와 벡터를 삭제하고 새로 생성
        
        return { # 생성된 문서 반환
            "status": "created",
            "document": document,
        } 
    need_update = needs_update(existing_document, metadata) # 데이터베이스 문서와 Notion 페이지의 마지막 편집 시간 비교
    if not force and not need_update: # 업데이트가 필요하지 않으면 기존 문서 반환
        return { # 기존 문서 반환
            "status": "skipped",
            "document": existing_document,
        }
    document = sync_notion_page(db, page) # Notion 페이지 메타데이터 동기화

    sections = get_page_sections(page["id"], metadata["title"]) # Notion 페이지의 섹션 조회
    replace_document_index(
        db = db,
        document_id = document.id,
        sections = sections,
        chunk_size = chunk_size,
        overlap = overlap
    )
    return {
        "status": "updated",
        "document": document,
    } # 동기화된 문서 반환

def sync_all_notion_pages(db: Session, force: bool = False): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    notion_pages = get_pages() # Notion API를 통해 모든 페이지 조회
    stats = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
    }
    documents = []
    for page in notion_pages: # 각 페이지에 대해 동기화 수행
        result = sync_full_notion_page(db, page, force = force) # Notion 페이지 동기화
        status = result["status"] # 동기화 결과 상태 확인
        stats[status] += 1 # 상태별 통계 업데이트
        document = result["document"] # 동기화된 문서 가져오기
        document_data = {
            "id": document.id,
            "title": document.title,
            "source": document.source,
            "notion_page_id": document.notion_page_id,
            "last_edited_time": document.last_edited_time,
        } # 동기화된 문서 정보를 딕셔너리로 변환
        documents.append(document_data) # 동기화된 문서 리스트에 추가
    return {
        "stats": stats,
        "documents": documents,
    } # 동기화 통계와 문서 리스트 반환

def needs_update(db_document, page_metadata: dict) -> bool:
    if db_document is None: # 데이터베이스에 문서가 존재하지 않으면 업데이트 필요
        return True
    return (db_document.last_edited_time != page_metadata.get("last_edited_time")) # 데이터베이스 문서의 마지막 편집 시간과 Notion 페이지의 마지막 편집 시간이 다르면 업데이트 필요

def replace_document_index(
    db: Session,
    document_id: int,
    sections : list[dict],
    chunk_size: int = 500,
    overlap: int = 100,
): 
    delete_document_vectors(document_id) # 기존 문서의 벡터 삭제

    delete_chunks_by_document_id(db, document_id) # 기존 문서의 청크 삭제

    chunks = sync_notion_sections(
        db = db,
        document_id = document_id,
        sections = sections,
        chunk_size = chunk_size,
        overlap = overlap,
    )
    sync_document_vectors(db, document_id) # 새로 생성된 청크를 기반으로 벡터 동기화
    
    return len(chunks) # 새로 생성된 청크 수 반환

def sync_notion_sections(db: Session, document_id: int, sections: list[dict], chunk_size: int = 500, overlap: int = 100):
    all_chunks = []
    start_index = 0

    for section in sections: 
        section_content = section["content"]

        if not section_content.strip():  # 섹션 내용이 비어있으면 건너뜀
            continue

        texts = split_text(section_content, chunk_size, overlap) # 섹션 내용을 청크로 분할

        chunks = create_chunks_for_document( # 분할된 청크를 데이터베이스에 저장
            db = db,
            document_id = document_id,
            texts = texts,
            page_id = section["page_id"],
            page_title = section["page_title"],
            page_path = section["page_path"],
            start_index = start_index,
        )
        all_chunks.extend(chunks) # 생성된 청크를 all_chunks 리스트에 추가
        start_index += len(chunks) # 다음 섹션의 청크 인덱스를 위해 start_index를 업데이트

    return all_chunks