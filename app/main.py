from fastapi import FastAPI, HTTPException, Response, status

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


@app.get("/books")
async def list_books() -> list[Book]:
    return storage.list_all()


@app.get("/books/{book_id}")
async def read_book(book_id: int) -> Book:
    book = storage.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return book


@app.put("/books/{book_id}")
async def replace_book(book_id: int, data: BookIn) -> Book:
    book = storage.replace(book_id, data)
    if book is None:
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int) -> Response:
    if not storage.delete(book_id):
        raise HTTPException(status_code=404, detail=f"no book with id {book_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
