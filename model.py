import re
from abc import ABC
from typing import Any, List, Union

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AbstractBaseModel(ABC, Base):
    _ids: Union[List[Any], None] = None
    __tablename: Union[str, None] = None

    @classmethod
    @property
    def __tablename__(cls):
        if not cls.__tablename:
            _name = cls.__name__
            cls.__tablename = re.sub(r"(?<!^)(?=[A-Z])", "_", _name).lower()

        return cls.__tablename

    @classmethod
    @property
    def ids(cls) -> Union[List[Any], None]:
        if cls._ids is None:
            cls._ids = None

        return cls._ids


class BaseTableAt(AbstractBaseModel):
    __abstract__ = True

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())
