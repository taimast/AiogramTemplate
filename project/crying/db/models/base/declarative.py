from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .mixin import BaseQuery


# todo L1 TODO 18.04.2023 17:00 taima: Use func from sqlalchemy_utils. get_tables is not used


class Base(AsyncAttrs, DeclarativeBase, BaseQuery):
    id: Mapped[int] = mapped_column(primary_key=True)
    type_annotation_map = {
        str: String(255),
    }
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
