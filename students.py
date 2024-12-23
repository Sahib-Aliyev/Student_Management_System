from fastapi import APIRouter, Depends
from jwt import get_current_user
from sqlalchemy.orm import Session
from db import get_db
from schema import *
from student_service import *

student_router = APIRouter(tags=["Student"])


@student_router.get("/student")
def get_all_student(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    message = get_all_student_from_db(current_user=current_user, db=db)
    return message


@student_router.post("/student")
def create_new_student(
    *,
    item: CreateNewStudent,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    message = create_new_student_in_db(data=item, current_user=current_user, db=db)
    return message


@student_router.delete("/student/{id}")
def delete_student(
    id, 
    current_user=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    message = delete_student_from_db(id=id, current_user=current_user, db=db)
    return message


@student_router.get("/student/{id}")
def get_all_student_data(
    id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    message = get_all_student_data_from_db(id=id, current_user=current_user, db=db)
    return message