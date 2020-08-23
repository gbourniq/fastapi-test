import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from veryneatapp.main import app


@pytest.fixture
def mock_client() -> FastAPI:
    client = TestClient(app)
    return client
