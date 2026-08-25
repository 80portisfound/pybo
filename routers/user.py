from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import (
    UserCreate,
    UserResponse,
    TokenResponse,
)
import models
from auth import get_current_user
from database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from security import hash_password, create_access_token , verify_password # security.py에서 정의한 상수와 password_hash, create_access_token 함수를 임포트하여 JWT 토큰 생성 및 비밀번호 해싱에 사용
from crud import user as user_crud
router = APIRouter(tags=["Users"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능


@router.post("/users", response_model=UserResponse, status_code=201) # 사용자 생성 엔드포인트 정의, 요청 본문은 username과 password를 사용하고, 데이터베이스 세션은 get_db 종속성을 통해 주입
def create_user(user: UserCreate, db: Session = Depends(get_db)): # 상태 코드는 201(Created)로 설정
    existing_user = user_crud.get_user_by_username(db, user.username) # CRUD 함수를 사용하여 데이터베이스에서 사용자 조회
    if existing_user: # 이미 존재하는 사용자일 경우
        raise HTTPException(status_code=409, detail="Username already exists") # 409 Conflict 예외 발생
    
    hashed_password = hash_password(user.password) # 비밀번호를 해싱하여 저장
    db_user = user_crud.create_user(db, user.username, hashed_password) # CRUD 함수를 사용하여 데이터베이스에 사용자 생성
    return db_user # 생성된 사용자 객체 반환

@router.post("/login", response_model=TokenResponse) # 사용자 ID를 기반으로 특정 사용자를 조회하는 엔드포인트 정의
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입, OAuth2PasswordRequestForm을 사용하여 사용자 인증 정보를 가져옴
    db_user = user_crud.get_user_by_username(db, form_data.username) # CRUD 함수를 사용하여 데이터베이스에서 사용자 조회
    if db_user is None: # 사용자가 존재하지 않을 경우
        raise HTTPException(status_code=401, detail="Incorrect username or password") # 401 Unauthorized 예외 발생

    if not verify_password(form_data.password, db_user.password_hash): # 비밀번호 검증
        raise HTTPException(status_code=401, detail="Incorrect username or password") # 401 Unauthorized 예외 발생
    
    access_token = create_access_token(
    db_user.username
    ) # create_access_token 함수를 사용하여 JWT 토큰 생성

    return {
        "access_token": access_token, # 생성된 access_token 반환
        "token_type": "bearer", # 토큰 타입을 bearer로 설정
    }

@router.get("/users/me", response_model=UserResponse) # 현재 로그인한 사용자의 정보를 조회하는 엔드포인트 정의
def get_me(current_user: models.User = Depends(get_current_user)): # 현재 사용자 객체는 get_current_user 종속성을 통해 주입
    return current_user # 현재 사용자 객체 반환
