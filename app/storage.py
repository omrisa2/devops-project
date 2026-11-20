"""Book storage.

If the DATABASE_URL environment variable is set, books are stored in PostgreSQL.
Otherwise they are kept in memory (the unit tests use this).
"""

import os

import psycopg
from psycopg.rows import DictRow, dict_row

from app.models import Book, BookIn


class MemoryStorage:
    """Books in a dict. Each process has its own copy."""

    def __init__(self) -> None:
        self._books: dict[int, Book] = {}
        self._next_id = 1

    def add(self, data: BookIn) -> Book:
        book = Book(id=self._next_id, **data.model_dump())
        self._books[book.id] = book
        self._next_id += 1
        return book

    def list_all(self) -> list[Book]:
        return list(self._books.values())

    def get(self, book_id: int) -> Book | None:
        return self._books.get(book_id)

    def replace(self, book_id: int, data: BookIn) -> Book | None:
        if book_id not in self._books:
            return None
        book = Book(id=book_id, **data.model_dump())
        self._books[book_id] = book
        return book

    def delete(self, book_id: int) -> bool:
        return self._books.pop(book_id, None) is not None

    def clear(self) -> None:
        self._books.clear()
        self._next_id = 1


CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS books (
    id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title  TEXT    NOT NULL,
    author TEXT    NOT NULL,
    year   INTEGER,
    read   BOOLEAN NOT NULL
)
"""


class PostgresStorage:
    """Books in a PostgreSQL table. Every process sees the same books."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._table_ready = False

    def _connect(self) -> psycopg.Connection[DictRow]:
        conn = psycopg.connect(self._url, row_factory=dict_row)
        if not self._table_ready:
            conn.execute(CREATE_TABLE)
            conn.commit()
            self._table_ready = True
        return conn

    def add(self, data: BookIn) -> Book:
        with self._connect() as conn:
            row = conn.execute(
                "INSERT INTO books (title, author, year, read) "
                "VALUES (%(title)s, %(author)s, %(year)s, %(read)s) RETURNING *",
                data.model_dump(),
            ).fetchone()
        assert row is not None
        return Book(**row)

    def list_all(self) -> list[Book]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM books ORDER BY id").fetchall()
        return [Book(**row) for row in rows]

    def get(self, book_id: int) -> Book | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE id = %s", (book_id,)
            ).fetchone()
        return Book(**row) if row else None

    def replace(self, book_id: int, data: BookIn) -> Book | None:
        with self._connect() as conn:
            row = conn.execute(
                "UPDATE books SET title = %(title)s, author = %(author)s, "
                "year = %(year)s, read = %(read)s WHERE id = %(id)s RETURNING *",
                {**data.model_dump(), "id": book_id},
            ).fetchone()
        return Book(**row) if row else None

    def delete(self, book_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM books WHERE id = %s", (book_id,))
        return cursor.rowcount == 1

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("TRUNCATE books RESTART IDENTITY")


def _make_storage() -> MemoryStorage | PostgresStorage:
    url = os.environ.get("DATABASE_URL")
    if url:
        return PostgresStorage(url)
    return MemoryStorage()


_storage = _make_storage()


def add(data: BookIn) -> Book:
    return _storage.add(data)


def list_all() -> list[Book]:
    return _storage.list_all()


def get(book_id: int) -> Book | None:
    return _storage.get(book_id)


def replace(book_id: int, data: BookIn) -> Book | None:
    return _storage.replace(book_id, data)


def delete(book_id: int) -> bool:
    return _storage.delete(book_id)


def clear() -> None:
    """Empty the storage. For tests only."""
    _storage.clear()
