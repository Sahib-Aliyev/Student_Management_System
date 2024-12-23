from fastapi import APIRouter, Depends
from jwt import get_current_user
from sqlalchemy.orm import Session
from db import get_db
from schema import *
from grade_service import *

grade_router = APIRouter(tags=["Grade"])


@grade_router.get("/grade/{student_id}")
def get_grade_by_id(
    *, student_id, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = get_grade_by_id_from_db(
        student_id=student_id, current_user=current_user, db=db
    )
    return message


@grade_router.get("/grades/{course_id}")
def get_grade_by_course_id(
    *, course_id, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = get_grade_by_course_id_from_db(
        course_id=course_id, current_user=current_user, db=db
    )
    return message


@grade_router.post("/grade/{course_id}")
def assign_grade_to_student(
    *,
    student_id,
    grade,
    item: GetId,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    message = assign_grade_to_student_in_db(
        student_id=student_id, grade=grade, data=item, current_user=current_user, db=db
    )
    return message


@grade_router.get("/grade/gpa/{student_id}")
def get_gpa_by_student_id(
    *, student_id, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    message = get_gpa_by_student_id_from_db(
        student_id=student_id, current_user=current_user, db=db
    )
    return message


@grade_router.put("/grade/{course_id}")
def update_grade(
    *,
    student_id,
    grade,
    item: GetId,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    message = update_grade_in_db(
        student_id=student_id, grade=grade, data=item, db=db, current_user=current_user
    )
    return message


@grade_router.delete("/grade/{course_id}")
def delete_grade(
    *,
    student_id,
    item: GetId,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    message = delete_grade_in_db(
        student_id=student_id, data=item, db=db, current_user=current_user
    )
    return message
