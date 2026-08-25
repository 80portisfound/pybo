from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas.document import DocumentCreate

import models

def get_document(db: Session, document_id: int): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    return db.get( # db.get() 메서드를 사용하여 Document 객체를 조회
        models.Document,
        document_id,
    )

def get_documents( # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db: Session,
    skip: int = 0,
    limit: int = 10,
):
    statement = select(models.Document).offset(skip).limit(limit) # SQLAlchemy의 select() 함수를 사용하여 Document 객체를 조회하는 쿼리 생성, offset()과 limit() 메서드를 사용하여 페이징 처리
    documents = db.scalars(statement).all() # db.scalars() 메서드를 사용하여 쿼리 결과를 스칼라 값으로 변환하고, all() 메서드를 사용하여 모든 결과를 리스트로 반환
    return documents # 조회된 문서 리스트 반환

def create_document(db: Session, document: DocumentCreate): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_document = models.Document(title=document.title, source=document.source,
                                  notion_page_id=document.notion_page_id, last_edited_time=document.last_edited_time
    ) # Document 모델 인스턴스 생성
    db.add(db_document) # 세션에 추가   
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_document) # 새로 생성된 객체를 세션에 반영
    return db_document # 생성된 문서 객체 반환

def get_document_by_notion_page_id(db: Session, notion_page_id: str): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    statement = select(models.Document).where(models.Document.notion_page_id == notion_page_id) # SQLAlchemy의 select() 함수를 사용하여 Document 객체를 조회하는 쿼리 생성, where() 메서드를 사용하여 notion_page_id 필드로 필터링
    document = db.scalars(statement).first() # db.scalars() 메서드를 사용하여 쿼리 결과를 스칼라 값으로 변환하고, first() 메서드를 사용하여 첫 번째 결과를 반환
    return document # 조회된 문서 객체 반환

def upsert_document(db: Session, document: DocumentCreate): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    existing_document = get_document_by_notion_page_id(db, document.notion_page_id) # notion_page_id로 기존 문서 조회
    if existing_document: # 기존 문서가 존재할 경우
        existing_document.title = document.title # title 필드 업데이트
        existing_document.source = document.source # source 필드 업데이트
        existing_document.last_edited_time = document.last_edited_time # last_edited_time 필드 업데이트
        db.commit() # 커밋하여 데이터베이스에 반영
        db.refresh(existing_document) # 수정된 객체를 세션에 반영
        return existing_document # 수정된 문서 객체 반환
    else: # 기존 문서가 존재하지 않을 경우
        return create_document(db, document) # 새 문서 생성 후 반환

def get_all_documents(db: Session): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    statement = select(models.Document) # SQLAlchemy의 select() 함수를 사용하여 Document 객체를 조회하는 쿼리 생성
    documents = db.scalars(statement).all() # db.scalars() 메서드를 사용하여 쿼리 결과를 스칼라 값으로 변환하고, all() 메서드를 사용하여 모든 결과를 리스트로 반환
    return documents # 조회된 문서 리스트 반환