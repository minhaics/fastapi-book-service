from typing import List
from pydantic import BaseModel
from sqlmodel import Field
from src.db.models import Book, Review

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class UserResponseModel(BaseModel):
    message: str
    user: UserCreateModel  

class UserModel(BaseModel):
    first_name: str= Field(max_length=25)
    last_name: str= Field(max_length=25)
    username: str= Field(max_length=8)
    email: str= Field(max_length=40)

class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[Review] 

# inside src/auth/routes.py
class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class EmailModel(BaseModel):
    addresses: List[str]

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
