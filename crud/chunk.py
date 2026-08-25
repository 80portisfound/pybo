from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas.chunk import ChunkCreate

import models

def create_chunk(db: Session, chunk: ChunkCreate, document_id: int): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_chunk = models.Chunk(document_id=document_id, content=chunk.content, chunk_index=chunk.chunk_index, page_id=chunk.page_id, page_title=chunk.page_title, page_path=chunk.page_path) # Chunk 모델 인스턴스 생성
    db.add(db_chunk) # 세션에 추가   
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_chunk) # 새로 생성된 객체를 세션에 반영
    return db_chunk # 생성된 Chunk 객체 반환

def get_chunks(db: Session, document_id: int): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    statement = select(models.Chunk).where(models.Chunk.document_id == document_id).order_by(models.Chunk.chunk_index) # SQLAlchemy의 select() 함수를 사용하여 Chunk 객체를 조회하는 쿼리 생성, where() 메서드를 사용하여 document_id로 필터링
    chunks = db.scalars(statement).all() # db.scalars() 메서드를 사용하여 쿼리 결과를 스칼라 값으로 변환하고, all() 메서드를 사용하여 모든 결과를 리스트로 반환
    return chunks # 조회된 Chunk 리스트 반환

def get_chunk(db: Session, chunk_id: int): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    return db.get( # db.get() 메서드를 사용하여 Chunk 객체를 조회
        models.Chunk,
        chunk_id,
    )

def get_all_chunks(db: Session): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    statement = select(models.Chunk) # SQLAlchemy의 select() 함수를 사용하여 Chunk 객체를 조회하는 쿼리 생성
    chunks = db.scalars(statement).all() # db.scalars() 메서드를 사용하여 쿼리 결과를 스칼라 값으로 변환하고, all() 메서드를 사용하여 모든 결과를 리스트로 반환
    return chunks # 조회된 Chunk 리스트 반환

def create_chunks_for_document(db: Session, document_id: int, texts: list[str], page_id: str, page_title: str, page_path: str, start_index: int = 0): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    chunks = [] # 생성된 청크를 저장할 리스트 초기화
    for index, text in enumerate(texts): # texts 리스트를 순회하며 인덱스와 텍스트를 가져옴
        chunk_data = ChunkCreate(content=text, chunk_index=index + start_index, page_id=page_id, page_title=page_title, page_path=page_path) # ChunkCreate 모델 인스턴스 생성
        db_chunk = create_chunk(db, chunk_data,document_id) # chunk 모듈의 create_chunk 함수를 사용하여 청크 생성
        chunks.append(db_chunk) # 생성된 청크를 리스트에 추가
    return chunks # 생성된 청크 리스트 반환

def delete_chunks_by_document_id(db: Session, document_id: int): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    statement = select(models.Chunk).where(models.Chunk.document_id == document_id) # SQLAlchemy의 select() 함수를 사용하여 Chunk 객체를 조회하는 쿼리 생성, where() 메서드를 사용하여 document_id로 필터링
    chunks = db.scalars(statement).all() # db.scalars() 메서드를 사용하여 쿼리 결과를 스칼라 값으로 변환하고, all() 메서드를 사용하여 모든 결과를 리스트로 반환
    for chunk in chunks: # 조회된 청크 리스트를 순회하며 삭제
        db.delete(chunk) # db.delete() 메서드를 사용하여 청크 삭제
    db.commit() # 커밋하여 데이터베이스에 반영

def search_chunks_by_keyword(db: Session, keyword: str): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    statement = select(models.Chunk).where(models.Chunk.content.contains(keyword)) # SQLAlchemy의 select() 함수를 사용하여 Chunk 객체를 조회하는 쿼리 생성, where() 메서드를 사용하여 content에 keyword가 포함된 청크를 필터링
    return db.scalars(statement).all() # 조회된 Chunk 리스트 반환