from sqlalchemy import Column, Integer, String , Boolean , Float
from db import Base, engine


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)
    is_deleted = Column(Boolean, default=False)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    fin = Column(String,unique=True)
    birth_date = Column(String)
    is_deleted = Column(Boolean, default=False)


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    description = Column(String)
    is_deleted = Column(Boolean, default=False)


class Registration(Base):
    __tablename__ = "student_course_registration"
    id = Column(Integer, primary_key=True)
    course_name = Column(String)
    student_name = Column(String)
    final_point = Column(Float)
    description = Column(String)
    is_deleted = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)