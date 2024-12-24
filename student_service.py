from sqlalchemy.orm import Session
from schema import *
from models import *
from exception import *
from utility import *
from jwt import get_current_user
from fastapi import Depends


def get_all_student_from_db(
    db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(status_code=401, detail="Only admins can get data")
    students = db.query(Student).filter(Student.is_deleted == False).all()
    students_lst= [
        {"Id": student.id, "Name": student.name, "Surname": student.surname}
        for student in students
    ]
    if len(students_lst)==0:
        return {"Message":"There are no students in the db."}
    return students_lst

def create_new_student_in_db(
    *,
    db: Session,
    data: CreateNewStudent,
    current_user: User = Depends(get_current_user),
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(
            status_code=401, detail="Only admins can create new student"
        )
    student_in_db = db.query(Student).filter(Student.fin == data.fin).first()
    fin_list = []
    students = db.query(Student).filter(Student.is_deleted == False).all()
    for student in students:
        fin_list.append(student.fin)
    if not student_in_db:
        new_student = Student(
            name=data.name,
            surname=data.surname,
            fin=data.fin,
            birth_date=data.birth_date,
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return {"Message": "Student has been created"}

    if student_in_db.fin == data.fin and student_in_db.is_deleted == True:
        student_in_db.name = data.name
        student_in_db.surname = data.surname
        student_in_db.is_deleted = False
        student_in_db.birth_date = data.birth_date
        student_in_db.fin = data.fin
        db.commit()
        return {"Message": "Student has been created"}
    if student_in_db.fin == data.fin and student_in_db.is_deleted == False:
        raise StudentAlreadyExist()


def delete_student_from_db(
    *, id: int, db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(status_code=401, detail="Only admins delete student")
    student_in_db = db.query(Student).filter(Student.id == id).first()
    if not student_in_db:
        raise StudentNotFoundException()
    elif student_in_db.is_deleted == True:
        raise StudentNotFoundException()
    student_in_db.is_deleted = True
    db.commit()
    return {
        "Message": f"Student {student_in_db.name} with {student_in_db.id} id has been deleted successfully "
    }


def get_all_student_data_from_db(
    *, id: int, db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(status_code=401, detail="Only admins delete student")
    student_in_db = (
        db.query(Student).filter(Student.id == id, Student.is_deleted == False).first()
    )
    if not student_in_db:
        raise StudentNotFoundException()
    courses = db.query(Registration).filter(Registration.student_id == id).all()
    lst_course = [
        {
            "Lecturer_name": course.lecturer_name,
            "Course_name": course.course_name,
            "Final_point": course.final_point,
        }
        for course in courses
    ]
    if not courses:
        lst_course = "Student did not enter course"
    return {
        "Name": student_in_db.name,
        "Surname": student_in_db.surname,
        "Fin": student_in_db.fin,
        "birth_date": student_in_db.birth_date,
        "Course_info": lst_course,
    }