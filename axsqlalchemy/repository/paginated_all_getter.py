import math
from typing import Generic, Iterable, List, Optional
from sqlalchemy import func, select
from pydantic import parse_obj_as

from .types import TIModel, TOModel, TDBModel
from .all_getter import AllGetterRepo


class PaginatedAllGetterRepo(AllGetterRepo[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def all(self, *ids, filters: Iterable = tuple(), count: Optional[int] = None, page: Optional[int] = None) -> list[TOModel]:
        filters = self._get_filters(ids, columns=self.ids4all, extra_filters=filters)
        objs = (
            await self.session.execute(
                self.paginate_query( 
                    (
                        select(self.Model)
                        .where(*filters)
                        .order_by(self.Model.created_at.desc()) 
                    ),
                    count=count,
                    page=page,
                )
            )
        ).unique().scalars().all()

        return parse_obj_as(List[self.OSchema], objs)

    async def all_page_count(self, *ids, filters: Iterable = tuple(), count: Optional[int] = None) -> int:
        all_count = await self.all_count(ids, filters)
        return math.ceil(all_count / count) if count else 1 

    async def all_count(self, *ids, filters: Iterable = tuple()) -> int:
        filters = self._get_filters(ids, columns=self.ids4all, extra_filters=filters)

        obj = ( 
            await self.session.execute(
                select(func.count(self.Model.created_at))
                .where(*filters)
            )
        ).scalar()

        return obj or 0

    def paginate_query(self, query, count: Optional[int] = None, page: Optional[int] = None):
        if count and page:
            return query.offset((page - 1) * count).limit(count)

        return query

