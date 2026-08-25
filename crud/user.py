from sqlalchemy import select
from sqlalchemy.orm import Session

import models


def get_user_by_username(db: Session, username: str):
    statement = select(models.User).where(models.User.username == username)
    return db.scalars(statement).first()


def create_user(db: Session, username: str, password_hash: str):
    db_user = models.User(username=username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
