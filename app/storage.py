from app.models import Book, BookIn

_books: dict[int, Book] = {}
_next_id = 1


def add(data: BookIn) -> Book:
    global _next_id
    book = Book(id=_next_id, **data.model_dump())
    _books[book.id] = book
    _next_id += 1
    return book


def list_all() -> list[Book]:
    return list(_books.values())


def get(book_id: int) -> Book | None:
    return _books.get(book_id)


def replace(book_id: int, data: BookIn) -> Book | None:
    if book_id not in _books:
        return None
    book = Book(id=book_id, **data.model_dump())
    _books[book_id] = book
    return book


def delete(book_id: int) -> bool:
    return _books.pop(book_id, None) is not None


def clear() -> None:
    """Empty the storage. For tests only."""
    global _next_id
    _books.clear()
    _next_id = 1
