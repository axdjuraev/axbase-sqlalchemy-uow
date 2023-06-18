from typing import Any, List, Union

from pydantic import BaseModel
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from axabc.db import AbstractAsyncRepository

from .model import AbstractBaseModel, BaseTableAt


class BaseRepository(AbstractAsyncRepository):
    DBModel: AbstractBaseModel = BaseTableAt()
    IModel = BaseModel
    OModel = BaseModel

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def __get_filters(self, ids: Union[tuple[Any], None]) -> tuple[Any]:
        if ids is None:
            return (True,)

        filters = []

        if self.DBModel is None:
            raise NotImplementedError

        for colum, value in zip(self.DBModel.ids, ids):
            filters.append(colum == value)

        return tuple(filters)

    async def add(self, obj: IModel) -> IModel:
        if not self.DBModel:
            raise NotImplementedError

        obj = self.DBModel(**obj.dict())
        self.session.add(obj)
        await self.session.commit()

        return self.IModel.from_orm(obj)

    async def get(self, *ids: Any) -> Any:
        filters = self.__get_filters(ids)

        if self.DBModel.ids is None:
            raise NotImplementedError

        obj = (
            (
                await self.session.execute(
                    select(self.DBModel)
                    .where(and_(*filters))
                    .order_by(self.DBModel.created_at),
                )
            )
            .scalars()
            .first()
        )

        if obj:
            return self.OModel.from_orm(obj)

    async def update(self, obj: IModel) -> IModel:
        (
            await self.session.execute(
                update(self.DBModel)
                .where(self.DBModel.id == obj.id)
                .values(**obj.dict()),
            )
        )
        return obj

    async def delete(self, obj: IModel) -> None:
        await self.session.execute(
            delete(self.DBModel).where(self.DBModel.id == obj.id)
        )

    async def all(self, ids: Union[tuple[Any], None] = None) -> Union[List[Any], None]:
        filters = self.__get_filters(ids)
        objs = await self.session.execute(select(self.DBModel).where(*filters))

        if objs:
            return [self.OModel.from_orm(obj) for obj in objs]
