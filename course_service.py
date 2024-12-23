from sqlalchemy.orm import Session
from schema import *
from models import *
from exception import *
from utility import *
from jwt import get_current_user
from fastapi import Depends


def get_all_subjects_from_db(
    db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(status_code=401, detail="Only admins can get data")
    courses_in_db = db.query(Course).filter(Course.is_deleted == False).all()
    subjects_lst = [
        {course.lecturer_name: {course.subject_name: course.description}}
        for course in courses_in_db
    ]
    if len(subjects_lst) == 0:
        raise HTTPException(status_code=404, detail="Courses not found")
    return subjects_lst


def create_new_course_in_db(
    *,
    db: Session,
    data: CreateNewCourse,
    current_user: User = Depends(get_current_user),
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if  current_user_in_db.role != "admin":
        raise HTTPException(status_code=401, detail="Only admins can create new course")
    lecturer_in_db = db.query(User).filter(User.role == "lecturer").all()
    lecturer_lst = [lecture.id for lecture in lecturer_in_db]

    if data.teacher_id not in lecturer_lst:
        raise HTTPException(
            status_code=403, detail="Only lecturers can be added to the course"
        )
    active_lecturer = db.query(User).filter(User.is_deleted == False).all()
    active_lecturer_lst = [lecture.id for lecture in active_lecturer]
    if data.teacher_id not in active_lecturer_lst:
        raise HTTPException(status_code=404, detail="Lecturer is not found")
    deleted_course = (
        db.query(Course)
        .filter(
            Course.subject_name == data.subject_name,
            Course.teacher_id == data.teacher_id,
            Course.is_deleted == True,
        )
        .first()
    )
    if deleted_course:
        deleted_course.is_deleted = False
        db.commit()
        return {"Message": "Course created successfully"}
    if (
        db.query(Course)
        .filter(
            Course.subject_name == data.subject_name,
            Course.teacher_id == data.teacher_id,
        )
        .first()
    ):
        raise HTTPException(status_code=400, detail="Course name already exists")
    if data.teacher_id in lecturer_lst and active_lecturer_lst:
        lecturer = db.query(User).filter(User.id == data.teacher_id).first()
        new_course = Course(
            teacher_id=data.teacher_id,
            subject_name=data.subject_name,
            lecturer_name=lecturer.username,
            description=data.description,
        )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return {"Message": "Course has been created"}


def registration_in_db(
    *,
    data: RegistrationData,
    db: Session,
    current_user: User = Depends(get_current_user),
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(status_code=401, detail="Only admins can registrate")
    course_in_db = (
        db.query(Course)
        .filter(Course.subject_name == data.course_name, Course.is_deleted == False)
        .first()
    )
    if not course_in_db:
        raise HTTPException(status_code=404, detail="Course not found")
    student_in_db = (
        db.query(Student)
        .filter(Student.id == data.student_id, Student.is_deleted == False)
        .first()
    )
    if not student_in_db:
        raise HTTPException(status_code=404, detail="Student not found")
    lecturer = (
        db.query(Course).filter(Course.lecturer_name == data.lecturer_name).first()
    )
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer is not found")

    lecturer_subject = (
        db.query(Course)
        .filter(
            Course.lecturer_name == data.lecturer_name,
            Course.subject_name == data.course_name,
        )
        .first()
    )
    if not lecturer_subject:
        raise HTTPException(
            status_code=404,
            detail=f"{data.lecturer_name} don't has {data.course_name} course",
        )
    student_in_registration = (
        db.query(Registration)
        .filter(
            Registration.student_id == data.student_id,
            Registration.course_name == data.course_name,
            Registration.lecturer_name == data.lecturer_name,
        )
        .first()
    )
    if student_in_registration:
        raise HTTPException(status_code=400, detail="Student alredy registrared")
    else:
        print(student_in_db.name)
        new_student_reg = Registration(
            student_id=data.student_id,
            lecturer_name=lecturer_subject.lecturer_name,
            course_name=data.course_name,
            student_name=student_in_db.name,
        )
        db.add(new_student_reg)
        db.commit()
        db.refresh(new_student_reg)
        return {"Message": "Student has been registrated"}


def get_course_info_from_db(
    db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if current_user_in_db.role == "admin":
        raise HTTPException(
            status_code=401, detail="Only lecturers can get info about courses"
        )
    courses = db.query(Course).filter(
        Course.teacher_id == current_user_in_db.id, Course.is_deleted == False
    )
    student_regstration = db.query(Registration).filter(
        Registration.lecturer_name == current_user_in_db.username,
        Registration.is_deleted == False,
    )
    info_lst = []
    for course in courses:
        info_dict = dict()
        info_dict.update(
            {
                "lecturer_name": course.lecturer_name,
                "course_name": course.subject_name,
                "students": [],
            }
        )
        info_lst.append(info_dict)
    for i in info_lst:
        for student in student_regstration:
            if (
                i["course_name"] == student.course_name
                and i["lecturer_name"] == student.lecturer_name
            ):
                i["students"].append(student.student_name)
    return info_lst


def delete_course_from_db(
    *, id: int, db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if not current_user_in_db.role == "admin":
        raise HTTPException(status_code=401, detail="Only admins can delete course")
    course = (
        db.query(Course).filter(Course.id == id, Course.is_deleted == False).first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Not Found")
    student_in_course = (
        db.query(Registration)
        .filter(Registration.course_name == course.subject_name)
        .first()
    )
    if student_in_course:
        raise HTTPException(status_code=403, detail="You can not delete course")
    course.is_deleted = True
    db.commit()
    return {"Message": "Course has been deleted succesfully"}