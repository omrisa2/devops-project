import pytest

BOOK = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
MISSING_ID = 999999


def create_book(api):
    response = api.post("/books", json=BOOK)
    assert response.status_code == 201
    return response.json()


def test_healthz(api):
    response = api.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_book(api):
    response = api.post("/books", json=BOOK)
    assert response.status_code == 201
    book = response.json()
    assert book == {"id": book["id"], **BOOK, "read": False}
    assert response.headers["Location"] == f"/books/{book['id']}"


def test_list_books_includes_created_book(api):
    book = create_book(api)
    response = api.get("/books")
    assert response.status_code == 200
    assert book in response.json()


def test_read_book(api):
    book = create_book(api)
    response = api.get(f"/books/{book['id']}")
    assert response.status_code == 200
    assert response.json() == book


def test_replace_book(api):
    book = create_book(api)
    changed = {**BOOK, "read": True}
    response = api.put(f"/books/{book['id']}", json=changed)
    assert response.status_code == 200
    assert response.json() == {"id": book["id"], **changed}
    assert api.get(f"/books/{book['id']}").json() == {"id": book["id"], **changed}


def test_delete_book(api):
    book = create_book(api)
    response = api.delete(f"/books/{book['id']}")
    assert response.status_code == 204
    assert api.get(f"/books/{book['id']}").status_code == 404


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_missing_book_returns_404(api, method):
    body = BOOK if method == "PUT" else None
    response = api.request(method, f"/books/{MISSING_ID}", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": f"book {MISSING_ID} was not found"}


def test_wrong_type_returns_422(api):
    response = api.post("/books", json={**BOOK, "year": "1965"})
    assert response.status_code == 422
