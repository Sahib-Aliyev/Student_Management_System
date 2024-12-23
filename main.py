from fastapi import FastAPI, APIRouter
from login import authentication_router
from user import user_router
from students import student_router
from course import course_router
from grade import grade_router

app = FastAPI()

app.include_router(authentication_router)
app.include_router(user_router)
app.include_router(student_router)
app.include_router(course_router)
app.include_router(grade_router)


@app.get("/")
def helth_check():
    return {"Message": "Hello World"}