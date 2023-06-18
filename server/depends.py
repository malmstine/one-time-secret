from sqlalchemy.ext.asyncio import AsyncSession

from server.db import async_session


async def get_session() -> AsyncSession:
    """
    Return async session to pg connect
    :return: async pg session
    """
    async with async_session() as session:
        yield session


