from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import question, answer, user, document, chunk, notion,search
import models
from database import Base, engine

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()  # API 경로와 설정을 등록하는 중심 객체
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(question.router)  # question.py의 router를 FastAPI 앱에 등록
app.include_router(answer.router)  # answer.py의 router를 FastAPI 앱에 등록
app.include_router(user.router)  # user.py의 router를 FastAPI 앱에 등록
app.include_router(document.router)  # document.py의 router를 FastAPI 앱에 등록
app.include_router(chunk.router)  # chunk.py의 router를 FastAPI 앱에 등록
app.include_router(notion.router)  # notion.py의 router를 FastAPI 앱에 등록
app.include_router(search.router)  # search.py의 router를 FastAPI 앱에 등록

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}

Base.metadata.create_all(bind=engine) # 데이터베이스 테이블 생성, Base를 상속받은 모든 모델의 테이블을 생성, 이미 존재하면 무시
