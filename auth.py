from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from jwt.exceptions import InvalidTokenError
from database import get_db
from security import SECRET_KEY, ALGORITHM
from crud import user as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): # 현재 사용자 정보를 가져오는 함수, 토큰과 데이터베이스 세션을 종속성으로 주입
    credentials_exception = HTTPException(
            status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"} # 인증 실패 시 발생할 예외 정의
        )
    try:    
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # JWT 토큰을 디코딩하여 payload를 가져옴
        username: str = payload.get("sub") # payload에서 "sub" 키를 가져와 username 변수에 할당
        if username is None: # username이 존재하지 않을 경우
            raise credentials_exception # 401 Unauthorized 예외 발생
            
    except InvalidTokenError: # JWT 토큰이 유효하지 않을 경우 발생하는 예외 처리
        raise credentials_exception # 401 Unauthorized 예외 발생

    db_user = user_crud.get_user_by_username(db, username) # 데이터베이스에서 username을 기반으로 사용자 조회

    if db_user is None: # 사용자가 존재하지 않을 경우
        raise credentials_exception # 401 Unauthorized 예외 발생
    return db_user # 현재 사용자 객체 반환
        
