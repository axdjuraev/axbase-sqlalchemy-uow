import math
from typing import Generic, Iterable, Optional
from sqlalchemy import func, select

from .types import TIModel, TOModel, TDBModel
from .all_getter import AllGetterRepo


class PaginatedRepo(AllGetterRepo[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def all_page_count(self, *ids, filters: Iterable = tuple(), count: Optional[int] = None) -> int:
        all_count = await self.all_count(*ids, filters)
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

