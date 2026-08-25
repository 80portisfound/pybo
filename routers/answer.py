from fastapi import APIRouter, Depends, HTTPException # FastAPI의 APIRouter, Depends, HTTPException을 임포트하여 라우터 정의 및 예외 처리에 사용
from sqlalchemy.orm import Session # SQLAlchemy의 Session을 임포트하여 데이터베이스 세션을 관리
from sqlalchemy import select # SQLAlchemy의 select를 임포트하여 데이터베이스 쿼리 작성에 사용
from schemas.answer import AnswerCreate, AnswerResponse, AnswerUpdate # Pydantic 모델을 임포트하여 요청 및 응답 데이터 검증에 사용
import models
from database import get_db # 데이터베이스 세션을 가져오는 함수 임포트 
from auth import get_current_user # 현재 사용자 정보를 가져오는 함수 임포트
from fastapi.security import OAuth2PasswordBearer # FastAPI의 OAuth2PasswordBearer를 임포트하여 OAuth2 인증에 사용
from crud import answer as answer_crud # crud 모듈에서 answer 관련 함수를 임포트하여 데이터베이스 작업에 사용
from crud import question as question_crud # crud 모듈에서 question 관련 함수를 임포트하여 데이터베이스 작업에 사용
router = APIRouter(tags=["Answers"])  # 라우터 객체 생성, 태그를 통해 API 문서에서 그룹화 가능

@router.get(
    "/answers/{answer_id}", 
    response_model=AnswerResponse,
    ) # 답변 ID를 기반으로 특정 답변을 조회하는 엔드포인트 정의
def get_answer(answer_id: int, db: Session = Depends(get_db)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    answer = answer_crud.get_answer(db, answer_id) # CRUD 함수를 사용하여 데이터베이스에서 답변 조회
    if answer is None: # 답변이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Answer not found") # 404 Not Found 예외 발생
    return answer # 조회된 답변 객체 반환

@router.get(
    "/questions/{question_id}/answers",
    response_model=list[AnswerResponse],
) # 특정 질문에 대한 답변 목록을 조회하는 엔드포인트 정의, 응답 모델은 AnswerResponse 모델의 리스트로 지정
def get_answers( question_id: int,db: Session = Depends(get_db),): # 데이터베이스 세션은 get_db 종속성을 통해 주입  
        db_question = question_crud.get_question(db, question_id) # CRUD 함수를 사용하여 데이터베이스에서 질문 조회
        if db_question is None: # 질문이 존재하지 않을 경우
            raise HTTPException(status_code=404, detail="Question not found") # 404 Not Found 예외 발생
        
        return answer_crud.get_answers(db, question_id) # CRUD 함수를 사용하여 데이터베이스에서 해당 질문에 대한 답변 목록 조회 및 반환


@router.post("/questions/{question_id}/answers", response_model=AnswerResponse, status_code=201) # 특정 질문에 대한 답변을 생성하는 엔드포인트 정의
def create_answer(question_id: int, answer: AnswerCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_question = question_crud.get_question(db, question_id) # CRUD 함수를 사용하여 데이터베이스에서 질문 조회
    if db_question is None: # 질문이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Question not found") # 404 Not Found 예외 발생
    return answer_crud.create_answer(answer, db, question_id, current_user.id) # CRUD 함수를 사용하여 데이터베이스에 답변 생성 및 반환

@router.put("/answers/{answer_id}", response_model=AnswerResponse, status_code=200) # 특정 답변을 수정하는 엔드포인트 정의
def update_answer(answer_id: int, answer: AnswerUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_answer = answer_crud.get_answer(db, answer_id) # CRUD 함수를 사용하여 데이터베이스에서 답변 조회
    if db_answer is None: # 답변이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Answer not found") # 404 Not Found 예외 발생
    if db_answer.author_id != current_user.id: # 답변의 작성자와 현재 사용자가 다를 경우
        raise HTTPException(status_code=403, detail="Not authorized to update this answer") # 403 Forbidden 예외 발생
    return answer_crud.update_answer(db, db_answer, answer) # CRUD 함수를 사용하여 데이터베이스에서 답변 수정 및 반환

@router.delete("/answers/{answer_id}", status_code=204) # 특정 답변을 삭제하는 엔드포인트 정의, 상태 코드는 204(No Content)로 설정
def delete_answer(answer_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): # 데이터베이스 세션은 get_db 종속성을 통해 주입
    db_answer = answer_crud.get_answer(db, answer_id) # CRUD 함수를 사용하여 데이터베이스에서 답변 조회
    if db_answer is None: # 답변이 존재하지 않을 경우
        raise HTTPException(status_code=404, detail="Answer not found") # 404 Not Found 예외 발생
    if db_answer.author_id != current_user.id: # 답변의 작성자와 현재 사용자가 다를 경우
        raise HTTPException(status_code=403, detail="Not authorized to delete this answer") # 403 Forbidden 예외 발생
    answer_crud.delete_answer(db, db_answer) # CRUD 함수를 사용하여 데이터베이스에서 답변 삭제
    return None # 삭제 후 반환할 내용 없음



