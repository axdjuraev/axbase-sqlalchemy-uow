from abc import ABC
from typing import Type, TypeVar

from sqlalchemy.orm import sessionmaker

from axabc.db import AbstractAsyncUOW, BaseRepoCollector


class BaseSQLAlchemyUOW(AbstractAsyncUOW):
    def __init__(
        self,
        session_maker: sessionmaker,
        repo: Type[BaseRepoCollector],
    ) -> None:
        self.session_maker = session_maker
        self.repo = repo(_uow=self)
