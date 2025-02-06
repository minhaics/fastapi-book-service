# Inside src/db/main.py
from sqlmodel import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from src.config import Config
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession

# Sử dụng create_async_engine cho kết nối async
async_engine: AsyncEngine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True,  # Bật log để debug
    connect_args={},  # Đảm bảo không có tham số không hợp lệ được truyền vào
)

async def initdb():
    """create our database models in the database"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
                
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = sessionmaker(
        bind=async_engine, class_= AsyncSession, expire_on_commit=False
    )    
    async with Session() as session:
        yield session
