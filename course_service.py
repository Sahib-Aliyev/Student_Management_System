from sqlalchemy import desc
from sqlalchemy.orm import Session
from schema import *
from db import get_db
from models import *
from exception import *
from utility import *
from jwt import get_current_user
from fastapi import Depends

def get_all_subjects_from_db(db: Session ,current_user: User= Depends(get_current_user)):
    current_user_in_db=db.query(User).filter(User.username==current_user['sub']).first()
    if not current_user_in_db.role=="admin":
        raise HTTPException(status_code=401, detail="Only admins can get data")
    courses_in_db=db.query(Course).filter(Course.is_deleted == False).all()
    subjects_lst = [{course.lecturer_name:{course.subject_name: course.description}} for course in courses_in_db]
    return subjects_lst

def create_new_course_in_db(*,db:Session , data :CreateNewCourse ,current_user:User= Depends(get_current_user)):
    current_user_in_db=db.query(User).filter(User.username==current_user['sub']).first()
    if not current_user_in_db.role=="admin":
        raise HTTPException(status_code=401, detail="Only admins can create new course")
    lecturer_in_db=db.query(User).filter(User.role=="lecturer" ).all()
    lecturer_lst=[ lecture.id for lecture in lecturer_in_db ]
    
    if data.teacher_id not in lecturer_lst:
        raise HTTPException(status_code=403 , detail="Only lecturers can be added to the course")
    active_lecturer=db.query(User).filter(User.is_deleted==False ).all()
    active_lecturer_lst=[lecture.id for lecture in active_lecturer]
    if data .teacher_id not in active_lecturer_lst:
        raise HTTPException(status_code=404 , detail="Lecturer is not found")
    if db.query(Course).filter(Course.subject_name == data.subject_name,Course.teacher_id==data.teacher_id).first():
        raise HTTPException(status_code=400, detail="Course name already exists")
    if data.teacher_id in lecturer_lst and active_lecturer_lst:
        lecturer=db.query(User).filter(User.id==data.teacher_id).first()
        new_course= Course(teacher_id=data.teacher_id,subject_name=data.subject_name , lecturer_name=lecturer.username,description=data.description)
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return {"Message": "Course has been created"}


def registration_in_db(*,data:RegistrationData,db:Session , current_user:User= Depends(get_current_user)):
    current_user_in_db=db.query(User).filter(User.username==current_user['sub']).first()
    if not current_user_in_db.role=="admin":
        raise HTTPException(status_code=401, detail="Only admins can registrate")
    course_in_db=db.query(Course).filter(Course.subject_name==data.course_name,Course.is_deleted==False).first()
    if not course_in_db:
        raise HTTPException(status_code=404,detail="Course not found")
    student_in_db=db.query(Student).filter(Student.id==data.student_id,Student.is_deleted==False).first()
    if not student_in_db:
        raise HTTPException(status_code=404,detail="Student not found")
    lecturer=db.query(Course).filter(Course.lecturer_name==data.lecturer_name).first()
    if not lecturer:
        raise HTTPException(status_code=404,detail="Lecturer is not found")

    lecturer_subject=db.query(Course).filter(Course.lecturer_name==data.lecturer_name,Course.subject_name==data.course_name).first()
    if not lecturer_subject:
        raise HTTPException(status_code=404,detail=f"{data.lecturer_name} don't has {data.course_name} course")
    student_in_registration=db.query(Registration).filter(Registration.student_id==data.student_id,Registration.course_name==data.course_name,Registration.lecturer_name==data.lecturer_name).first()
    if student_in_registration:
        raise HTTPException(status_code=400,detail="Student alredy registrared")
    else:
        print(student_in_db.name)
        new_student_reg = Registration(student_id=data.student_id,lecturer_name=lecturer_subject.lecturer_name, course_name=data.course_name,student_name=student_in_db.name)
        db.add(new_student_reg)
        db.commit()
        db.refresh(new_student_reg)
        return {"Message": "Student has been registrated"}