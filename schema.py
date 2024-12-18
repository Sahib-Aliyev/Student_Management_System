from pydantic import BaseModel
from datetime import date

class CreateNewUser(BaseModel):
    password: str
    role: str

    class Config:
        extra = "forbid"

class CreateNewStudent(BaseModel):
    name : str
    surname : str
    fin : str
    birth_date : date
