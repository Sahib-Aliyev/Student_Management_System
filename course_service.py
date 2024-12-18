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
    subjects_lst = [{course.name: course.description} for course in courses_in_db]
    return subjects_lst

