from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, DeclarativeBase 

DATABASE_URL = "sqlite:///./pybo.db" # 데이터 베이스 URL, SQLite를 사용하며 현재 디렉토리에 pybo.db 파일을 생성

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, # 커넥션을 만든 스레드에서만 그 커넥션을 사용할 수 있도록 하는 SQLite의 기본 동작을 해제
)

SessionLocal = sessionmaker( #SessionLocal은 데이터베이스 세션을 생성하는 팩토리 역할을 하는 클래스
    autocommit=False, # 자동 커밋 기능을 비활성화, 트랜잭션을 명시적으로 커밋해야 함
    autoflush=False, # 자동 플러시 기능을 비활성화, 세션에 추가된 객체를 자동으로 데이터베이스에 반영하지 않음
    bind=engine,    # 데이터베이스 연결을 위해 생성된 엔진을 바인딩
)


class Base(DeclarativeBase): # 이 클래스 상속한 모델들이 전부 이 Base를 상속받게 되며, SQLAlchemy의 ORM 기능을 활용할 수 있게 됨
    pass

def get_db(): # 데이터베이스 세션을 생성하고 반환하는 함수
    db = SessionLocal() # 데이터베이스 세션 생성
    try:
        yield db # 생성된 세션 반환
    finally:
        db.close() # 세션 종료
