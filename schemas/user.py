from pydantic import BaseModel, Field # Pydantic의 BaseModel과 Field를 임포트하여 데이터 검증 및 모델 정의에 사용

class UserCreate(BaseModel): # 사용자 생성 요청을 위한 Pydantic 모델 정의, username과 password 필드를 포함
    username: str = Field(min_length=3, max_length=50) # 최소 3자, 최대 50자
    password: str = Field(min_length=8) # 최소 8자

class UserResponse(BaseModel): # 사용자 응답을 위한 Pydantic 모델 정의, id와 username 필드를 포함
    id: int
    username: str

class TokenResponse(BaseModel): # 토큰 응답을 위한 Pydantic 모델 정의, access_token과 token_type 필드를 포함
    access_token: str
    token_type: str
