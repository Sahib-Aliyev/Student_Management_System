from sqlalchemy import desc
from sqlalchemy.orm import Session
from schema import *
from db import get_db
from models import *
from exception import *
from utility import *
from jwt import get_current_user
from fastapi import Depends

def create_new_user_in_db(*,username, data: CreateNewUser, db: Session):
    user_in_db = db.query(User).filter(User.username == username).first()
    if user_in_db:
        raise UserAlreadyExist()
    hash_password = hashPassword(data.password)
    new_user = User(username=username, password=hash_password,role=data.role,is_deleted=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "user has been created"}

def delete_user_from_db(*,username, db: Session ,current_user: User= Depends(get_current_user)):
    current_user_in_db =db.query(User).filter(User.username==current_user.username).first()
    if current_user_in_db.role!= 'admin':
        raise HTTPException(status_code=401, detail="Only admins can delete")
    user_to_delete = db.query(User).filter(User.username == username).first() 
    if not user_to_delete or user_to_delete.is_deleted==True:
        raise UserNotFoundException()
    user_to_delete.is_deleted = True
    db.commit()

    return {"message": f"User {username} has been deleted successfully."}
