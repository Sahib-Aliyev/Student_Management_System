from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from models import *
from utility import *

secret_key = "7ff9b67b4b584ab0be8422b0fc5ff279dfc2011ef424655bee89401a9b6f6a04"

o2auth = OAuth2PasswordBearer(tokenUrl="token")


def authenticate(username: str, password: str, db: Session):
    user_in_db = db.query(User).filter(User.username == username).first()
    if not user_in_db:
        return False
    hash_password = user_in_db.password
    if not verifyPassword(hash_password, password):
        return False
    return user_in_db


def create_accsess_token(data, expire_time=None):
    to_encode = data.copy()
    if expire_time:
        expire = datetime.now() + expire_time
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encodded_token = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encodded_token


def get_current_user(token=Depends(o2auth)):
    try:
        payload = jwt.decode(token, secret_key, algorithms="HS256")
        username = payload["sub"]
        if not username:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return payload