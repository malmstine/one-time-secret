import datetime
import pytest

from server.utils import SimpleBackend, RequestRate, new_rate, RateError


@pytest.mark.asyncio
async def test_simple_backend():
    simple_backend = SimpleBackend()
    data = RequestRate(date=datetime.datetime(2020, 10, 10), rate=0)
    await simple_backend.set("data", data)
    store_data = await simple_backend.get("data")
    assert store_data == data, (store_data, data)


@pytest.mark.asyncio
async def test_simple_backend_get_none(session):
    simple_backend = SimpleBackend()
    store_data = await simple_backend.get("data")
    assert store_data is None, store_data


@pytest.mark.asyncio
async def test_new_rate(session):
    new_request_data = new_rate(request_rate=None, limit=10, per=10)
    assert new_request_data


@pytest.mark.asyncio
async def test_create_new_rate(session):
    date = datetime.datetime(2020, 10, 10)
    data = RequestRate(date=date, rate=0)
    new_request_data = new_rate(request_rate=data, limit=10, per=10, next_date=date + datetime.timedelta(seconds=10))
    assert new_request_data != data


@pytest.mark.asyncio
async def test_create_new_rate(session):
    date = datetime.datetime(2020, 1, 10)
    data = RequestRate(date=date, rate=0)
    limit = 2
    per = 100
    excepted = False
    try:
        for _ in range(limit + 2):
            data = new_rate(request_rate=data, limit=limit, per=per, next_date=date + datetime.timedelta(seconds=10))
            print(data.rate)
    except RateError:
        excepted = True
    assert excepted
