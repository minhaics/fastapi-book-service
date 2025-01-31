from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import initdb
from src.auth.routes import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initdb()
    yield
    print("server is stopping")
    
version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """
    
version_prefix = f"/api/{version}"

app = FastAPI(
    lifespan = lifespan,
    description= description
    )
# add the lifespan event to our application
app.include_router(book_router, 
                   prefix=f"{version_prefix}/books", 
                   tags=["books"]
                   )

app.include_router(
    auth_router,
    prefix= f"{version_prefix}/auth", 
    tags= ["auth"]  
)
