from fastapi import APIRouter, Depends
from jwt import get_current_user
from sqlalchemy.orm import Session
from db import get_db
from schema import *
from users_service import *

user_router = APIRouter(tags=["User"])


@user_router.get("/user")
def get_current_username(current_user=Depends(get_current_user)):
    return {"username": current_user["sub"]}


@user_router.post("/user")
def create_new_user(username: str, item: CreateNewUser, db: Session = Depends(get_db)):
    message = create_new_user_in_db(username=username, data=item, db=db)
    return message


@user_router.delete("/user")
def delete_user(
    username: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = delete_user_from_db(username=username, db=db, current_user=current_user)
    return message