from typing import Any, Generic, List, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from axabc.db import AbstractAsyncRepository
from .model import BaseTableAt


TDBModel = TypeVar("TDBModel", bound=BaseTableAt)
TIModel = TypeVar("TIModel", bound=BaseModel)
TOModel = TypeVar("TOModel", bound=BaseModel)


class BaseRepository(AbstractAsyncRepository, Generic[TDBModel, TIModel, TOModel]):
    Model: Type[TDBModel]
    Schema: Type[TIModel]
    OSchema: Type[TOModel]

    def __init_subclass__(cls) -> None:
        types = getattr(cls, "__orig_bases__")[0].__args__
        cls.Model, cls.Schema, cls.OSchema = types

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: TDBModel) -> TOModel:
        if not self.Model:
            raise NotImplementedError

        if type(obj) is self.OSchema:
            obj = self.Schema.from_orm(obj)

        obj = self.Model(**obj.dict())
        self.session.add(obj)
        await self.session.commit()

        return self.OSchema.from_orm(obj)

    def __get_filters(
        self,
        ids: Union[tuple[Any], List[Any], None, TIModel, TOModel],
        columns: Union[List[Any], tuple[Any], None] = None,
    ) -> tuple[Any]:
        if ids is None:
            return (True,)

        if columns is None:
            if self.Model.ids is None:
                return (True,)
            columns = self.Model.ids

        if type(ids) not in [tuple, list]:
            ids = self.__get_obj_ids(self.Schema.from_orm(ids), columns)

        filters = []

        if self.Model is None:
            raise NotImplementedError

        if columns is not None:
            for colum, value in zip(columns, ids):
                filters.append(colum == value)

        return tuple(filters)

    def __get_obj_ids(self, obj: TIModel, columns) -> tuple[Any]:
        ids = []

        if not columns:
            return tuple(ids)

        for column in columns:
            ids.append(getattr(obj, column.name))

        return tuple(ids)

    async def get(self, *ids: Any) -> Any:
        filters = self.__get_filters(ids)

        if self.Model.ids is None:
            raise NotImplementedError

        obj = (
            (
                await self.session.execute(
                    select(self.Model)
                    .where(and_(*filters))
                    .order_by(self.Model.created_at.desc()),
                )
            )
            .scalars()
            .first()
        )

        if obj:
            return self.OSchema.from_orm(obj)

    async def update(self, obj: Union[TIModel, TOModel]) -> TIModel:
        if type(obj) is self.OSchema:
            obj = self.Schema.from_orm(obj)

        filters = self.__get_filters(obj)
        (
            await self.session.execute(
                update(self.Model)
                .where(*filters)
                .values(
                    **obj.dict(),
                ),
            )
        )
        return self.Schema.from_orm(obj)

    async def delete(self, obj: TIModel) -> None:
        filters = self.__get_filters(obj)
        await self.session.execute(delete(self.Model).where(*filters))

    async def all(self, ids: Union[tuple[Any], None] = None) -> Union[List[Any], None]:
        filters = self.__get_filters(ids, columns=self.Model.ids_all)
        objs = await self.session.execute(select(self.Model).where(*filters))

        if objs:
            return [self.OSchema.from_orm(obj) for obj in objs]
