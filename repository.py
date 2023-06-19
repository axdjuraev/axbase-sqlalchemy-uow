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

    def __get_filters(
        self,
        ids: Union[tuple[Any], List[Any], None, IModel, OModel],
        columns: Union[List[Any], tuple[Any], None] = DBModel.ids,
    ) -> tuple[Any]:
        if ids is None or columns is None:
            return (True,)

        if type(ids) not in [tuple, list]:
            ids = self.__get_obj_ids(self.IModel.from_orm(ids), columns)

        filters = []

        if self.DBModel is None:
            raise NotImplementedError

        for colum, value in zip(self.DBModel.ids, ids):
            filters.append(colum == value)

        return tuple(filters)

    def __get_obj_ids(self, obj: IModel, columns=DBModel.ids) -> tuple[Any]:
        ids = []
        fields: dict = obj.__class__.__fields__

        for column in columns:
            ids.append(fields.get(column.__name__))

        return tuple(ids)

    async def add(self, obj: Union[IModel, OModel]) -> IModel:
        if not self.DBModel:
            raise NotImplementedError

        if type(obj) is self.OModel:
            obj = self.IModel.from_orm(obj)

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
        filters = self.__get_filters(obj)
        (
            await self.session.execute(
                update(self.DBModel)
                .where(*filters)
                .values(
                    **obj.dict(),
                ),
            )
        )
        return obj

    async def delete(self, obj: IModel) -> None:
        filters = self.__get_filters(obj)
        await self.session.execute(delete(self.DBModel).where(*filters))

    async def all(self, ids: Union[tuple[Any], None] = None) -> Union[List[Any], None]:
        filters = self.__get_filters(ids, columns=self.DBModel.ids_all)
        objs = await self.session.execute(select(self.DBModel).where(*filters))

        if objs:
            return [self.OModel.from_orm(obj) for obj in objs]
