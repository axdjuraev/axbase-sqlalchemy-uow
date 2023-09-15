from sqlalchemy import select, and_
from typing import Generic, Iterable, Optional

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class GetterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def get(self, *ids, filters: Iterable = tuple()) -> Optional[TOModel]:
        filters = self._get_filters(ids, extra_filters=filters, use_defaults=False)

        obj = (
            (
                await self.session.execute(
                    select(self.Model)
                    .where(and_(*filters))
                    .order_by(self.Model.created_at.desc()),
                )
            )
            .scalars()
            .first()
        )

        return obj and self.OSchema.from_orm(obj)

