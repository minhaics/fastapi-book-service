from pydantic import BaseModel
from sqlmodel import Field

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class UserModel(BaseModel):
    first_name: str= Field(max_length=25)
    last_name: str= Field(max_length=25)
    username: str= Field(max_length=8)
    email: str= Field(max_length=40)
    
# inside src/auth/routes.py
class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
