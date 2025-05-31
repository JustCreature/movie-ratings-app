
import pytest_asyncio
from fastapi.testclient import TestClient

from app.main import create_app


@pytest_asyncio.fixture(autouse=False)
async def test_client():
    app = create_app()
    return TestClient(app)
