from pwdlib import PasswordHash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import jwt


load_dotenv()  # .env 파일에서 환경 변수를 로드

SECRET_KEY = os.getenv("SECRET_KEY") # JWT 토큰 서명에 사용되는 비밀 키, 실제 서비스에서는 안전하게 관리되어야 함
ALGORITHM = "HS256" # JWT 토큰 서명에 사용되는 알고리즘, HMAC-SHA256을 사용
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # JWT 토큰 만료 시간, 30분으로 설정

password_hash = PasswordHash.recommended() # recommended() 클래스 메서드로 권장 해싱 알고리즘을 선택

def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # 현재 UTC 시간에 토큰 만료 시간을 더하여 expire 변수에 할당

    payload = {
        "sub": username, # 토큰의 주체(subject)로 사용자의 username을 설정
        "exp": expire, # 토큰의 만료 시간(expiration)을 설정
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) # PyJWT의 encode 함수를 사용하여 payload를 SECRET_KEY와 ALGORITHM으로 서명하여 access_token 생성

    return access_token # 생성된 access_token 반환
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password) # verify() 메서드를 사용하여 평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부 반환 

def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password) # hash() 메서드를 사용하여 평문 비밀번호를 해싱하여 반환
    