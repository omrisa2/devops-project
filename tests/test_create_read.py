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
