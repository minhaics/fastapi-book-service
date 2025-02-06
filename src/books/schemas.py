from pydantic import BaseModel
from uuid import UUID
from datetime import date
from src.db.models import Review

class Book(BaseModel):
    uid: UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    
class BookWithReview(Book):
    reviews: list[Review]

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str

class BookCreateModel(BaseModel):
    """
    This class is used to validate the request when creating or updating a book
    """
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
