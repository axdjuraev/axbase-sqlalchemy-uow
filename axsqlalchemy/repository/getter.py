from sqlalchemy import select, and_
from typing import Generic, Iterable, Optional

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class GetterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    @property
    def _base_get_query(self):
        return select(self.Model)

    async def get(self, *ids, filters: Iterable = tuple(), query = None) -> Optional[TOModel]:
        query = query if query is not None else self._base_get_query
        filters = self._get_filters(ids, extra_filters=filters, use_defaults=False)

        obj = (
            (
                await self.session.execute(
                    query
                    .where(and_(*filters))
                    .order_by(self.Model.created_at.desc()),
                )
            )
            .scalars()
            .first()
        )

        return obj and self.OSchema.from_orm(obj)

