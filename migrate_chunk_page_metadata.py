from sqlalchemy import inspect, text
from database import engine

existing_columns = { # 기존 chunk 테이블의 컬럼 이름을 가져와서 집합으로 저장
    column["name"]
    for column in inspect(engine).get_columns("chunk")
}

with engine.begin() as connection:
    if "page_id" not in existing_columns:
        # ALTER TABLE 문을 사용하여 chunk 테이블에 page_id 컬럼 추가
        connection.execute(text("ALTER TABLE chunk ADD COLUMN page_id VARCHAR(200)"))
    if "page_title" not in existing_columns:
        # ALTER TABLE 문을 사용하여 chunk 테이블에 page_title 컬럼 추가
        connection.execute(text("ALTER TABLE chunk ADD COLUMN page_title VARCHAR(200)"))
    if "page_path" not in existing_columns: 
        # ALTER TABLE 문을 사용하여 chunk 테이블에 page_path 컬럼 추가
        connection.execute(text("ALTER TABLE chunk ADD COLUMN page_path VARCHAR(200)")) 

