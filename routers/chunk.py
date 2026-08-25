from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas.chunk import ChunkCreate, ChunkResponse
import models
from database import get_db
from crud import document as document_crud
from crud import chunk as chunk_crud

router = APIRouter(tags=["Chunks"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능

@router.post("/documents/{document_id}/chunks", response_model=ChunkResponse, status_code=201) # 특정 문서에 대한 Chunk를 생성하는 엔드포인트 정의
def create_chunk(document_id: int, chunk: ChunkCreate, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_document = document_crud.get_document(db, document_id) # CRUD 함수를 사용하여 데이터베이스에서 문서 조회
    if db_document is None: # 문서가 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Document not found") # 404 Not Found 예외 발생
    return chunk_crud.create_chunk(db, chunk, document_id) # CRUD 함수를 사용하여 데이터베이스에 Chunk 생성 및 반환

@router.get("/documents/{document_id}/chunks", response_model=list[ChunkResponse]) # 특정 문서에 대한 Chunk 목록을 조회하는 엔드포인트 정의
def get_chunks(document_id: int, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_document = document_crud.get_document(db, document_id) # CRUD 함수를 사용하여 데이터베이스에서 문서 조회
    if db_document is None: # 문서가 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Document not found") # 404 Not Found 예외 발생
    return chunk_crud.get_chunks(db, document_id) # CRUD 함수를 사용하여 데이터베이스에서 해당 문서에 대한 Chunk 목록 조회 및 반환

@router.get("/chunks/{chunk_id}", response_model=ChunkResponse) # Chunk ID를 기반으로 특정 Chunk를 조회하는 엔드포인트 정의
def get_chunk(chunk_id: int, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    chunk = chunk_crud.get_chunk(db, chunk_id) # CRUD 함수를 사용하여 데이터베이스에서 Chunk 조회
    if chunk is None: # Chunk가 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Chunk not found") # 404 Not Found 예외 발생
    return chunk # 조회된 Chunk 객체 반환
