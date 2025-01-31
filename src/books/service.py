from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.models import Book
from src.books.schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from datetime import datetime
from uuid import UUID

class BookService:
    """
    This class provides methods to create, read, update, and delete books
    """
    async def get_all_books(self, session: AsyncSession) -> list[Book]:
        """
        Get a list of all books
        returns:
           list: list of books
        """
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def create_book(self, book_data: BookCreateModel, session: AsyncSession) -> Book:
        """
        Create a new book
        Args:
            book_data (BookCreateModel): data to create a new
        Returns:
            Book: the new book
        """
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d"
        ).strftime("%Y-%m-%d")
        
        session.add(new_book)
        await session.commit()
        return new_book

    async def get_book(self, book_uid: str, session: AsyncSession)-> Optional[Book]:
        """Get a book by its UUID.
        Args:
            book_uid (str): the UUID of the book
        Returns:
            Book: the book object
        """
        statement = select(Book).where(Book.uid == UUID(book_uid))
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        """Update a book
        Args:
            book_uid (str): the UUID of the book
            update_data (BookCreateModel): the data to update the book
        Returns:
            Book: the updated book
        """
        book_to_update = await self.get_book(book_uid, session)
        if book_to_update is not None:
            update_data_dict: dict = update_data.model_dump()
            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)
            await session.commit()
            return book_to_update
        else:
            return None
        
    async def delete_book(self, book_uid:str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return None
