from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas.answer import AnswerCreate, AnswerUpdate

import models

def get_answer(
    db: Session,
    answer_id: int,
):
    return db.get(
        models.Answer,
        answer_id,
    )


def get_answers( # 특정 질문에 대한 답변 목록을 조회하는 함수 정의
    db: Session, # 데이터베이스 세션은 get_db 종속성을 통해 주입
    question_id: int, # 질문 ID를 기반으로 특정 질문에 대한 답변 목록을 조회
):
    statement = select(models.Answer).where(models.Answer.question_id == question_id) # SQLAlchemy의 select 문을 사용하여 Answer 모델에서 해당 질문 ID를 가진 답변 조회
    answers = db.scalars(statement).all() # 쿼리 실행 후 결과를 리스트로 변환
    return answers # 조회된 답변 목록 반환

def create_answer(answer: AnswerCreate, db: Session, question_id: int, author_id: int): # 특정 질문에 대한 답변을 생성하는 함수 정의
    db_answer = models.Answer(question_id=question_id, content=answer.content, author_id=author_id) # 모델 인스턴스 생성
    db.add(db_answer) # 세션에 추가
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_answer) # 새로 생성된 객체를 세션에 반영
    return db_answer # 생성된 답변 객체 반환

def update_answer(db: Session, db_answer: models.Answer, answer: AnswerUpdate): # 특정 답변을 수정하는 함수 정의
    db_answer.content = answer.content # content 필드 업데이트
    db.commit() # 커밋하여 데이터베이스에 반영
    db.refresh(db_answer) # 수정된 객체를 세션에 반영
    return db_answer # 수정된 답변 객체 반환

def delete_answer(db: Session, db_answer: models.Answer): # 특정 답변을 삭제하는 함수 정의
    db.delete(db_answer) # 세션에서 객체 삭제
    db.commit() # 커밋하여 데이터베이스에 반영