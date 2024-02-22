from typing import TYPE_CHECKING, TypeVar
from axabc.db.repo_collector import BaseRepoCollector
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import decl_base


if TYPE_CHECKING:
    from axsqlalchemy.settings import Settings as DBSettings
    from axabc.db import AsyncUOWFactory
    

TRepoCollection = TypeVar("TRepoCollection", bound=BaseRepoCollector)


def get_uowf(settings: "DBSettings", TypeRepoCollection: type[TRepoCollection]) -> "AsyncUOWFactory[TRepoCollection]":
    engine = create_async_engine(settings.db_connection_string)
    session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
    session_maker.engine = engine  # type: ignore
    return AsyncUOWFactory(TypeRepoCollection, session_maker)


async def create_models(engine: AsyncEngine, base: decl_base):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


async def drop_models(engine: AsyncEngine, base: decl_base):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)


async def recreate_models(engine: AsyncEngine, base: decl_base):
    await drop_models(engine, base)
    await create_models(engine, base)
