import os

import httpx2
import pytest

# The address of a running app. The pipeline and a local run both start it on port 8000.
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.fixture
def api():
    with httpx2.Client(base_url=BASE_URL, timeout=10) as client:
        yield client
