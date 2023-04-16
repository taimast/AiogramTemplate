import datetime

from sqlalchemy import String, BigInteger
from sqlalchemy import func
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    # type_annotation_map = {
    #     str_30: String(30),
    #     str_50: String(50),
    #     num_12_4: Numeric(12, 4),
    #     num_6_2: Numeric(6, 2),
    # }
    # registry = registry(
    #     type_annotation_map={
    #         # str_30: String(30),
    #         # str_50: String(50),
    #         # num_12_4: Numeric(12, 4),
    #         # num_6_2: Numeric(6, 2),
    #         int: BigInteger,
    #     }
    # )
    pass


class AbstractUser(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    is_bot: Mapped[bool] = mapped_column(default=False)
    is_premium: Mapped[bool]


class TimestampMixin:
    created_at: Mapped[datetime.datetime | None] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
