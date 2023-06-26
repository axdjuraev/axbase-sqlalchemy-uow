from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from axabc.db import (AbstractAsyncRepository, AbstractUOW, AbstractUOWFactory,
                      BaseRepoCollector)

TRepoCollector = TypeVar("TRepoCollector", bound=BaseRepoCollector)


class UOW(AbstractUOW, Generic[TRepoCollector]):
    def __init__(self, repo: Type[TRepoCollector], session: AsyncSession) -> None:
        self.repo: TRepoCollector = repo(_uow=self)
        self.session = session
        self.is_session_closed: bool = False

    async def __aenter__(self):
        await self.session.begin()
        return self

    async def __aexit__(self, *args, **kwargs):
        if any(args) or kwargs:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.dispose()

    async def save(self):
        await self.session.commit()

    async def dispose(self):
        await self.session.close()
        self.is_session_closed = True

    async def rollback(self):
        await self.session.rollback()

    def get_repo(self, cls: Type[AbstractAsyncRepository]) -> AbstractAsyncRepository:
        if self.is_session_closed:
            raise ValueError("use uow in context manager")

        return cls(self.session)


class UOWFactory(AbstractUOWFactory, Generic[TRepoCollector]):
    def __init__(
        self,
        repo: Type[TRepoCollector],
        session_maker: sessionmaker,
    ) -> None:
        self.repo = repo
        self.session_maker = session_maker

    def __call__(self) -> UOW[TRepoCollector]:
        session = self.session_maker()
        return UOW(self.repo, session)
