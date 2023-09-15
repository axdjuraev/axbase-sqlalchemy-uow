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

    async def delete(self, *ids, filters: Union[tuple, None] = None) -> None:
        filters = self.__get_filters(ids, extra_filters=filters, use_defaults=False)
        await self.session.execute(delete(self.Model).where(*filters))


