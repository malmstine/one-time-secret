from typing import Optional
from pydantic import BaseModel


class CipherSecretSchema(BaseModel):
    password: Optional[str] = None


class SecretSchema(BaseModel):
    secret: str
    password: Optional[str]


class SecretKeyResponse(BaseModel):
    secret_key: str


class SecretTextResponse(BaseModel):
    secret: str
