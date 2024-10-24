from datetime import timedelta, datetime, timezone

import asyncpg
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from config import JWT_SECRET
from src.main import app
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.database.database import get_async_session, Base
from config import TEST_DB_HOST, TEST_DB_NAME, TEST_DB_PASS, TEST_DB_PORT, TEST_DB_USER
from typing import AsyncGenerator

# Database setup
DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
Base.metadata.bind = async_engine

# Override the session dependency

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

async def mock_jwt_token():
    token_data = {
        "sub": "1",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

async def create_test_db_if_not_exists():
    """Create the test database (users_test) if it doesn't exist."""
    try:
        # Connect to the default 'postgres' database
        conn = await asyncpg.connect(
            user=TEST_DB_USER, password=TEST_DB_PASS, database="postgres", host=TEST_DB_HOST, port=TEST_DB_PORT
        )

        # Check if the test database exists
        result = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")

        if not result:
            # Database doesn't exist, create it
            print(f"Database '{TEST_DB_NAME}' does not exist, creating...")
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
            print(f"Database '{TEST_DB_NAME}' created successfully.")
        else:
            print(f"Database '{TEST_DB_NAME}' already exists.")

        await conn.close()
    except Exception as e:
        print(f"Error while checking/creating test database: {e}")


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created!")


async def drop_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Tables dropped!")


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await create_test_db_if_not_exists()
    await create_tables()
    yield
    await drop_tables()


# Test for creating a vacancy
async def test_create_vacancy():
    new_vacancy_data = {
        "title": "Software Engineer",
        "salary": "100000 USD",
        "description": "Develops software solutions."
    }

    token = await mock_jwt_token()

    headers = {
        "usersAuth": f"{token}"
    }

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/v1/vacancies/", json=new_vacancy_data, headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        assert "id" in response.json()
        assert "user_id" in response.json()

# Test for getting the count of vacancies
async def test_get_count_vacancies():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/v1/vacancies/count")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        assert "count" in response.json()