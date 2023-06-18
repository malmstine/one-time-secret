import uuid
import typing as t
from fastapi import Depends, Request, FastAPI
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from server.depends import get_session
from server.domains import get_secret_or_none, get_secret, add_secret
from server.schemas import (
    SecretSchema, CipherSecretSchema,
    SecretKeyResponse, SecretTextResponse
)
from server.utils import Secret, create_limiter, SimpleBackend


app = FastAPI()


def get_host(request: Request) -> t.Hashable:
    return "limit_" + request.headers["host"]


limiter = create_limiter(limit=5, per=60, backend=SimpleBackend(), determinant=get_host)


@app.post("/generate", dependencies=[Depends(limiter)], response_model=SecretKeyResponse)
async def generate_secret(secret: SecretSchema,
                          session: AsyncSession = Depends(get_session)):

    """
    take secret and passphrase and returns secret_key that can be used to get the secret
    """
    secret_key = await add_secret(session=session,
                                  secret_text=secret.secret,
                                  password=secret.password)
    return dict(secret_key=secret_key.hex)


@app.post("/secrets/{secret_key}", dependencies=[Depends(limiter)], response_model=SecretTextResponse)
async def get_secrete(secret_key: str,
                      secret_data: CipherSecretSchema = CipherSecretSchema(),
                      session: AsyncSession = Depends(get_session)):
    """
    accepts a passphrase as input and returns a secret
    """
    secret_key = uuid.UUID(hex=secret_key, version=4)
    cipher_secret = await get_secret_or_none(session=session,
                                             secret_key=secret_key)
    if not cipher_secret:
        return Response("Not Found", status_code=404)

    if cipher_secret.use_user_password and not secret_data.password:
        return Response("Password Required", status_code=400)

    password = secret_data.password if cipher_secret.use_user_password else None

    try:
        secret = get_secret(cipher_secret=cipher_secret,
                            password=password)
    except Secret.WrongPassword:
        return Response("Wrong Password", status_code=403)

    await cipher_secret.fire()
    return JSONResponse(dict(secret=secret),
                        status_code=200)
