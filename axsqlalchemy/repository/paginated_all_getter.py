from typing import Generic, Iterable, List, Optional
from sqlalchemy import select
from pydantic import parse_obj_as

from .types import TIModel, TOModel, TDBModel
from .paginated import PaginatedRepo


class PaginatedAllGetterRepo(PaginatedRepo[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
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

