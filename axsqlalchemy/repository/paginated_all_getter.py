from typing import Generic, Iterable, List, Optional
from sqlalchemy import select
from pydantic import parse_obj_as

from .types import TIModel, TOModel, TDBModel
from .paginated import PaginatedRepo


class PaginatedAllGetterRepo(PaginatedRepo[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    @property
    def _base_all_paginated_query(self): 
        return self._base_all_query

    async def all(self, *ids, filters: Iterable = tuple(), count: Optional[int] = None, page: Optional[int] = None, query = None) -> list[TOModel]:
        query = query if query is not None else self._base_all_query
        return await super().all(
            *ids, 
            filters=filters,
            query=(
                self.paginate_query( 
                    query,
                    count=count,
                    page=page,
                )
            ),
        )

