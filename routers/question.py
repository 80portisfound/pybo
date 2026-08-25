from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select 
from schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
import models
from database import get_db
from auth import get_current_user
from crud import question as question_crud


router = APIRouter(tags=["Questions"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능

@router.get(
    "/questions/{question_id}",
    response_model=QuestionResponse,
) # 질문 ID를 기반으로 특정 질문을 조회하는 엔드포인트 정의, 요청 경로 매개변수로 question_id를 사용하고, 응답은 QuestionResponse 모델을 사용
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
): #  데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question = question_crud.get_question(
        db,
        question_id,
    ) # crud 모듈의 get_question 함수를 호출하여 데이터베이스에서 해당 ID를 가진 질문 조회

    if db_question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        ) # 404 Not Found 예외 발생

    return db_question # 조회된 질문 객체 반환
     
@router.get("/questions",
            response_model=list[QuestionResponse],  # 응답 모델을 Question 모델의 리스트로 지정
        ) # 질문 목록을 조회하는 엔드포인트 정의, skip과 limit 쿼리 파라미터를 통해 페이징 처리 가능
def get_questions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    keyword: str | None = Query(default=None, min_length=1, max_length=100), # 검색 키워드 쿼리 파라미터, 최소 1자, 최대 100자
    db: Session = Depends(get_db) # 데이터베이스 세션은 get_db 종속성을 통해 주입
):
    return question_crud.get_questions(
        db,
        skip=skip,
        limit=limit,
        keyword=keyword,
    ) # crud 모듈의 get_questions 함수를 호출하여 데이터베이스에서 질문


@router.post("/questions", response_model=QuestionResponse, status_code=201) # 질문 생성 엔드포인트 정의, 요청 본문은 QuestionCreate 모델을 사용하고, 응답은 QuestionResponse 모델을 사용하며 상태 코드는 201(Created)로 설정
def create_question(question: QuestionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    return question_crud.create_question(question, db, current_user.id) # crud 모듈의 create_question 함수를 호출하여 데이터베이스에 질문 생성


@router.put("/questions/{question_id}", response_model=QuestionResponse) # 질문 수정 엔드포인트 정의, 요청 본문은 QuestionCreate 모델을 사용하고, 응답은 QuestionResponse 모델을 사용
def update_question(question_id: int, question: QuestionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question = question_crud.get_question(db, question_id) # crud 모듈의 get_question 함수를 호출하여 데이터베이스에서 해당 ID를 가진 질문 조회
    if db_question is None: # 질문이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Question not found") # 404 Not Found 예외 발생
    if db_question.author_id != current_user.id: # 질문의 작성자와 현재 사용자가 다를 경우
        raise HTTPException(status_code=403, detail="Not authorized to update this question") # 403 Forbidden 예외 발생
    return question_crud.update_question(db, db_question, question) # crud 모듈의 update_question 함수를 호출하여 질문 수정

@router.delete("/questions/{question_id}", status_code=204) # 질문 삭제 엔드포인트 정의, 상태 코드는 204(No Content)로 설정
def delete_question(question_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question = question_crud.get_question(db, question_id) # crud 모듈의 get_question 함수를 호출하여 데이터베이스에서 해당 ID를 가진 질문 조회
    if db_question is None: # 질문이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Question not found") # 404 Not Found 예외 발생
    if db_question.author_id != current_user.id: # 질문의 작성자와 현재 사용자가 다를 경우
        raise HTTPException(status_code=403, detail="Not authorized to delete this question") # 403 Forbidden 예외 발생
    question_crud.delete_question(db, db_question) # crud 모듈의 delete_question 함수를 호출하여 질문 삭제
    return None # 삭제 후 반환값 없음

@router.patch("/questions/{question_id}", response_model=QuestionResponse) # 질문 부분 수정 엔드포인트 정의, 요청 본문은 QuestionUpdate 모델을 사용하고, 응답은 QuestionResponse 모델을 사용
def patch_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question = question_crud.get_question(db, question_id) # crud 모듈의 get_question 함수를 호출하여 데이터베이스에서 해당 ID를 가진 질문 조회
    if db_question is None: # 질문이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Question not found") # 404 Not Found 예외 발생
    if db_question.author_id != current_user.id: # 질문의 작성자와 현재 사용자가 다를 경우
        raise HTTPException(status_code=403, detail="Not authorized to update this question") # 403 Forbidden 예외 발생
    return question_crud.patch_question(db, db_question, question) # crud 모듈의 patch_question 함수를 호출하여 질문 부분 수정
