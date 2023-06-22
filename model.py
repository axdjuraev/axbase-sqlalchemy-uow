import re
from abc import ABC
from typing import Any, List, Union

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Meta(ABC, type(Base)):
    ...


class AbstractBaseModel(Base, metaclass=Meta):
    __abstract__ = True

    _ids: Union[List[Any], None] = None
    _ids_all: Union[List[Any], None] = None
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
    def ids(cls) -> Union[List[Any], tuple[Any], None]:
        if cls._ids is None:
            cls._ids = []

            for constraint in cls.__table__.constraints:
                if type(constraint) is sa.PrimaryKeyConstraint:
                    for column in constraint.columns:
                        cls._ids.append(column)

        return cls._ids

    @classmethod
    @property
    def ids_all(cls) -> Union[List[Any], tuple[Any], None]:
        return cls._ids_all


class BaseTableAt(AbstractBaseModel):
    __abstract__ = True

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())
