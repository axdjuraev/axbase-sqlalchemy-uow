from typing import Any, Type, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from axabc.db import (
    AbstractAsyncRepository,
    AbstractUOW,
    AbstractUOWFactory,
    BaseRepoCollector,
)


class BaseUOW(AbstractUOW):
    def __init__(self, repo: Type[BaseRepoCollector], session: AsyncSession) -> None:
        self.repo = repo(_uow=self)
        self.session = session

    async def __aenter__(self):
        await self.session.begin()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.close()

    async def save(self):
        await self.session.commit()

    async def dispose(self):
        await self.session.close()

    async def rollback(self):
        await self.session.rollback()

    def get_repo(self, cls: Type[AbstractAsyncRepository]) -> AbstractAsyncRepository:
        return cls(self.session)


class BaseUOWFactory(AbstractUOWFactory):
    def __init__(
        self,
        session_maker: sessionmaker,
        repo: Type[BaseRepoCollector],
        session: Union[AsyncSession, None] = None,
    ) -> None:
        self.session_maker = session_maker
        self.repo = repo

    async def __aenter__(self) -> Any:
        session = self.session_maker()
        return await BaseUOW(self.repo, session).__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # * This should rollback uow session but I have no idea how to do that from uowfactory
        pass
