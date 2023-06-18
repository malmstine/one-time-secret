import asyncio
import pytest as pytest

from os import environ
from httpx import AsyncClient, URL
from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from server.depends import get_session
from server.main import app as app_main, limiter, get_host
from server.models import metadata
from server.utils import create_limiter, SimpleBackend


DB_USER = environ.get("DB_TEST_USER", "secret")
DB_PASS = environ.get("DB_TEST_PASS", "secret")
DB_PORT = environ.get("DB_TEST_PORT", "5432")
DB_HOST = environ.get("DB_TEST_HOST", "127.0.0.1")
DB_NAME = environ.get("DB_TEST_NAME", "test_secret")


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine_():
    database_url = DATABASE_URL
    engine = create_async_engine(database_url)
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture()
async def create_(engine_):
    async with engine_.begin() as conn:
        await conn.execute(text('create extension if not exists "uuid-ossp"'))
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture
async def session(engine_, create_):
    async with AsyncSession(engine_) as session:
        yield session


@pytest.fixture(scope="session")
def app():
    yield app_main


@pytest.fixture()
async def override_session(engine_, app):

    async def get_session_override_():
        async with AsyncSession(engine_) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_override_


@pytest.fixture()
async def override_limiter(engine_, app):
    async def empty_limiter(request: Request):
        return request
    app.dependency_overrides[limiter] = empty_limiter


@pytest.fixture()
async def override_1_per_1s_limiter(engine_, app):
    app.dependency_overrides[limiter] = create_limiter(limit=1, per=1,
                                                       backend=SimpleBackend(),
                                                       determinant=get_host)


@pytest.fixture
async def async_client(app, override_session, override_limiter, create_):
    async with AsyncClient(app=app, base_url=URL('http://testserver')) as test_client:
        yield test_client
