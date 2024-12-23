from sqlalchemy.orm import Session
from schema import *
from models import *
from exception import *
from utility import *
from jwt import get_current_user
from fastapi import Depends


def get_grade_by_id_from_db(
    *, student_id: int, db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    if current_user_in_db.role != "admin":
        raise HTTPException(status_code=401, detail="Only admins get data")
    student = (
        db.query(Student)
        .filter(Student.id == student_id, Student.is_deleted == False)
        .all()
    )
    if not student:
        raise StudentNotFoundException()
    courses = db.query(Registration).filter(Registration.student_id == student_id).all()
    if not courses:
        return {"Message": "Student has not enrolled in any courses."}
    return [
        {
            "Lecturer_name": course.lecturer_name,
            "Course_name": course.course_name,
            "Final_point": course.final_point,
        }
        for course in courses
    ]


def get_grade_by_course_id_from_db(
    *, course_id: int, db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )
    course_in_db = (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_deleted == False)
        .first()
    )
    if not course_in_db:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user_in_db.role == "admin":
        courses = (
            db.query(Registration)
            .filter(
                Registration.course_name == course_in_db.subject_name,
                Registration.is_deleted == False,
            )
            .all()
        )
        if not courses:
            return {"Message": "There are no students in the course."}
        return [
            {
                "Lecturer_name": course.lecturer_name,
                "Course_name": course.course_name,
                "Student_name": course.student_name,
                "Final_point": course.final_point,
            }
            for course in courses
        ]
    elif current_user_in_db.role == "lecturer":
        courses = (
            db.query(Registration)
            .filter(
                Registration.course_name == course_in_db.subject_name,
                Registration.lecturer_name == current_user_in_db.username,
                Registration.is_deleted == False,
            )
            .all()
        )
        if not courses:
            raise HTTPException(status_code=404, detail="Not found")
        grade_lst = [
            {
                "Lecturer_name": course.lecturer_name,
                "Course_name": course.course_name,
                "Student_name": course.student_name,
                "Final_point": course.final_point,
            }
            for course in courses
        ]
        return grade_lst


def assign_grade_to_student_in_db(
    data: GetId,
    student_id: int,
    grade: str,
    db: Session,
    current_user: User = Depends(get_current_user),
):

    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )

    if current_user_in_db.role != "lecturer":
        raise HTTPException(status_code=403, detail="Only lecturers can assign grades")

    course_in_db = (
        db.query(Course)
        .filter(Course.id == data.course_id, Course.is_deleted == False)
        .first()
    )

    if not course_in_db:
        raise HTTPException(status_code=404, detail="Course not found")

    student_enrollment = (
        db.query(Registration)
        .filter(
            Registration.student_id == student_id,
            Registration.course_name == course_in_db.subject_name,
            Registration.lecturer_name == current_user_in_db.username,
            Registration.is_deleted == False,
        )
        .first()
    )

    if not student_enrollment:
        raise HTTPException(
            status_code=404,
            detail="Student is not enrolled in this course or not assigned to this lecturer",
        )

    valid_grades = ["A", "B", "C", "D", "F"]
    if grade not in valid_grades:
        raise HTTPException(
            status_code=400, detail="Invalid grade. Valid grades are A, B, C, D, F."
        )

    student_enrollment.final_point = grade
    db.commit()
    return {
        "message": f"Grade {grade} successfully assigned to student {student_id} for course {course_in_db.subject_name}"
    }


def get_gpa_by_student_id_from_db(
    *, student_id: int, db: Session, current_user: User = Depends(get_current_user)
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )

    if current_user_in_db.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view GPA")

    courses = (
        db.query(Registration)
        .filter(Registration.student_id == student_id, Registration.is_deleted == False)
        .all()
    )

    if not courses:
        raise HTTPException(
            status_code=404, detail="Student not enrolled in any courses"
        )

    grade_to_gpa = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}

    total_weighted_points = 0
    total_credits = 0

    for course in courses:
        if course.final_point not in grade_to_gpa:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid grade {course.final_point} in course {course.course_name}",
            )

        gpa_points = grade_to_gpa[course.final_point]

        credits = course.course_credits if hasattr(course, "course_credits") else 3
        total_weighted_points += gpa_points * credits
        total_credits += credits

    if total_credits == 0:
        raise HTTPException(
            status_code=400, detail="No credits available for GPA calculation"
        )

    gpa = total_weighted_points / total_credits
    return {"student_id": student_id, "GPA": round(gpa, 2)}


def update_grade_in_db(
    student_id: int,
    grade: str,
    data: GetId,
    db: Session,
    current_user: User = Depends(get_current_user),
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )

    if not current_user_in_db:
        raise HTTPException(status_code=404, detail="Current user not found")

    print(
        f"Current user: {current_user_in_db.username}, Role: {current_user_in_db.role}"
    )

    if current_user_in_db.role != "lecturer":
        raise HTTPException(status_code=403, detail="Only lecturers can assign grades")

    course_in_db = (
        db.query(Course)
        .filter(Course.id == data.course_id, Course.is_deleted == False)
        .first()
    )

    if not course_in_db:
        raise HTTPException(status_code=404, detail="Course not found")

    print(f"Course found: {course_in_db.subject_name}")

    student_enrollment = (
        db.query(Registration)
        .filter(
            Registration.student_id == student_id,
            Registration.course_name == course_in_db.subject_name,
            Registration.lecturer_name == current_user_in_db.username,
            Registration.is_deleted == False,
        )
        .first()
    )

    if not student_enrollment:
        raise HTTPException(
            status_code=404,
            detail="Student is not enrolled in this course or not assigned to this lecturer",
        )

    print(f"Student {student_id} is enrolled in the course {course_in_db.subject_name}")

    valid_grades = ["A", "B", "C", "D", "F"]
    if grade not in valid_grades:
        raise HTTPException(
            status_code=400, detail="Invalid grade. Valid grades are A, B, C, D, F."
        )

    print(f"Grade {grade} is valid")

    student_enrollment.final_point = grade
    db.commit()

    return {
        "message": f"Grade {grade} successfully assigned to student {student_id} for course {course_in_db.subject_name}"
    }


def delete_grade_in_db(
    data: GetId,
    student_id: int,
    db: Session,
    current_user: User = Depends(get_current_user),
):
    current_user_in_db = (
        db.query(User).filter(User.username == current_user["sub"]).first()
    )

    if not current_user_in_db:
        raise HTTPException(status_code=404, detail="Current user not found")

    if current_user_in_db.role != "lecturer":
        raise HTTPException(status_code=403, detail="Only lecturers can delete grades")

    course_in_db = (
        db.query(Course)
        .filter(Course.id == data.course_id, Course.is_deleted == False)
        .first()
    )

    if not course_in_db:
        raise HTTPException(status_code=404, detail="Course not found")

    student_enrollment = (
        db.query(Registration)
        .filter(
            Registration.student_id == student_id,
            Registration.course_name == course_in_db.subject_name,
            Registration.lecturer_name == current_user_in_db.username,
            Registration.is_deleted == False,
        )
        .first()
    )

    if not student_enrollment:
        raise HTTPException(
            status_code=404,
            detail="Student is not enrolled in this course or not assigned to this lecturer",
        )

    if student_enrollment.final_point == None:
        raise HTTPException(status_code=404, detail="Grade not found")
    student_enrollment.final_point = None
    db.commit()

    return {
        "message": f"Grade for student {student_id} in course {course_in_db.subject_name} has been removed."
    }
