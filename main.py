from fastapi import FastAPI, APIRouter
from login import authentication_router
from user import user_router

app=FastAPI()

app.include_router(authentication_router)
app.include_router(user_router)

@app.get('/')
def helth_check():
    return{'Message':'Hello World'}