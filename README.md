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

## Run the tests and the checks

    pytest --cov            # the unit tests; fails below 75% coverage
    ruff check .            # lint
    ruff format --check .   # formatting
    mypy                    # types

The settings are in `pyproject.toml`. The same checks run on every push
(`branch.yml`) and on every pull request (`pr.yml`), on Python 3.13 and 3.14.

To run them before each commit, once after cloning:

    pre-commit install

From then on, a failing check stops `git commit`.

## Run the integration tests

The tests in `integration/` call a running app over HTTP, with PostgreSQL behind it.
Plain `pytest` does not collect them. To run them locally:

    docker build -t devops-project:pr .
    docker run -d --name it-db -e POSTGRES_USER=books -e POSTGRES_PASSWORD=local \
        -e POSTGRES_DB=books -p 5432:5432 postgres:18
    until docker exec it-db pg_isready -U books; do sleep 1; done
    docker run -d --name it-app --network host \
        -e DATABASE_URL=postgresql://books:local@localhost:5432/books devops-project:pr
    pytest integration -v
    docker rm -f it-app it-db

`BASE_URL` points the tests at another address (default `http://localhost:8000`).
On a pull request, `integration-tests` runs them against the image from `image-build`.

## The pipeline

| Workflow    | Runs on                          | Jobs                                                     |
|-------------|----------------------------------|----------------------------------------------------------|
| `branch.yml`| a push to any branch but `main`  | lint, unit-tests                                         |
| `pr.yml`    | a pull request to `main`         | lint, unit-tests → image-build → integration-tests, security |
| `merge.yml` | a merge into `main`              | image-push → deploy → smoke-test                         |

`main` is protected: every change reaches it through a pull request with an approval,
and the pull request checks (lint, unit-tests, image-build, integration-tests) must pass.
