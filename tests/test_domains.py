import uuid

import pytest

from server.domains import add_secret, get_secret_or_none


@pytest.mark.asyncio
async def test_add_secret(session):
    secret_key = await add_secret(session=session, secret_text="secret")
    assert isinstance(secret_key, uuid.UUID)


@pytest.mark.asyncio
async def test_add_secret_with_password(session):
    secret_key = await add_secret(session=session, secret_text="secret")
    assert isinstance(secret_key, uuid.UUID)


@pytest.mark.asyncio
async def test_get_secret_or_none(session):
    secret_key = uuid.uuid4()
    secret = await get_secret_or_none(session=session, secret_key=secret_key)
    assert secret is None, secret
