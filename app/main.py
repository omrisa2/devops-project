from fastapi import FastAPI, Response, status

from app import storage
from app.models import Book, BookIn

app = FastAPI(title="Reading List API")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(data: BookIn, response: Response) -> Book:
    book = storage.add(data)
    response.headers["Location"] = f"/books/{book.id}"
    return book
