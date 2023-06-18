import dataclasses
import datetime
import hashlib
import logging

from Crypto.Cipher import AES
from typing import Optional, Callable
from fastapi import HTTPException
from fastapi.requests import Request

from server import settings

logger = logging.getLogger()


class AESPassword:

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value: bytes):
        if not value:
            raise ValueError("Value must be not empty")
        value = hashlib.md5(value).digest()
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Secret:

    _base_password: Optional[str] = settings.SECRET_KEY
    _nonce: str = settings.NONCE
    password = AESPassword()

    class WrongPassword(Exception):
        pass

    def __init__(self, *, password=None):
        self.password = (password or self._base_password).encode()

    @property
    def cipher(self):
        return AES.new(self.password,
                       AES.MODE_EAX,
                       nonce=self._nonce.encode())

    def encrypt(self, secret_text: str):
        return self.cipher.encrypt_and_digest(secret_text.encode())

    def decrypt(self, cipher_secret: bytes, tag: bytes, *, raise_exception=False) -> str | None:
        cipher = self.cipher
        try:
            secret = cipher.decrypt(cipher_secret)
            cipher.verify(tag)
        except ValueError as ex:
            if raise_exception:
                raise self.WrongPassword("Password wrong") from ex
            return None
        return secret.decode()


@dataclasses.dataclass
class RequestRate:
    date: datetime.datetime
    rate: float


class RateError(Exception):
    pass


def new_rate(*, request_rate: RequestRate | None,
             limit: int,
             per: int,
             next_date=None) -> RequestRate:
    """
    For two time intervals, calculates the average number of requests per second
    :param request_rate: object with last request data
    :param limit: limit request to per
    :param per: in sec
    :return: request rate limiter
    :param next_date: date current request
    """
    now = datetime.datetime.now() if not next_date else next_date
    if not request_rate:
        return RequestRate(rate=.0, date=now)

    critical = limit
    up_delta = 1.
    down_delta = limit / per

    prev_date = request_rate.date + datetime.timedelta(seconds=down_delta)

    rate = request_rate.rate
    if prev_date < now:
        time_delta = now - prev_date
        rate = max(request_rate.rate - (time_delta.seconds * down_delta), 0)

    if rate > critical:
        raise RateError

    return RequestRate(rate=rate + up_delta, date=now)


class BaseBackend:

    async def set(self, name, request_rate: RequestRate):
        raise NotImplemented

    async def get(self, name) -> RequestRate:
        raise NotImplemented


class SimpleBackend(BaseBackend):
    """
    Backend for storage data for rate request limiter
    """
    def __init__(self):
        self.storage = dict()

    async def set(self, name, request_rate: RequestRate):
        self.storage[name] = request_rate

    async def get(self, name) -> RequestRate:
        return self.storage.get(name)


def create_limiter(*,
                   limit: int,
                   per: int,
                   backend: BaseBackend,
                   determinant: Callable) -> Callable:

    """
    Allows you to limit the number of requests at a given time
    :param limit: limit request to per
    :param per: in sec
    :param backend: to storage
    :param determinant:
    :return: request rate limiter
    """

    async def limiter(request: Request):
        client_inst = determinant(request)
        last_request = await backend.get(client_inst)
        try:
            new_request = new_rate(request_rate=last_request, limit=limit, per=per)
        except RateError:
            raise HTTPException(status_code=429)
        await backend.set(client_inst, new_request)

    return limiter
