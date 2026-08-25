from pydantic import BaseModel, Field # Pydantic의 BaseModel과 Field를 임포트하여 데이터 검증 및 모델 정의에 사용

class DocumentCreate(BaseModel): # 문서 생성 요청을 위한 Pydantic 모델 정의, title과 content 필드를 포함
    title: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자
    source: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자
    notion_page_id: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자
    last_edited_time: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자


class DocumentResponse(BaseModel): # 문서 응답을 위한 Pydantic 모델 정의, id, title, source 필드를 포함
    id: int 
    title: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자
    source: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자
    notion_page_id: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자
    last_edited_time: str = Field(min_length=1, max_length=200) # 최소 1자, 최대 200자

