from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas.question import QuestionCreate, QuestionUpdate

import models


def get_question(
    db: Session,
    question_id: int,
):
    return db.get(   # 데이터베이스에서 주어진 question_id에 해당하는 Question 객체를 조회
        models.Question,
        question_id,
    )


def get_questions( # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db: Session,
    skip: int = 0,
    limit: int = 10,
    keyword: str | None = None,
):
    statement = select(models.Question)

    if keyword: # keyword가 제공되면 subject 필드에서 해당 키워드를 포함하는 질문을 필터링
        statement = statement.where(
            models.Question.subject.contains(keyword)
        )

    statement = ( # offset와 limit를 적용하여 페이징 처리
        statement
        .offset(skip)
        .limit(limit)
    )

    questions = db.scalars(statement).all() # 쿼리 실행 후 결과를 리스트로 반환

    return questions

def create_question(question: QuestionCreate, db: Session, author_id: int): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question = models.Question(subject=question.subject, content=question.content, author_id=author_id) # 모델 인스턴스 생성
    db.add(db_question) # 세션에 추가   
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_question) # 새로 생성된 객체를 세션에 반영
    return db_question # 생성된 질문 객체 반환

def update_question(db : Session, db_question: models.Question, question: QuestionCreate): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question.subject = question.subject # subject 필드 업데이트
    db_question.content = question.content # content 필드 업데이트
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_question) # 수정된 객체를 세션에 반영
    return db_question # 수정된 질문 객체 반환
    
def delete_question(db: Session, db_question: models.Question): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db.delete(db_question)
    db.commit()

def patch_question(db: Session, db_question: models.Question, question: QuestionUpdate): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    if question.subject is not None: # subject 필드가 None이 아닐 경우에만 업데이트
        db_question.subject = question.subject # subject 필드 업데이트
    if question.content is not None: # content 필드가 None이 아닐 경우에만 업데이트
        db_question.content = question.content # content 필드 업데이트
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_question) # 수정된 객체를 세션에 반영
    return db_question # 수정된 질문 객체 반환