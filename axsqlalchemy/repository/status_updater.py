from sqlalchemy import update, and_
from typing import Generic, Iterable

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class StatusUpdaterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def deactivate(self, *ids, filters: Iterable = tuple()) -> None:
        return await self.update_status(*ids, status=False, filters=filters)

    async def update_status(self, *ids, status: bool, filters: Iterable = tuple()) -> None:
        filters = self._get_filters(ids, use_defaults=False, extra_filters=filters)
        
        await self.session.execute(
           update(self.Model)
           .where(and_(*filters))
           .values(is_active=status)
        )

