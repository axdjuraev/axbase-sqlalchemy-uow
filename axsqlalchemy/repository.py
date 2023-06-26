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
    DBModel: TDBModel = BaseTableAt
    IModel = BaseModel
    OModel = BaseModel

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: Union["IModel", "OModel"]) -> OModel:
        if not self.DBModel:
            raise NotImplementedError

        if type(obj) is self.OModel:
            obj = self.IModel.from_orm(obj)

        obj = self.DBModel(**obj.dict())
        self.session.add(obj)
        await self.session.commit()

        return self.OModel.from_orm(obj)

    def __get_filters(
        self,
        ids: Union[tuple[Any], List[Any], None, "IModel", "OModel"],
        columns: Union[List[Any], tuple[Any], None] = None,
    ) -> tuple[Any]:
        if ids is None:
            return (True,)

        if columns is None:
            if self.DBModel.ids is None:
                return (True,)
            columns = self.DBModel.ids

        if type(ids) not in [tuple, list]:
            ids = self.__get_obj_ids(self.IModel.from_orm(ids), columns)

        filters = []

        if self.DBModel is None:
            raise NotImplementedError

        if columns is not None:
            for colum, value in zip(columns, ids):
                filters.append(colum == value)

        return tuple(filters)

    def __get_obj_ids(self, obj: "IModel", columns) -> tuple[Any]:
        ids = []

        if not columns:
            return tuple(ids)

        for column in columns:
            ids.append(getattr(obj, column.name))

        return tuple(ids)


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

    async def update(self, obj: Union["IModel", "OModel"]) -> "IModel":
        if type(obj) is self.OModel:
            obj = self.IModel.from_orm(obj)

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
        return self.IModel.from_orm(obj)

    async def delete(self, obj: "IModel") -> None:
        filters = self.__get_filters(obj)
        await self.session.execute(delete(self.DBModel).where(*filters))

    async def all(self, ids: Union[tuple[Any], None] = None) -> Union[List[Any], None]:
        filters = self.__get_filters(ids, columns=self.DBModel.ids_all)
        objs = await self.session.execute(select(self.DBModel).where(*filters))

        if objs:
            return [self.OModel.from_orm(obj) for obj in objs]
