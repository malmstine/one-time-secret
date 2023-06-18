import dataclasses
from sqlalchemy import column
from sqlalchemy.ext.asyncio import AsyncSession

from server.models import secret_table, SecretKey
from server.utils import Secret


@dataclasses.dataclass(frozen=True, kw_only=True)
class CipherSecret:
    secret: bytes
    tag: bytes
    use_user_password: bool
    session: AsyncSession

    async def fire(self):
        await self.session.commit()


async def get_secret_or_none(*, session: AsyncSession, secret_key: SecretKey) -> CipherSecret | None:
    """
    Returns the encrypted secret, or None if none exists
    """
    result = await session.execute(secret_table.delete()
                                               .where(column("secret_key") == secret_key)
                                               .returning(secret_table.c.secret,
                                                          secret_table.c.tag,
                                                          secret_table.c.use_user_password))
    try:
        [cipher_secret, tag, use_user_password] = result.fetchone()
    except TypeError:
        return None

    return CipherSecret(secret=cipher_secret,
                        tag=tag,
                        use_user_password=use_user_password,
                        session=session)


def get_secret(*, cipher_secret: CipherSecret, password: str = None) -> str:
    """
    Decrypts the stored secret
    """
    cipher = Secret(password=password)
    return cipher.decrypt(cipher_secret.secret,
                          cipher_secret.tag,
                          raise_exception=True)


async def add_secret(*, session: AsyncSession,
                     secret_text: str,
                     password: str = None) -> SecretKey:
    """
    Keeps a secret. Doesn't save password. If there is no password, the default password is used
    """
    cipher = Secret(password=password)
    cipher_secret, tag = cipher.encrypt(secret_text)
    use_user_password = bool(password)
    result = await session.execute(secret_table.insert()
                                               .values(secret=cipher_secret,
                                                       tag=tag,
                                                       use_user_password=use_user_password)
                                               .returning(column("secret_key")))

    [secret_key] = result.fetchone()
    await session.commit()
    return secret_key
