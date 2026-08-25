from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class Question(Base): #ORM 모델
    __tablename__ = "question" # DB의 실제 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True) # Python/SQLAlchemy 측 컬럼 타입 & Primary Key 컬럼
    subject: Mapped[str] = mapped_column(String(200), nullable=False) # 최대 200자, Null 허용 X
    content: Mapped[str] = mapped_column(Text(), nullable=False) # Text 타입(길이가 긴 문자열), null 허용 X
    answers: Mapped[list["Answer"]] = relationship(back_populates="question") # Answer 모델과의 관계 설정, Question 객체를 통해 관련된 Answer 객체들을 조회 가능
    author_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True) # 기존 질문은 작성자 정보가 없으므로 null 허용
    author: Mapped["User | None"] = relationship(back_populates="questions") # User 모델과의 관계 설정, Question 객체를 통해 관련된 User 객체를 조회 가능

class Answer(Base): #ORM 모델
    __tablename__ = "answer" # DB의 실제 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True) # Python/SQLAlchemy 측 컬럼 타입 & Primary Key 컬럼
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False) # Foreign Key 설정, Question 테이블의 id 컬럼 참조, null 허용 X
    content: Mapped[str] = mapped_column(Text(), nullable=False) # Text 타입(길이가 긴 문자열), null 허용 X
    question: Mapped["Question"] = relationship(back_populates="answers") # Question 모델과의 관계 설정, Answer 객체를 통해 관련된 Question 객체를 조회 가능, back_populates를 통해 양방향 관계 설정(1:N 관계)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True) # 기존 답변은 작성자 정보가 없으므로 null 허용
    author: Mapped["User | None"] = relationship(back_populates="answers") # User 모델과의 관계 설정, Answer 객체를 통해 관련된 User 객체를 조회 가능, back_populates를 통해 양방향 관계 설정(1:N 관계)    

class User(Base) : # 사용자 ORM 모델
    __tablename__ = "user" # DB의 실제 테이블 이름

    id : Mapped[int] = mapped_column(primary_key=True) # Python/SQLAlchemy 측 컬럼 타입 & Primary Key 컬럼
    username : Mapped[str] = mapped_column(String(50), nullable=False, unique=True, ) # 최대 50자, Null 허용 X, 유니크 제약 조건
    password_hash : Mapped[str] = mapped_column(String(255), nullable=False) # 최대 255자, Null 허용 X
    questions: Mapped[list["Question"]] = relationship(back_populates="author") # Question 모델과의 관계 설정, User 객체를 통해 관련된 Question 객체들을 조회 가능
    answers: Mapped[list["Answer"]] = relationship(back_populates="author") # Answer 모델과의 관계 설정, User 객체를 통해 관련된 Answer 객체들을 조회 가능

class Document(Base) : # 문서 ORM 모델
    __tablename__ = "document" # DB의 실제 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True) # Python/SQLAlchemy 측 컬럼 타입 & Primary Key 컬럼
    title : Mapped[str] = mapped_column(String(200), nullable=False) # 최대 200자, Null 허용 X
    source : Mapped[str] = mapped_column(String(200), nullable=False) # 최대 200자, Null 허용 X
    notion_page_id : Mapped[str] = mapped_column(String(200), nullable=False, unique=True) # 최대 200자, Null 허용 O, 유니크 제약 조건
    last_edited_time : Mapped[str] = mapped_column(String(200), nullable=False) # 최대 200자, Null 허용 X
    chunks : Mapped[list["Chunk"]] = relationship(back_populates="document") # Chunk 모델과의 관계 설정, Document 객체를 통해 관련된 Chunk 객체들을 조회 가능

class Chunk(Base) : # 문서 조각 ORM 모델
    __tablename__ = "chunk" # DB의 실제 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True) # Python/SQLAlchemy 측 컬럼 타입 & Primary Key 컬럼
    document_id : Mapped[int] = mapped_column(ForeignKey("document.id"), nullable=False) # Foreign Key 설정, Document 테이블의 id 컬럼 참조, null 허용 X
    content : Mapped[str] = mapped_column(Text(), nullable=False) # Text 타입(길이가 긴 문자열), null 허용 X
    chunk_index : Mapped[int] = mapped_column(nullable=False) # 조각의 순서를 나타내는 인덱스, null 허용 X
    page_id : Mapped[str | None] = mapped_column(String(200), nullable=True) # 최대 200자, Null 허용 , Notion 페이지 ID
    page_title : Mapped[str | None] = mapped_column(String(200), nullable=True) # 최대 200자, Null 허용 , Notion 페이지 제목
    page_path : Mapped[str | None] = mapped_column(String(200), nullable=True) # 최대 200자, Null 허용, Notion 페이지 경로
    document : Mapped["Document"] = relationship(back_populates="chunks") # Document 모델과의 관계 설정, Chunk 객체를 통해 관련된 Document 객체를 조회 가능, back_populates를 통해 양방향 관계 설정(1:N 관계)
