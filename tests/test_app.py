import uuid
import pytest

from tests.test_domains import get_secret_or_none


secret_request_data = dict(secret="red panda attacks")
secret_request_data_with_pass = dict(secret="red panda attacks", password="strong_password")


async def generate_request(async_client, with_password=False):
    data = secret_request_data_with_pass if with_password else secret_request_data
    response = await async_client.post("/generate", json=data)
    return data, response


@pytest.mark.asyncio
async def test_429_response(async_client, override_1_per_1s_limiter):

    response_codes = set()
    for _ in range(10):
        response = await async_client.post("/generate", json=dict(secret="red panda attacks"))
        response_codes.add(response.status_code)

    assert 429 in response_codes, response_codes


@pytest.mark.asyncio
async def test_generate(session):
    secret_key = uuid.uuid4()
    c = await get_secret_or_none(session=session, secret_key=secret_key)
    assert c is None


@pytest.mark.asyncio
async def test_base_case_without_password(async_client):
    request_data, response = await generate_request(async_client)
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key)
    assert response.status_code == 200, response.text
    response_text = response.json()["secret"]
    assert response_text == request_data["secret"], f"response {response_text}"


@pytest.mark.asyncio
async def test_base_case_with_password(async_client):
    request_data, response = await generate_request(async_client, True)
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key,
                                       json=dict(password=request_data["password"]))
    assert response.status_code == 200, response.text
    response_text = response.json()["secret"]
    assert response_text == request_data["secret"]


@pytest.mark.asyncio
async def test_with_wrong_password(async_client):
    wrong_password = "another_password"
    request_data, response = await generate_request(async_client, True)
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key, json=dict(password=wrong_password))
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_base_case_double_request_secret(async_client):
    request_data, response = await generate_request(async_client, True)
    password = request_data["password"]
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key, json=dict(password=password))
    assert response.status_code == 200, response.text
    response_text = response.json()["secret"]
    assert response_text == request_data["secret"]
    response = await async_client.post("/secrets/" + secret_key, json=dict(password=password))
    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_base_case_with_password(async_client):
    secret_text = "red panda attacks"
    password = "strong_password"
    wrong_password = "another_password"
    response = await async_client.post("/generate", json=dict(secret=secret_text, password=password))
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key, json=dict(password=wrong_password))
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_base_case_with_passed_password(async_client, app):
    request_data, response = await generate_request(async_client, True)
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key)
    assert response.status_code == 400, response.text


@pytest.mark.asyncio
async def test_base_case_with_not_required_optional_password(async_client):
    request_data, response = await generate_request(async_client)
    assert response.status_code == 200, response.text
    secret_key = response.json()["secret_key"]
    response = await async_client.post("/secrets/" + secret_key, json=dict(password="password"))
    assert response.status_code == 200, response.text
