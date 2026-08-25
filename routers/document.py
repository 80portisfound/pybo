from auth import get_current_user # 현재 사용자 정보를 가져오는 함수 임포트
from fastapi.security import OAuth2PasswordBearer # FastAPI의 OAuth2PasswordBearer를 임포트하여 OAuth2 인증에 사용
from crud import document as document_crud # crud 모듈에서 document 관련 함수를 임포트하여 데이터베이스 작업에 사용
from database import get_db # 데이터베이스 세션을 가져오는 함수 임포트
from fastapi import APIRouter, Depends, HTTPException,Query # FastAPI의 APIRouter, Depends, HTTPException을 임포트하여 라우터 생성 및 의존성 주입, 예외 처리에 사용
from sqlalchemy.orm import Session # SQLAlchemy의 Session을 임포트하여 데이터베이스 세
from schemas.document import DocumentCreate, DocumentResponse # Pydantic 모델을 임포트하여 요청 및 응답 데이터 검증에 사용


router = APIRouter(tags=["Documents"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능

@router.post("/documents", response_model=DocumentResponse, status_code=201) # 문서를 생성하는 엔드포인트 정의
def create_document( document: DocumentCreate, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    return document_crud.create_document(db, document) # CRUD 함수를 사용하여 데이터베이스에 문서 생성 및 반환    

@router.get("/documents/", response_model=list[DocumentResponse]) # 문서 목록을 조회하는 엔드포인트 정의, 응답 모델은 DocumentResponse 모델의 리스트로 지정
def get_documents( skip: int = Query(default=0, ge = 0), limit: int = Query(default=10, ge = 1, le = 100), db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입, skip과 limit은 쿼리 파라미터로 받아 페이징 처리
    return document_crud.get_documents(db, skip=skip, limit=limit) # CRUD 함수를 사용하여 데이터베이스에서 문서 목록 조회 및 반환 

@router.get("/documents/{document_id}", response_model=DocumentResponse) # 문서 ID를 기반으로 특정 문서를 조회하는 엔드포인트 정의
def get_document(document_id: int, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    document = document_crud.get_document(db, document_id) # CRUD 함수를 사용하여 데이터베이스에서 문서 조회
    if document is None: # 문서가 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Document not found") # 404 Not Found 예외 발생
    return document # 조회된 문서 객체 반환

