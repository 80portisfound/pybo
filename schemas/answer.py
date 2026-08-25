from pydantic import BaseModel, Field # Pydantic의 BaseModel과 Field를 임포트하여 데이터 검증 및 모델 정의에 사용

class AnswerCreate(BaseModel): # 답변 생성 요청을 위한 Pydantic 모델 정의, content 필드를 포함
    content: str = Field(min_length=1)

class AnswerResponse(BaseModel): # 답변 응답을 위한 Pydantic 모델 정의, id, question_id, content 필드를 포함
    id: int
    question_id: int
    content: str

class AnswerUpdate(BaseModel): # 답변 수정 요청을 위한 Pydantic 모델 정의, content 필드를 포함
    content: str = Field(min_length=1)