from abc import ABC
import re
from typing import Optional, Union, Type, Any
from functools import wraps
from axabc.test import BaseAsyncTest
from sqlalchemy import create_engine
from axsqlalchemy.repository import BaseRepository
from axsqlalchemy.settings import Settings
from axsqlalchemy.utils.creation import create_models
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class BaseAsyncRepoTest(BaseAsyncTest, ABC):
    _is_dbsetup = False
    SettingsClass: Union[Type[Settings], None] = None
    DBBase: Any = None
    TRepo: Optional[Type[BaseRepository]] = None
    repo: Optional[BaseRepository] = None
    session: AsyncSession

    @staticmethod
    def async2sync_url(url: str) -> str:
        return re.sub(r'(\w+)[+]\w+', r'\1', url)

    @classmethod
    def setup_class(cls):
        if cls.SettingsClass is None:
            raise NotImplementedError("SettingsClass is not implemented")
        settings = cls.SettingsClass()  # type: ignore
        sync_settings = cls.SettingsClass()  # type: ignore
        sync_settings.DB_DRIVERNAME = cls.async2sync_url(sync_settings.DB_DRIVERNAME)

        cls.engine = create_async_engine(settings.db_connection_string)
        cls.session_maker = sessionmaker(
            cls.engine,  # type: ignore
            class_=AsyncSession,
            expire_on_commit=False,
        )
        cls.sync_engine = create_engine(sync_settings.db_connection_string)
        cls.DBBase.metadata.create_all(cls.sync_engine)

    @staticmethod
    def setupdb(f):
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            if self.DBBase is None:
                raise NotImplementedError("DBBase is not implemented")
            if not self._is_dbsetup:
                self._is_db_setup = True
                await create_models(self.engine, self.DBBase)
            return await f(self, *args, **kwargs)

        return wrapper


def with_session(f):
    @wraps(f)
    async def wrapper(self: BaseAsyncRepoTest, *args, **kwargs):
        async with self.session_maker() as session:  # type: ignore
            async with session.begin():
                self.session = session
                return await f(self, *args, **kwargs)

    return wrapper


def with_repo(f):
    @wraps(f)
    @with_session
    async def wrapper(self: BaseAsyncRepoTest, *args, **kwargs):
        if self.TRepo is None:
            raise NotImplementedError('TRepo is None')
        self.repo = self.TRepo(session=self.session)
        return await f(self, *args, **kwargs)

    return wrapper

