from sqlalchemy import delete
from typing import Generic, Iterable

from .types import TIModel, TOModel, TDBModel
from .base import BaseRepoCreator


class DeleterRepo(BaseRepoCreator[TDBModel, TIModel, TOModel], Generic[TDBModel, TIModel, TOModel]):
    async def delete(self, *ids, filters: Iterable = tuple()) -> None:
        filters = self._get_filters(ids, extra_filters=filters, use_defaults=False)
        await self.session.execute(delete(self.Model).where(*filters))

