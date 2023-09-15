import math
from typing import Generic, Iterable, List, Optional
from sqlalchemy import select
from pydantic import parse_obj_as

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class GetterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    ids4all: Iterable = tuple()

    async def all(
        self, 
        *ids, 
        filters: Iterable = tuple(), 
        count: Optional[int] = None,
        page: Optional[int] = None,
    ) -> list[TOModel]:
        filters = self._get_filters(ids, columns=self.ids4all, extra_filters=filters)
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

    async def all_page_count(self, *ids, 
        filters: Iterable = tuple(), 
        count: Optional[int] = None,
    ) -> int:
        all_count = await self.all_count(ids, filters)
        return math.ceil(all_count / count) if count else 1 

    async def all_count(self, *ids, filters: Iterable = tuple()) -> int:
        filters = self._get_filters(ids, columns=self.Model.ids_all, extra_filters=filters)
        query = ( 
            select(func.count(self.Model.created_at))
            .where(*filters)
        )
        return (await self.session.execute(query)).scalar() or 0

