from os import environ
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


DB_USER = environ.get("DB_USER", "secret")
DB_PASS = environ.get("DB_PASS", "secret")
DB_PORT = environ.get("DB_PORT", "5432")
DB_HOST = environ.get("DB_HOST", "127.0.0.1")
DB_NAME = environ.get("DB_NAME", "secret")


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL, echo=True)


def create_session_marker(engine_):
    return sessionmaker(
        engine_, class_=AsyncSession, expire_on_commit=False
    )


async_session = create_session_marker(engine)
