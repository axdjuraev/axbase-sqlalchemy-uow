from typing import Generic, Iterable, List, Type
from sqlalchemy import select
from pydantic import BaseModel, parse_obj_as

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class AllGetterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    ids4all: Iterable = tuple()

    @property
    def _base_all_query(self): 
        return select(self.Model)

    @property
    def _all_schema(self) -> Type[BaseModel]:
        return self.OSchema

    async def all(self, *ids, filters: Iterable = tuple(), query = None) -> list[TOModel]:
        query = query if query is not None else self._base_all_query
        filters = self._get_filters(ids, columns=self.ids4all, extra_filters=filters)

        objs = (
            await self.session.execute(
                query
                .where(*filters)
                .order_by(self.Model.created_at.desc()) 
            )
        ).unique().scalars().all()

        return parse_obj_as(List[self._all_schema], objs)  # type: ignore

