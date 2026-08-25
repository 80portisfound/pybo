from pydantic import BaseModel, Field # Pydantic의 BaseModel과 Field를 임포트하여 데이터 검증 및 모델 정의에 사용


class QuestionCreate(BaseModel): # 질문 생성 요청을 위한 Pydantic 모델 정의, subject와 content 필드를 포함
    subject: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=1)

class QuestionResponse(BaseModel): # 질문 응답을 위한 Pydantic 모델 정의, id, subject, content 필드를 포함
    id: int
    subject: str
    content: str

class QuestionUpdate(BaseModel): # 질문 수정 요청을 위한 Pydantic 모델 정의, subject와 content 필드를 포함
    subject: str | None = Field(
        default=None, 
        min_length=2, 
        max_length=100,
    )
    content: str | None = Field(
        default=None,
        min_length=1
    )
