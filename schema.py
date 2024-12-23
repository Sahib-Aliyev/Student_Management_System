from pydantic import BaseModel
from datetime import date
from typing import Optional


class CreateNewUser(BaseModel):
    password: str
    role: str

    class Config:
        extra = "forbid"


class CreateNewStudent(BaseModel):
    name: str
    surname: str
    fin: str
    birth_date: date


class CreateNewCourse(BaseModel):
    teacher_id: int
    subject_name: str
    description: str


class RegistrationData(BaseModel):
    student_id: int
    lecturer_name: str
    course_name: str


class GetId(BaseModel):
    course_id: int