# devops-project

A reading-list CRUD API in FastAPI, delivered by a CI/CD pipeline on GitHub Actions.
Built as the final project of a DevOps course, following the guidelines at
https://www.yuval.guide/project/devops-project/

## The API

One resource, the book: `id`, `title`, `author`, `year`, `read`.

| Method and path      | Does                |
|----------------------|---------------------|
| `POST /books`        | creates a book      |
| `GET /books`         | lists every book    |
| `GET /books/<id>`    | reads one book      |
| `PUT /books/<id>`    | replaces one book   |
| `DELETE /books/<id>` | deletes one book    |
| `GET /healthz`       | says the app is up  |

Storage is in memory for now.

## Run it locally

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt
    uvicorn app.main:app --reload

The interactive API docs are at http://127.0.0.1:8000/docs

## Run the tests

    pytest

## The pipeline

| Workflow    | Runs on                          | Jobs                                                     |
|-------------|----------------------------------|----------------------------------------------------------|
| `branch.yml`| a push to any branch but `main`  | lint, unit-tests                                         |
| `pr.yml`    | a pull request to `main`         | lint, unit-tests → image-build → integration-tests, security |
| `merge.yml` | a merge into `main`              | image-push → deploy → smoke-test                         |

`main` is protected: every change reaches it through a pull request with an approval.
