from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jwt import create_accsess_token, authenticate
from sqlalchemy.orm import Session
from db import get_db
from exception import UserNotFoundException

authentication_router = APIRouter(tags=["Authentication"])


@authentication_router.post("/token")
def login_for_accsess_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_deleted == True:
        raise UserNotFoundException()

    if user.is_deleted == False:
        accsess_token = create_accsess_token(data={"sub": user.username})
        return {"access_token": accsess_token, "token_type": "bearer"}