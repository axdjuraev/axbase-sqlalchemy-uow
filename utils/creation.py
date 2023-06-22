from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import decl_base


async def create_models(engine: AsyncEngine, base: decl_base):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


async def drop_models(engine: AsyncEngine, base: decl_base):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)


async def recreate_models(engine: AsyncEngine, base: decl_base):
    await drop_models(engine, base)
    await create_models(engine, base)
