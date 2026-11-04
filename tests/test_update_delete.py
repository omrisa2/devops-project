BOOK = {"title": "Dune", "author": "Frank Herbert", "year": 1965}


def test_replace_book(client):
    client.post("/books", json=BOOK)
    response = client.put("/books/1", json={**BOOK, "read": True})
    assert response.status_code == 200
    assert response.json() == {"id": 1, **BOOK, "read": True}
    assert client.get("/books/1").json() == {"id": 1, **BOOK, "read": True}


def test_replace_book_resets_missing_optional_fields(client):
    client.post("/books", json={**BOOK, "read": True})
    response = client.put("/books/1", json={"title": "Dune", "author": "Frank Herbert"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Dune",
        "author": "Frank Herbert",
        "year": None,
        "read": False,
    }


def test_replace_book_ignores_id_in_body(client):
    client.post("/books", json=BOOK)
    response = client.put("/books/1", json={**BOOK, "id": 99})
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_replace_missing_book_returns_404(client):
    response = client.put("/books/7", json=BOOK)
    assert response.status_code == 404
    assert response.json() == {"detail": "no book with id 7"}


def test_replace_book_with_wrong_type_returns_422(client):
    client.post("/books", json=BOOK)
    response = client.put("/books/1", json={**BOOK, "year": "1965"})
    assert response.status_code == 422


def test_delete_book(client):
    client.post("/books", json=BOOK)
    response = client.delete("/books/1")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/books/1").status_code == 404


def test_delete_missing_book_returns_404(client):
    response = client.delete("/books/7")
    assert response.status_code == 404
    assert response.json() == {"detail": "no book with id 7"}


def test_deleted_id_is_never_reused(client):
    client.post("/books", json=BOOK)
    client.post("/books", json=BOOK)
    client.delete("/books/2")
    response = client.post("/books", json=BOOK)
    assert response.json()["id"] == 3
