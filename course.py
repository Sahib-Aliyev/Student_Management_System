from fastapi import APIRouter, Depends
from jwt import get_current_user
from sqlalchemy.orm import Session
from db import get_db
from schema import *
from course_service import *

course_router = APIRouter(tags=["Course"])


@course_router.get("/course")
def get_all_subjects(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = get_all_subjects_from_db(current_user=current_user, db=db)
    return message


@course_router.post("/course")
def create_new_course(
    *,
    item: CreateNewCourse,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    message = create_new_course_in_db(data=item, db=db, current_user=current_user)
    return message


@course_router.post("/register_course")
def regisrtation(
    *,
    item: RegistrationData,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    message = registration_in_db(data=item, db=db, current_user=current_user)
    return message


@course_router.get("/course_info_for_lecturers")
def get_course_info(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = get_course_info_from_db(current_user=current_user, db=db)
    return message


@course_router.delete("/course/{id}")
def delete_course(
    *, id, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = delete_course_from_db(id=id, current_user=current_user, db=db)
    return message