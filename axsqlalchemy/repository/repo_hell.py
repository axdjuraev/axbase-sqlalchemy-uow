
import math
from typing import Any, Generic, List, Type, Union
from pydantic import parse_obj_as
from sqlalchemy import and_, delete, select, update, func
from axabc.db import AbstractAsyncRepository

from .types import TDBModel, TIModel, TOModel


class BaseRepository(AbstractAsyncRepository):

    def __init_subclass__(cls) -> None:
        types = getattr(cls, "__orig_bases__")[0].__args__
        cls.Model, cls.Schema, cls.OSchema = types

    def paginate_query(self, query, count: Union[int, None], page: Union[int, None]):
        if count and page:
            return query.offset((page - 1) * count).limit(count)
        return query

    async def add(self, obj: TIModel, autocommit=True) -> TOModel:
        if not self.Model:
            raise NotImplementedError

        if type(obj) in (self.OSchema, self.Schema):
            obj = self.Schema.from_orm(obj)

        obj = self.Model(**obj.dict())  # type: ignore
        self.session.add(obj)
        
        if autocommit:
            await self.session.commit()

        return self.OSchema.from_orm(obj)

    async def update_status(self, *ids, status: bool, filters: Union[tuple, None] = None) -> None:
        filters = self.__get_filters(ids, use_defaults=False, extra_filters=filters)
        
        if self.Model.ids is None:
            raise NotImplementedError
        
        await self.session.execute(
           update(self.Model)
           .where(and_(*filters))
           .values(is_active=status)
        )

    async def deactivate(self, *ids, filters: Union[tuple, None] = None) -> None:
        return await self.update_status(*ids, status=False, filters=filters)

    async def update(self, obj: Union[TIModel, TOModel], filters: Union[tuple, None] = None) -> TIModel:
        if type(obj) in (self.OSchema, self.Schema):
            obj = self.Schema.from_orm(obj)

        filters = self.__get_filters(obj, extra_filters=filters, use_defaults=False)
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

    async def delete(self, *ids, filters: Union[tuple, None] = None) -> None:
        filters = self.__get_filters(ids, extra_filters=filters, use_defaults=False)
        await self.session.execute(delete(self.Model).where(*filters))

    async def all(
        self, 
        ids: Union[tuple[Any], None] = None, 
        filters: Union[tuple, None] = None, 
        count: Union[int, None] = None,
        page: Union[int, None] = None,
    ) -> List[TOModel]:
        filters = self.__get_filters(ids, columns=self.Model.ids_all, extra_filters=filters)
        query = self.paginate_query( 
            (
                select(self.Model)
                .where(*filters)
                .order_by(self.Model.created_at.desc()) 
            ),
            count=count,
            page=page,
        )
        objs = (await self.session.execute(query)).unique().scalars().all()
        return parse_obj_as(List[self.OSchema], objs)

    async def all_page_count(
        self, 
        ids: Union[tuple[Any], None] = None, 
        filters: Union[tuple, None] = None, 
        count: Union[int, None] = None,
    ) -> int:
        all_count = await self.all_count(ids, filters)
        return math.ceil(all_count / count) if count else 1 

    async def all_count(
        self, 
        ids: Union[tuple[Any], None] = None, 
        filters: Union[tuple, None] = None, 
    ) -> int:
        filters = self.__get_filters(ids, columns=self.Model.ids_all, extra_filters=filters)
        query = ( 
            select(func.count(self.Model.created_at))
            .where(*filters)
        )
        return (await self.session.execute(query)).scalar()

