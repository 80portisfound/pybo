from pydantic import BaseModel, Field

class ChunkCreate(BaseModel): # 청크 생성 요청을 위한 Pydantic 모델 정의, content 필드를 포함
    content: str = Field(min_length=1) # 최소 1자
    chunk_index : int = Field(ge=0) # 0 이상인 정수
    page_id: str = Field(min_length=1) # 최소 1자
    page_title: str = Field(min_length=1) # 최소 1자
    page_path: str = Field(min_length=1) # 최소 1자


class ChunkResponse(BaseModel): # 청크 응답을 위한 Pydantic 모델 정의, id, content, chunk_index 필드를 포함
    id: int
    document_id: int
    content: str = Field(min_length=1) # 최소 1자
    chunk_index : int = Field(ge=0) # 0 이상인 정수

    page_id: str | None = None
    page_title: str | None = None
    page_path: str | None = None
