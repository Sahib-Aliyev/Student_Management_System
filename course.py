from fastapi import APIRouter,Depends
from jwt import get_current_user
from sqlalchemy.orm import Session
from db import get_db
from schema import *
from course_service import *

course_router=APIRouter(tags=['Course'])

@course_router.get('/course')
def get_all_subjects(db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    message=get_all_subjects_from_db(current_user=current_user,db=db)
    return message