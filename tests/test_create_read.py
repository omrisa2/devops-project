BOOK = {"title": "Dune", "author": "Frank Herbert", "year": 1965}


def test_create_book(client):
    response = client.post("/books", json=BOOK)
    assert response.status_code == 201
    assert response.headers["Location"] == "/books/1"
    assert response.json() == {"id": 1, **BOOK, "read": False}


def test_create_book_with_invalid_field_returns_422(client):
    response = client.post("/books", json={"title": "", "author": "Frank Herbert"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_book_with_body_not_json_returns_422(client):
    response = client.post(
        "/books",
        content="this is not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_list_books_when_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []


def test_list_books_oldest_first(client):
    client.post("/books", json=BOOK)
    client.post(
        "/books",
        json={"title": "Emma", "author": "Jane Austen", "year": 1815, "read": True},
    )
    response = client.get("/books")
    assert response.status_code == 200
    assert [book["title"] for book in response.json()] == ["Dune", "Emma"]


def test_read_book(client):
    client.post("/books", json=BOOK)
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **BOOK, "read": False}


def test_read_missing_book_returns_404(client):
    response = client.get("/books/7")
    assert response.status_code == 404
    assert response.json() == {"detail": "no book with id 7"}
