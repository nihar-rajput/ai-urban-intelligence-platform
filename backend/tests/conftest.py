import pytest
from backend.app.db.session import init_db


@pytest.fixture(autouse=True)
async def setup_database():
    """Ensure database tables are created before running tests."""
    await init_db()
    yield
