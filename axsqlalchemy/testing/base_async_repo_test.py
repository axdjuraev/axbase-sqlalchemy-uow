from abc import ABC
from typing import Union, Type, Any
from functools import wraps
from axabc.test import BaseAsyncTest
from axsqlalchemy.settings import Settings
from axsqlalchemy.utils.creation import create_models
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class BaseAsyncRepoTest(BaseAsyncTest, ABC):
    __is_dbsetup = False
    SettingsClass: Union[Type[Settings], None] = None
    DBBase: Any = None

    @classmethod
    def setup_class(cls):
        if cls.SettingsClass is None:
            raise NotImplementedError("SettingsClass is not implemented")
        settings = cls.SettingsClass()
        cls.engine = create_async_engine(settings.db_connection_string)
        cls.session_maker = sessionmaker(
            cls.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @staticmethod
    def setupdb(f):
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            if self.DBBase is None:
                raise NotImplementedError("DBBase is not implemented")
            if not self.__is_dbsetup:
                await create_models(self.engine, self.DBBase)
            return await f(self, *args, **kwargs)

        return wrapper


def with_session(f):
    @wraps(f)
    @BaseAsyncRepoTest.setupdb
    async def wrapper(self: BaseAsyncRepoTest, *args, **kwargs):
        async with self.session_maker() as session:
            async with session.begin():
                return await f(self, *args, session=session, **kwargs)

    return wrapper
