from datetime import timedelta, datetime

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from config import JWT_SECRET
from src.main import app
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.database.database import get_async_session, Base
from config import TEST_DB_HOST, TEST_DB_NAME, TEST_DB_PASS, TEST_DB_PORT, TEST_DB_USER
from typing import AsyncGenerator

DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

test_async_engine = create_async_engine(DATABASE_URL, echo=True)
test_async_session_maker = async_sessionmaker(test_async_engine, expire_on_commit=False)

Base.metadata.bind = test_async_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture
async def mock_jwt_token():
    token_data = {
        "sub": "test_user",
        "exp": datetime.now() + timedelta(days=1)
    }
    return jwt.encode(token_data, JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope='module', autouse=True)
async def setup_database():
    async with test_async_engine.begin() as conn:
        print("Tables are creating...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created!")

    yield

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio(loop_scope='module')
async def test_create_vacancy():
    new_vacancy_data = {
        "title": "Software Engineer",
        "salary": "100000 USD",
        "description": "Develops software solutions."
    }

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/v1/vacancies/", json=new_vacancy_data)
        assert response.status_code == 200
        assert "id" in response.json()


@pytest.mark.asyncio(loop_scope='module')
async def test_get_count_vacancies():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/v1/vacancies/count")
        assert response.status_code == 200
        assert "count" in response.json()
