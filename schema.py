from pydantic import BaseModel

class CreateNewUser(BaseModel):
    password: str
    role: str

    class Config:
        extra = "forbid"