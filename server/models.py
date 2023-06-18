import uuid

import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID

metadata = sqlalchemy.MetaData()


secret_table = sqlalchemy.Table(
    "secret",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column("secret_key",
                      UUID(as_uuid=True),
                      server_default=sqlalchemy.text("uuid_generate_v4()"),
                      unique=True,
                      nullable=False,
                      index=True),
    sqlalchemy.Column("secret", sqlalchemy.LargeBinary()),
    sqlalchemy.Column("tag", sqlalchemy.LargeBinary()),
    sqlalchemy.Column("use_user_password", sqlalchemy.Boolean()),
)

SecretKey = type(uuid.UUID)
